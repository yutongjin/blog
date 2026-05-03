+++
title = "Write"
date = 2026-05-02T00:00:00-07:00
draft = false
+++

Update the blog from your iPhone.

Preferred flow:

- Open [Admin](/admin/) to create a post in the private mobile editor.

Fallback flow:

- Use GitHub's mobile editor if the private publisher is unavailable.

Best flow:

1. Install the GitHub app on your iPhone and sign in.
2. Open one of the links below from Safari.
3. Make the edit, commit to `main`, and GitHub Actions will publish the site.

Quick links:

- [New post](https://github.com/yutongjin/blog/new/main?filename=content/posts%2Fmy-new-post.md&value=---%0Atitle%3A%20%22My%20New%20Post%22%0Adate%3A%202026-05-02%0Adraft%3A%20false%0Atags%3A%20%5B%5D%0A---%0A%0AWrite%20here.%0A)
- [Edit Now page](https://github.com/yutongjin/blog/edit/main/content/now.md)
- [Edit Projects page](https://github.com/yutongjin/blog/edit/main/content/projects.md)
- [All posts folder](https://github.com/yutongjin/blog/tree/main/content/posts)

Notes:

- New posts live in `content/posts/`.
- The front matter at the top controls the title, date, draft status, and tags.
- If you save a post with `draft: true`, Hugo will keep it out of the published site.
