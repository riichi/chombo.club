# 06: Home page, pagination and excerpts

**What to build:** The home page and its pagination in both languages: `/`, `/page/N/`, `/en/`, `/en/page/N/`.
- 10 posts per page, newest first
- the `home` template with header image and `srcset`, and the Discord link looked up by label
- post cards, with the excerpt taken from the rendered content before its first `</p>`, stripped and truncated to 40 words as today
- the paginator
- SEO: previous/next page links, and the `description` meta of posts now coming from the same excerpt rule (posts starting with a figure keep their empty description)

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] Every home and pagination URL in both languages passes the Parity check
- [ ] Post `description` meta tags match the Baseline across all posts (re-run the Parity check over the posts)
- [ ] A new post without any marker gets an excerpt automatically
