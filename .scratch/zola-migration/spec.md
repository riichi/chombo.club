# Spec: migrate chombo.club from Jekyll to Zola

Status: ready-for-agent

See `GLOSSARY.md` (Baseline, Render-equivalent, Parity check, Original, Translation, Language-exclusive post) and `docs/adr/0001-zola-replaces-jekyll.md`.

## Problem Statement

The site's build depends on Ruby and Jekyll plus five plugins (jekyll-polyglot, jekyll-archives, jekyll-paginate, jekyll-feed, jekyll-sitemap) and a custom Ruby plugin for translations. Maintainers want a build with no Ruby at all, without visitors, search engines, feed readers or inbound links noticing any change.

## Solution

Rebuild the site on Zola (one pinned binary, Tera templates, pulldown-cmark). Acceptance is a Parity check: the Zola output is compared file by file against the Jekyll Baseline built from commit `ae8d366`, and must be Render-equivalent everywhere except for a short, written list of known exceptions. Before merging, rebase onto the latest `master`, rebuild the Baseline and run the Parity check again.

## User Stories

1. As a visitor, I want every page to look the same as before, so that the migration is invisible to me.
2. As a visitor with a bookmarked post, I want every existing post, page, category, pagination and feed URL to keep working, so that my links don't break.
3. As a visitor following a `#section` link, I want heading anchors on existing content to stay the same, so that deep links and the table of contents still work.
4. As an English-speaking visitor, I want the `/en/` site to keep the same pages, navigation, language switcher and translations, so that I can read the site in English.
5. As a visitor, I want typographic quotes, apostrophes and ellipses to look the same as before, so that the text reads naturally.
6. As a visitor, I want lists, tables, figures, iframes and code blocks to keep their spacing and styling, so that tournament posts stay readable.
7. As a visitor, I want the home page and the `/page/N/` pagination to show the same posts in the same order with the same excerpts, so that browsing works as before.
8. As a visitor, I want category pages (`/categories/<name>/`) to list posts grouped by year with the same counts and Polish plural forms, so that archives work as before.
9. As a visitor reading a post, I want the previous/next links, breadcrumbs, dates in Polish or English month names, and the auto table of contents to work as before.
10. As a visitor, I want site search to keep working, so that I can find posts.
11. As a visitor, I want the light/dark theme toggle and self-hosted fonts to work as before.
12. As a feed subscriber, I want `/feed.xml` and `/en/feed.xml` to keep the same entry IDs and links, so that my feed reader doesn't show old posts as new.
13. As a search engine, I want the sitemaps, canonical URLs, hreflang alternates, Open Graph tags and JSON-LD to carry the same information, so that indexing isn't disrupted.
14. As a crawler, I want `/robots.txt` to keep the same rules.
15. As a visitor, I want `/pralka/`, `/trackertutorial/`, the PDFs and the favicons to stay at their root URLs.
16. As a visitor hitting a missing URL, I want the same 404 page.
17. As an author, I want to write a new post in Markdown with plain `"` quotes and get typographic quotes automatically, as today.
18. As an author, I want to embed a figure, the help lists and footer links with short shortcodes, so that I don't repeat markup.
19. As an author, I want the build to fail if a Translation's date, category or path disagrees with its Original, so that mistakes don't reach the site.
20. As an author, I want the build to fail if a post has no Translation and isn't marked Language-exclusive, so that I don't forget translations.
21. As an author, I want the build to fail if a post's `path` doesn't match its date and category, so that new URLs follow the same scheme.
22. As an author, I want the post excerpt taken from the first paragraph automatically, so that I don't need a `<!-- more -->` marker.
23. As an author, I want stray files in the repository root (notes, agent files) never to be published.
24. As a maintainer, I want to run the site locally with `zola serve` or `docker-compose up`, as described in the README and `AGENTS.md`.
25. As a maintainer, I want the production image and the Cloudflare PR previews to build without Ruby, with previews still overriding the base URL.
26. As a maintainer, I want Dependabot to keep the Zola version up to date and to stop tracking Ruby gems.
27. As a reviewer, I want the PR to include the Parity check report, so that I can verify equivalence without diffing by hand.

## Implementation Decisions

### Parity check (the single test seam)
- A standalone Python script (standard library plus `lxml`), committed on the migration branch for the duration of the migration and deleted in the last ticket. It takes a Baseline directory and a Zola output directory and reports per-file results plus a summary.
- The Baseline is produced by the pre-migration Dockerfile's build stage (`docker build --target build` at the Baseline commit, then copying `/output` out). It lives outside the worktree.
- Comparison rules:
  - **HTML**: parsed and compared as trees. Ignored: whitespace outside `pre`/`textarea`/`script`, attribute order, void-tag syntax, character references vs literal characters, quoting style, HTML comments. Normalised away: kramdown's code-block wrappers and the `language-plaintext`/`highlighter-rouge`/`highlight` classes (no style targets them).
  - **JSON-LD** and other embedded JSON: compared as parsed JSON.
  - **Feeds and sitemaps**: compared as normalised XML.
  - **CSS**: equal after running both through the same minifier.
  - **Everything else**: byte-identical.
