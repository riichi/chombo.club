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

**Status:** done

- [x] `zola build` succeeds with no Ruby involved
- [x] The chosen post's URL is identical to the Baseline (explicit `path`) and passes the Parity check, apart from previous/next links, which are documented
- [x] `/assets/css/main.css` passes the Parity check (CSS rule)
- [x] All root static files pass the Parity check byte-identically
- [x] Shared per-page values (path without language prefix, language-switch target, post category) live in one place in the templates

## Notes (done)

- Chosen post: `blog/2026/04/15/Mahjong-parlors-in-japan-a-blog-post/` (h2/h3 headings, figures).
- Previous/next links render empty: only one post exists, so `page.lower`/`page.higher` are unset. The only Parity check difference on that page is the missing `<nav class="post-nav">`; it will appear once the other posts are migrated.
- Zola 0.23 uses Tera v2: no macros or shortcodes. Shared helpers are components in `templates/components.html`, and content uses `{{ <figure alt="…" filename="…" /> }}`.
- Parity check: the CSS minifier now also normalises dart-sass vs grass serialiser differences (`@media (`, leading `0.`, `transparent`). New known exception: `no-css-source-map` (grass writes no `main.css.map`).
- `404.html`, `index.html`, `en/index.html` and `sitemap.xml` are still Zola defaults or placeholders; later tickets cover them.
