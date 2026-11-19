# 07: Category pages

**What to build:** The categories (`tournaments`, `blog`, `other`) as a per-language Zola taxonomy, rendered at `/categories/<name>/` and `/en/categories/<name>/`. Same as today:
- posts grouped by year
- localised category names and descriptions
- post counts with Polish plural forms (one/few/many)
- category tabs
- breadcrumbs and SEO

No pagination. Category links on posts and in navigation resolve to these URLs.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] All 6 category URLs pass the Parity check
- [ ] No extra taxonomy URLs are produced (e.g. a `/categories/` index), unless the Baseline has one
