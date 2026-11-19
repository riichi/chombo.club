# 08: Feeds, sitemaps, robots.txt and 404

**What to build:** The remaining generated files.
- `/feed.xml` and `/en/feed.xml` from custom Atom templates reproducing jekyll-feed: 10 entries, full content, `xml:lang`, the same entry IDs and links, and the `feed_meta` link in the head.
- `/sitemap.xml` and `/en/sitemap.xml` listing the same page URLs and `<lastmod>`s as the Baseline, without static files (known exception).
- `/robots.txt` at the root only, with the same rules (no `/en/robots.txt`, known exception).
- `/404.html` and `/en/404.html`.

**Blocked by:** 04

**Status:** done

- [x] Feeds pass the Parity check (normalised XML, `<updated>` ignored); entry `<id>`s are identical
- [x] Sitemaps pass the Parity check under the documented exception
- [x] `robots.txt` and both 404 pages pass the Parity check
