---
title: "Design Doc: Posting to My Hugo Blog Directly from iPhone"
date: 2026-05-03
draft: false
tags: ["blog", "design", "hugo", "tailscale", "automation"]
---

# Design Doc: Posting to My Hugo Blog Directly from iPhone

## 1. Problem

I wanted a low-friction way to publish to my blog from my iPhone.

The original blog setup was simple:

- content lives in Markdown inside a Hugo repo
- GitHub Actions builds and deploys the site
- GitHub Pages serves the final static output

That setup is good for reliability, but not good for writing on mobile. Editing Markdown through GitHub’s mobile UI technically works, but it is still a repo workflow, not a writing workflow.

The requirement was:

- open phone
- write a post
- publish

Without needing to manually browse files, edit Markdown in GitHub, or use the GitHub API.

## 2. Goals

- Publish a new post from iPhone with minimal friction
- Keep the existing Hugo + GitHub Actions deployment pipeline
- Avoid GitHub API integrations
- Keep content stored as normal Markdown files in the repo
- Use a simple, understandable architecture

## 3. Non-Goals

- Full CMS with rich media management
- Multi-user editing workflow
- In-browser editing of existing posts
- Database-backed content storage
- Real-time collaboration

## 4. Existing Stack

The baseline blog stack was:

- **Hugo** for static site generation
- **PaperMod** as the theme
- **GitHub repository** for source control
- **GitHub Actions** for build and deploy
- **GitHub Pages** for static hosting behind `yutongjin.com`

The deployment flow already existed:

1. Push to `main`
2. GitHub Actions runs `hugo --minify`
3. Built output is deployed to `yutongjin/yutongjin.github.io`
4. Custom domain serves the updated site

## 5. High-Level Design

The final design keeps the static site static, and adds a very small private publishing service.

There are two separate pieces:

### 5.1 Public static admin page

The Hugo site now serves `/admin/`.

This is only a form UI. It collects:

- publish endpoint
- username
- password
- title
- slug
- tags
- date
- draft flag
- body

It does **not** write files directly.

### 5.2 Private publish server

A small Python server runs on my Mac:

- `scripts/publish_server.py`

Its job is:

1. accept authenticated `POST /publish`
2. validate the payload
3. create `content/posts/<slug>.md`
4. run `git add`
5. run `git commit`
6. run `git push origin main`

This avoids the GitHub API entirely. It uses normal git operations against the repo checkout.

## 6. Tech Stack Used

The implementation used:

- **Hugo** for the blog site
- **PaperMod** for rendering
- **HTML/CSS/JavaScript** for the `/admin/` page
- **Python standard library HTTP server** for the publish backend
- **Basic Auth** for lightweight authentication
- **git CLI** for commit and push
- **Tailscale Funnel** to expose the local publisher over public HTTPS
- **GitHub Actions** for the existing deployment pipeline
- **GitHub Pages** for serving the final site

## 7. Data Flow

The end-to-end data flow is:

1. On iPhone, open `https://yutongjin.com/admin/`
2. Hugo/GitHub Pages serves the static admin page
3. User fills in post data and taps `Publish`
4. Browser sends `OPTIONS /publish` to check CORS
5. Browser sends authenticated `POST /publish` to the publish endpoint
6. Tailscale Funnel receives the public HTTPS request
7. Funnel forwards it to `http://127.0.0.1:8787` on the Mac
8. `publish_server.py` validates auth and request payload
9. Server writes a new Markdown file under `content/posts/`
10. Server runs `git add`, `git commit`, and `git push`
11. GitHub receives the push to `main`
12. GitHub Actions workflow is triggered by the push event
13. Workflow runs `hugo --minify`
14. Built site is deployed to the GitHub Pages repo
15. `yutongjin.com` serves the updated post and post index

## 8. Event Triggering

There are several explicit trigger points in the system:

### 8.1 Browser submit event

The user taps `Publish` on `/admin/`.

That triggers:

- JavaScript form submission
- JSON payload creation
- authenticated `fetch()` call to `/publish`

### 8.2 CORS preflight

Because the admin page and publisher are on different origins, Safari issues:

- `OPTIONS /publish`

The server responds with:

- `204 No Content`
- CORS headers allowing the request

Only after that does the browser send the real publish request.

### 8.3 Publish request

The real publish event is:

- `POST /publish`

If authentication succeeds and the payload is valid, the post is created.

### 8.4 Git push event

After the server pushes to `main`, GitHub Actions is triggered by repository state change:

- `on: push`
- `branches: ["main"]`

### 8.5 Deploy event

The existing GitHub Actions workflow builds and publishes the static site.

That is what makes the new post visible at:

- `/posts/<slug>/`
- `/posts/`

## 9. Request and Auth Model

The publisher uses HTTP Basic Auth.

Required environment variables:

