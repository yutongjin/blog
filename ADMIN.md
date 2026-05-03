# Private Mobile Admin

This adds a simple `/admin/` page for creating new posts from your iPhone and a small publish server that writes Markdown into the repo and pushes normally with `git`.

## What it does

- `content/admin.md` exposes `/admin/`
- `layouts/admin/single.html` renders a phone-friendly post form
- `scripts/publish_server.py` accepts authenticated `POST /publish` requests, creates `content/posts/<slug>.md`, commits, and pushes `main`

## Why this architecture

GitHub Pages is static hosting. It can serve the form, but it cannot accept writes itself.

So the form needs a private endpoint somewhere you control:

- your Mac
- a VPS
- a small private server

That endpoint does not use the GitHub API. It only performs a normal `git push`.

## Required environment

On the machine running `scripts/publish_server.py`:

```bash
export BLOG_ADMIN_USER="your-username"
export BLOG_ADMIN_PASSWORD="a-strong-password"
export BLOG_ALLOWED_ORIGIN="https://yutongjin.com"
```

The repo must be checked out there, with `git push origin main` already working.

## Run locally

```bash
python3 scripts/publish_server.py --host 0.0.0.0 --port 8787 --repo .
```

Health check:

```bash
curl http://127.0.0.1:8787/health
```

## iPhone flow

1. Open `https://yutongjin.com/admin/`
2. Enter your private publish endpoint URL
3. Enter username and password
4. Write the post and tap `Publish`

## Notes

- Existing posts are not edited by this flow; this creates new posts only.
- If a slug already exists, the server returns an error instead of overwriting.
- The current site deploy stays the same: server pushes to `main`, GitHub Actions builds Hugo, then deploys the site.
