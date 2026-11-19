# 04: English posts and translation checks

**What to build:** Every Translation is moved to Zola and passes the Parity check at its existing `/en/…` URL.

- Each `.en.md` becomes self-contained: date, `path` (`en/…`), category, header and last-modified copied from its Original, plus the heading IDs from the Baseline.
- The English chrome works: language switcher (Original ↔ Translation), hreflang alternates, English UI strings and navigation, English month names.
- English pages reference root assets (`/assets/…`, `/favicon.svg`, …) instead of `/en/…`. This is a known exception in the Parity check.
- Build-time checks (Tera `throw`):
  - a Translation's date, category or path disagrees with its Original
  - an Original has no Translation and isn't Language-exclusive

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] All 24 English post URLs exist and pass the Parity check; how-to-buy has no English URL
- [ ] Language switcher and hreflang links on posts in both languages match the Baseline
- [ ] Breaking a Translation's date, category or path, or deleting a Translation of a non-exclusive post, fails `zola build` with a clear message (verified in a scratch copy)
- [ ] No `/en/` copies of static files are produced