```bash
export BLOG_ADMIN_USER="<admin-username>"
export BLOG_ADMIN_PASSWORD="<strong-password>"
export BLOG_ALLOWED_ORIGIN="https://yutongjin.com"
```

The admin page sends:

- `Authorization: Basic ...`
- JSON request body with post fields

The publisher verifies:

- username matches `BLOG_ADMIN_USER`
- password matches `BLOG_ADMIN_PASSWORD`

This is intentionally lightweight. It is enough for a private personal workflow, but it is not a full IAM system.

## 10. Write Path

When a publish request succeeds, the server renders the post into standard front matter:

```yaml
---
title: "Post title"
date: 2026-05-03
draft: false
tags: ["tag1", "tag2"]
---
```

Then it appends the Markdown body and writes the file into:

- `content/posts/<slug>.md`

This keeps the source of truth exactly where Hugo already expects it.

## 11. Operational Setup

Two processes must be running on the Mac:

### 11.1 Publisher server

```bash
python3 scripts/publish_server.py --host 0.0.0.0 --port 8787 --repo .
```

### 11.2 Public HTTPS tunnel

```bash
tailscale funnel 8787
```

That produced a public endpoint similar to:

```text
https://<device-name>.<tailnet>.ts.net
```

That endpoint was then configured as the default publish endpoint on `/admin/`.

## 12. What Worked

- The form submitted successfully from iPhone
- The publish server created a new Markdown file
- The server committed and pushed the change
- GitHub Actions deployed the updated site
- The new post appeared both on its direct URL and on the posts index

This confirmed that the system works end to end.

## 13. Failure Modes Observed

Several errors showed up during setup, each tied to a specific layer:

### 13.1 `Failed to fetch`

Cause:

- no reachable publish endpoint yet

Meaning:

- browser could not connect to any publisher

### 13.2 `405`

Cause:

- wrong request path or direct browser access to `/publish`

Meaning:

- the endpoint was reachable, but the method/path usage was wrong

### 13.3 `404`

Cause:

- using the blog domain instead of the publisher domain

Meaning:

- request reached the static site, not the publish server

### 13.4 `Unauthorized`

Cause:

- wrong username/password

Meaning:

- network path worked, auth failed

### 13.5 `Address already in use`

Cause:

- publisher already running on port `8787`

Meaning:

- a second server instance was started accidentally

These were useful because each error corresponded to a different system boundary:

- browser/network
- routing
- auth
- local process lifecycle

## 14. Improvements Already Made

To reduce friction, the admin page was updated to default:

- `Publish endpoint`
- `Username`

The date is also auto-filled to today in the browser.

This means the normal mobile workflow is now:

1. open `/admin/`
2. type password
3. enter post content
4. publish

## 15. Tradeoffs

### 15.1 Pros

- very small system
- no GitHub API dependency
- content remains plain Markdown
- reuses the existing deploy pipeline
- easy to debug because each step is explicit

### 15.2 Cons

- Mac must be online
- publisher process must be running
- Tailscale Funnel must be running
- endpoint is tied to operational state, not permanent infrastructure
- auth is minimal
- only supports creating new posts, not editing old ones

## 16. Possible Improvements

The current version works, but it is still an MVP. Obvious next steps:

### 16.1 Reliability

- run the publisher with `launchd` so it auto-starts
- auto-start Tailscale and keep Funnel available
- move the publisher to a small VPS for always-on availability

### 16.2 UX

- hide the publish endpoint field entirely
- prefill more metadata defaults
- show the published post URL after success
- support editing existing posts from `/admin/`
- add a lightweight post list in the admin page

### 16.3 Security

- replace Basic Auth with a stronger auth flow
- rate-limit publish requests
- restrict publishing to a narrower device or identity boundary
- rotate credentials regularly

### 16.4 Content model

- support descriptions and cover images
- support scheduled publishing
- support timestamped front matter instead of date-only

## 17. Why This Design Was Good Enough

This design is not a full CMS, and it does not try to be.

It solves the real problem:

- writing and publishing from iPhone with low friction

while preserving the existing strengths of the blog:

- Git-based history
- Markdown source of truth
- Hugo build
- GitHub Actions deploy

In other words, instead of replacing the publishing stack, it adds the thinnest possible write layer in front of it.

## 18. Final Architecture Summary

The final system looks like this:

```text
iPhone Safari
  -> yutongjin.com/admin/ (static Hugo page on GitHub Pages)
  -> HTTPS POST to Tailscale Funnel endpoint
  -> local Python publish server on Mac
  -> write Markdown into content/posts/
  -> git add / commit / push
  -> GitHub Actions build and deploy
  -> updated yutongjin.com
```

That is the whole idea:

- static site for reading
- tiny private service for writing
- git for versioned content
- existing CI/CD for deployment

Small system, clear boundaries, good enough to use.
