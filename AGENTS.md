# AGENTS.md

Static site for chombo.club, built with Zola 0.23 (Tera v2). See README.md for the content layout.

- Build: `zola build` (output in `public/`); dev server: `zola serve`. Full image: `docker build --target build .`.
- Templates are Tera v2: no shortcodes, macros or `import`. Use components from `templates/components.html`; they are hygienic, so pass every value explicitly.
- Every post and page sets an explicit `path`; English ones must include the `en/` prefix themselves.
- Translations (`*.en.md`) are self-contained: full front matter, nothing inherited from the Polish Original.
- Build-time checks (`throw` in `templates/post.html`) fail the build on: path not matching Warsaw date + category, Translation date/category/path differing from its Original, and a Polish post with no Translation and no `extra.lang-exclusive`. Fix the content, don't remove the check.
- `get_page(...)` defaults to the current language; pass `lang=config.default_language` to reach the Original.
- Zola always renders the taxonomy list page; the Dockerfile deletes `/categories/index.html` and `/en/categories/index.html` after the build. Keep that step.
- Pagefind runs after `zola build` (Dockerfile); `zola serve` has no search index.
- Domain terms: GLOSSARY.md. Decisions: docs/adr/.
