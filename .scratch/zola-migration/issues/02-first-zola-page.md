# 02: First Zola page, end to end

**What to build:** A minimal Zola site that renders one Polish post Render-equivalent to the Baseline. This proves the whole setup before scaling up:
- Zola config: `pl` default, `en` language, `smart_punctuation` on, Sass compilation
- the SCSS partials and tokens compiling to the same CSS
- static files (fonts, images, JS, favicons, `pralka/`, `trackertutorial/`, downloads) served from the root
- the `default` and `post` templates with masthead, footer, breadcrumbs, ToC, SEO head, date formatting (Polish month names) and theme toggle
- UI strings and navigation as per-language data

Pick a simple post with headings, so the ToC and heading IDs get exercised (e.g. a `blog` post). Use Zola 0.23.6 via `ghcr.io/getzola/zola:v0.23.6`.

Previous/next links may render empty while only one post exists. Note this in the ticket rather than faking it.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] `zola build` succeeds with no Ruby involved
- [ ] The chosen post's URL is identical to the Baseline (explicit `path`) and passes the Parity check, apart from previous/next links, which are documented
- [ ] `/assets/css/main.css` passes the Parity check (CSS rule)
- [ ] All root static files pass the Parity check byte-identically
- [ ] Shared per-page values (path without language prefix, language-switch target, post category) live in one place in the templates
