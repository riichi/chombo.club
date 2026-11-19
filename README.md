chombo.club
===========

[Kraków Chombo Club](https://chombo.club) website source. Built using [Zola](https://www.getzola.org/) (v0.23, Tera v2 templates).

## Quickstart

Install Zola 0.23 and run:

```
zola serve
```

Then visit [127.0.0.1:1111](http://127.0.0.1:1111).

Search is built by [Pagefind](https://pagefind.app/) after Zola, so `zola serve` has no search index.
To try search locally, build the site and index it:

```
zola build
npx pagefind@1.3.0 --site public --serve
```

## Layout

- `content/posts/<year>/` – posts; `content/pages/` – standalone pages (about, calendar, contact, help); `content/_index{,.en}.md` – home pages.
- `templates/` – Tera templates; reusable pieces are components in `templates/components.html`, partials in `templates/partials/`.
- `sass/` – styles (compiled by Zola); `static/` – files copied as-is (images, downloads, JS, favicons).
- `data/` – UI labels (`ui-text.yml`), navigation (`navigation/{pl,en}.yml`) and help-page link lists (`help/*.yml`).
- `zola.toml` – site config; Polish is the default language, English lives under `/en/`.

Long posts and pages get a table of contents automatically (3+ headings); set `extra.toc = false` in front matter to hide it.

## Adding a post

Posts live in `content/posts/<year>/`, with the English Translation next to the Polish Original:

```
content/posts/2024/2024-07-27-headquarters.md
content/posts/2024/2024-07-27-headquarters.en.md
```

Both files carry full TOML front matter (each Translation is self-contained, nothing is inherited):

```
+++
title = "Mamy siedzibę!"
date = 2024-07-27T19:21:00+01:00
path = "other/2024/07/27/headquarters"
template = "post.html"

[taxonomies]
categories = ["other"]
+++
```

- `path` is explicit and must be `<category>/<Y>/<m>/<d>/<slug>` with the date in Europe/Warsaw; the English one is the same path prefixed with `en/` (Zola does not add the language prefix to a custom `path`).
- The build fails if a post's path does not match its date and category, or if a Translation's date, category or path differs from its Original.
- A Polish post without a Translation fails the build unless it sets `extra.lang-exclusive = ["pl"]`.

Pages follow the same pattern (`content/pages/about.md` with `path = "about"`, `about.en.md` with `path = "en/about"`, `template = "page.html"`).

## Images

Use plain Markdown: `![alt](/assets/images/foo.jpg)`. An image alone in its paragraph is styled as a figure, and an italic line right below it as its caption (CSS only, in `sass/assets/css/_content.scss`). Escape `*` in alt text (`\*`), or Markdown reads it as emphasis.

## Components

Tera v2 has no shortcodes or macros. Reusable markup is written as components (`{% component name(...) %}` in `templates/components.html`) and can be called from templates and Markdown, e.g.:

```
{{ <footer_link label="Discord" links={config.extra.footer_links} /> }}
```

Components are hygienic: pass everything they need explicitly. When used in Markdown they must not emit indented or blank lines, or CommonMark turns the output into a code block.

## Sitemap and 404 per language

Zola renders `sitemap.xml` and `404.html` only for the default language. To get `/en/sitemap.xml` and `/en/404.html`, `zola.toml` lists them in `[languages.en] feed_filenames`: Zola then renders those templates as English "feeds", with `lang = "en"` and `feed_url` set instead of `page`/`section`. `templates/base.html` derives the page path from `feed_url` in that case, and `templates/sitemap.xml` handles both renderings (with and without `lang`).

## Building the Docker image

The Dockerfile runs `zola build`, deletes the generated `/categories/` and `/en/categories/` index pages (Zola always renders the taxonomy list; the site has none), runs Pagefind, and serves the result with nginx. Using `docker compose`:

```
docker compose up --build
```

Then visit [localhost:8000](http://localhost:8000) to see the webpage.
