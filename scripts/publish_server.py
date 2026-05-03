#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "post"


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


class PublishError(Exception):
    pass


class Publisher:
    def __init__(self, repo_root: Path, branch: str) -> None:
        self.repo_root = repo_root
        self.branch = branch
        self.posts_dir = repo_root / "content" / "posts"

    def publish(self, payload: dict) -> dict:
        title = str(payload.get("title", "")).strip()
        body = str(payload.get("body", "")).rstrip() + "\n"
        slug = slugify(str(payload.get("slug", "")).strip() or title)
        post_date = str(payload.get("date", "")).strip() or date.today().isoformat()
        draft = bool(payload.get("draft", False))
        tags = payload.get("tags", [])

        if not title:
            raise PublishError("Title is required.")
        if not body.strip():
            raise PublishError("Body is required.")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", post_date):
            raise PublishError("Date must use YYYY-MM-DD.")
        if not isinstance(tags, list):
            raise PublishError("Tags must be a list.")

        clean_tags = []
        for tag in tags:
            tag_value = str(tag).strip()
            if tag_value:
                clean_tags.append(tag_value)

        path = self.posts_dir / f"{slug}.md"
        if path.exists():
            raise PublishError(f"{path.relative_to(self.repo_root)} already exists.")

        content = self._render_post(title, post_date, draft, clean_tags, body)
        path.write_text(content, encoding="utf-8")
        committed = False

        try:
            self._git("add", str(path.relative_to(self.repo_root)))
            self._git("commit", "-m", f"Add post: {title}")
            committed = True
            commit = self._git("rev-parse", "HEAD").strip()
            self._git("push", "origin", self.branch)
        except subprocess.CalledProcessError as error:
            if not committed and path.exists():
                path.unlink()
            raise error

        return {
            "path": str(path.relative_to(self.repo_root)),
            "commit": commit,
        }

    def delete(self, payload: dict) -> dict:
        slug = str(payload.get("slug", "")).strip()
        if not slug:
            raise PublishError("Slug is required.")

        path = self.posts_dir / f"{slug}.md"
        if not path.exists():
            raise PublishError(f"{path.relative_to(self.repo_root)} does not exist.")

        try:
            self._git("rm", str(path.relative_to(self.repo_root)))
            self._git("commit", "-m", f"Delete post: {slug}")
            commit = self._git("rev-parse", "HEAD").strip()
            self._git("push", "origin", self.branch)
        except subprocess.CalledProcessError as error:
            raise error

        return {
            "path": str(path.relative_to(self.repo_root)),
            "commit": commit,
        }

    def _render_post(self, title: str, post_date: str, draft: bool, tags: list[str], body: str) -> str:
        tag_line = ", ".join(json.dumps(tag, ensure_ascii=False) for tag in tags)
        return (
            "---\n"
            f"title: {yaml_quote(title)}\n"
            f"date: {post_date}\n"
            f"draft: {'true' if draft else 'false'}\n"
            f"tags: [{tag_line}]\n"
            "---\n\n"
            f"{body}"
        )

    def _git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout


class PublishHandler(BaseHTTPRequestHandler):
    server_version = "BlogPublishServer/0.1"

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._write_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        if self.path != "/health":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        self._send_json(HTTPStatus.OK, {"status": "ok"})

    def do_POST(self) -> None:
        if self.path not in {"/publish", "/delete"}:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return

        if not self._authorized():
            self._send_json(HTTPStatus.UNAUTHORIZED, {"error": "Unauthorized"}, extra_headers={
                "WWW-Authenticate": 'Basic realm="blog-admin"'
            })
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON body"})
            return

        try:
            if self.path == "/publish":
                result = self.server.publisher.publish(payload)
            else:
                result = self.server.publisher.delete(payload)
        except PublishError as error:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
            return
        except subprocess.CalledProcessError as error:
            stderr = (error.stderr or "").strip()
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": stderr or "Git command failed"})
            return
        except Exception as error:
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)})
            return

        self._send_json(HTTPStatus.OK, result)

    def _authorized(self) -> bool:
        expected_user = os.environ.get("BLOG_ADMIN_USER")
        expected_password = os.environ.get("BLOG_ADMIN_PASSWORD")
        if not expected_user or not expected_password:
            return False

        header = self.headers.get("Authorization", "")
        if not header.startswith("Basic "):
            return False

        try:
            decoded = base64.b64decode(header.split(" ", 1)[1]).decode("utf-8")
            username, password = decoded.split(":", 1)
        except Exception:
            return False

        return username == expected_user and password == expected_password

    def _send_json(self, status: HTTPStatus, payload: dict, extra_headers: dict | None = None) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self._write_cors_headers()
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_cors_headers(self) -> None:
        origin = os.environ.get("BLOG_ALLOWED_ORIGIN", "*")
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")


class PublishServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], handler_class: type[BaseHTTPRequestHandler], publisher: Publisher):
        super().__init__(server_address, handler_class)
        self.publisher = publisher


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Private publisher for Hugo blog posts.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--branch", default="main")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo).resolve()
    publisher = Publisher(repo_root=repo_root, branch=args.branch)
    server = PublishServer((args.host, args.port), PublishHandler, publisher)
    print(f"Listening on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
