# 05: Pages (about, contact, calendar, help)

**What to build:** The four pages in both languages are moved to Zola and pass the Parity check at `/about/`, `/contact/`, `/calendar/`, `/help/` and their `/en/` counterparts.

- `page` template (ToC, breadcrumbs, SEO as on posts)
- `help_items(collection=…)` shortcode covering both the English and Polish variants (`name_pl`/`description_pl` fallbacks, Tenhou subitems), reading the help data files
- `footer_link(label=…)` shortcode replacing positional `site.footer.links[N]`, looked up by label
- the `{% raw %}` calendar embed and the leaflet/PDF links (`relative_url`) converted
- heading IDs copied from the Baseline; backslash line breaks in `about.*` checked

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] All 8 page URLs pass the Parity check
- [ ] No Liquid syntax remains in page content
- [ ] An unknown `footer_link` label fails the build