- Excluded: `pagefind/` (only checked for existence), build timestamps (feed `<updated>`, footer year).
- Known exceptions, written in the script with a reason each: the dropped `/en/` copies of static files, EN pages referencing root assets instead of `/en/…`, sitemap without static-file entries, `pagination-page-1-redirect` (Zola always writes `<section>/page/1/` as a redirect; jekyll-paginate wrote nothing there), `no-css-source-map` (dart-sass wrote `main.css.map`; Zola's Sass compiler emits none).
- Smart punctuation was verified in a spike: Zola's `smart_punctuation` matches kramdown on all 57 posts and pages, so there are no source-level exceptions for punctuation.

### Content
- Content moves into Zola's `content/` tree: posts under a posts section grouped by year; pages as their own files. Files are renamed with `git mv`: `x.pl.md` → `x.md`, `x.en.md` stays.
- Front matter is converted to TOML. Each post gets an explicit `path` reproducing its existing URL exactly (English: `en/…`). Dates are kept with their existing instants; URL dates already shifted by Jekyll's Europe/Warsaw conversion are preserved.
- Translations carry every field they need (date, path, category, header, last-modified); nothing is inherited.
- Categories (`tournaments`, `blog`, `other`) become a Zola taxonomy, per language.
- Existing heading IDs are copied from the Baseline into explicit `{#id}` attributes by a one-time script. Zola's explicit IDs keep Unicode and `--` exactly (verified in the spike).
- Liquid in content is replaced by shortcodes: `figure` (also replacing the hand-written figure blocks in the instant-ramen post), `help_items(collection=…)`, `footer_link(label=…)` (looked up by label, not position). `{% raw %}` and `{% comment %}` blocks get Zola equivalents or plain HTML comments.
- Source edits where pulldown-cmark differs visibly: `\\` line breaks (brief-history post, 2 lines); loose/tight list items that change `<p>` wrapping (mostly saki-cards 2022); any other visible difference the Parity check finds.
- `lang-exclusive` is kept as a front-matter field; the how-to-buy post simply has no `.en.md`.

### Templates
- Tera ports of the `default`, `home`, `post`, `page` and `category` layouts and all includes, keeping the same markup and classes.
- UI strings stay in a data file with `pl`/`en` blocks, and navigation stays per language.
- Shared per-page values (current path without language prefix, language-switch target, post category) are computed in one macro or base-template block.
- Excerpt = the rendered content before its first `</p>`, so posts that start with a figure keep today's behaviour, including the empty description.
- Polish month names and plurals are ported from the existing data and logic. The footer year uses the build time.
- Build-time checks use Tera `throw`: a Translation's date, category or path disagrees with its Original; a post has no Translation and isn't Language-exclusive; a post's `path` doesn't match its date and category.
- Home pagination: 10 per page at `/page/N/`, per language. Category pages are not paginated.
- Custom Atom templates reproduce jekyll-feed's structure (10 entries, full content, `xml:lang`, the same entry IDs and links). A custom sitemap lists the same page URLs and `<lastmod>`s, without static files.
- `robots.txt` is generated at the root only.
- SCSS is compiled by Zola. The `_sass` partials and tokens stay as they are, moved to where Zola expects them.

### Static output
- Static files are served from the root only. EN pages reference root assets. Generated pages (pages, feed, sitemap, 404) exist under `/en/`.
- Only `content/` and `static/` are published, so stray root files can no longer leak.

### Build and deploy
- The Dockerfile copies the Zola binary from the pinned official image into a slim build stage with Pagefind, runs `zola build` (with `--base-url "$SITE_URL"` for previews), runs Pagefind, then copies the result into the existing nginx image.
- The GitHub Pages and Cloudflare preview workflows keep working unchanged as far as possible.
- Dependabot: remove `bundler`; the `docker` setting picks up the Zola image.
- `Gemfile`, `Gemfile.lock`, `_config.yml`, `_plugins/` and the Jekyll-only files are removed. README, `AGENTS.md` and `docker-compose.yml` are updated.

## Testing Decisions

- The single seam is the Parity check over the whole built site. It tests output only, not template internals, so templates can be refactored freely as long as the output stays Render-equivalent.
- Each ticket's acceptance criterion is "the Parity check is clean for the URL families this ticket covers". Tickets report the remaining differences elsewhere instead of hiding them.
- The build-time `throw` checks are tested by deliberately breaking a Translation's date or path, or removing a Translation, in a scratch copy, and confirming `zola build` fails with a clear message.
- Manual check at the end: click through the Cloudflare PR preview (search, theme toggle, language switch, pagination).
- There are no existing tests in the repo. This is the first.

## Out of Scope

- Design or content changes, new features, and fixing existing oddities: wrong timezone offsets in front matter, English-style quotes in Polish text, empty descriptions on posts that start with a figure.
- Redirects for the dropped `/en/` static-file URLs.
- A permanent CI parity check (Jekyll goes away).
- Changing the hosting (GitHub Pages, Cloudflare previews, nginx image).

## Further Notes

- Zola version: 0.23.6 (latest at time of writing), run from `ghcr.io/getzola/zola:v0.23.6`.
- Spike findings: explicit `{#id}` works; smart punctuation matches; a Translation with the same `path` as its Original is a URL collision, so `en/` prefixes are required.
- Delivery: everything goes on the `zola-migration` branch and ships as one PR, with the Parity check report and the preview link.
