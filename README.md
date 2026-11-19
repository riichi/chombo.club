chombo.club
===========

[Kraków Chombo Club](https://chombo.club) website source. Built using [Zola](https://www.getzola.org/) (v0.23, Tera v2 templates).

## Quickstart

The tools are pinned in `mise.toml` (Zola, Pagefind). Install [mise](https://mise.jdx.dev/) and [just](https://just.systems/), then:

```
mise install
just serve
```

Then visit [127.0.0.1:1111](http://127.0.0.1:1111). The recipes find the mise-installed tools by themselves (`mise activate` is not needed). Without mise, install the versions listed in `mise.toml` yourself.

Search is built by [Pagefind](https://pagefind.app/) after Zola, so `just serve` has no search index.
To try search locally, run `just preview` (builds the site into `public/`, indexes it and serves it at [127.0.0.1:1414](http://127.0.0.1:1414)).

## Tasks

`just --list` shows every recipe:

- `just serve` – live-reloading dev server.
- `just build [base_url]` – the production build in `public/`: `zola build`, then deletes the generated `/categories/` and `/en/categories/` index pages (Zola always renders the taxonomy list; the site has none), then runs Pagefind. CI deploys this output.
- `just preview` – build, then serve `public/` with search.
- `just check` – internal links and anchors (`zola check --skip-external-links`); `just check-external` also checks external links.
- `just validate` – checks the built HTML with the [Nu HTML Checker](https://validator.github.io/validator/) (runs in Docker). Run `just build` first.
- `just lint` – the pre-commit hooks on all files.

The Checks workflow (`.github/workflows/checks.yml`) runs `check`, `build` + `validate` and the pre-commit hooks on pull requests and on `master`; it is separate from the deploy workflow, so a failing check does not block deploys.

## Layout

- `content/posts/<year>/` – posts; `content/pages/` – standalone pages (about, calendar, contact, help); `content/_index{,.en}.md` – home pages.
- `templates/` – Tera templates; reusable pieces are components in `templates/components.html`, partials in `templates/partials/`.
- `sass/` – styles (compiled by Zola); `static/` – files copied as-is (images, downloads, JS, favicons).
- `data/` – UI labels (`ui-text.yml`), navigation (`navigation/{pl,en}.yml`) and help-page link lists (`help/*.yml`).
- `zola.toml` – site config; Polish is the default language, English lives under `/en/`.
- `mise.toml` (+ `mise.lock`) – pinned tool versions; `justfile` – developer tasks.

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

Use plain Markdown: `![alt](/assets/images/foo.jpg)`. An image alone in its paragraph is laid out as a figure (CSS only, in `sass/assets/css/_content.scss`). Escape `*` in alt text (`\*`), or Markdown reads it as emphasis.

For a captioned image, write the HTML: `<figure>` with the `<img>` and a `<figcaption>`, without blank lines inside (see the brief-history post). Markdown is not processed inside it.

## Components

Tera v2 has no shortcodes or macros. Reusable markup is written as components (`{% component name(...) %}` in `templates/components.html`) and can be called from templates and Markdown, e.g.:

```
{{ <footer_link label="Discord" links={config.extra.footer_links} /> }}
```

Components are hygienic: pass everything they need explicitly. When used in Markdown they must not emit indented or blank lines, or CommonMark turns the output into a code block.

Templates are formatted and linted by [djLint](https://djlint.com/) (`.djlintrc`), run as a [pre-commit](https://pre-commit.com/) hook (`pre-commit install`, or `prek install`). `components.html` is excluded, because reformatting would break components used in Markdown.

## Sitemap

`templates/sitemap.xml` lists every language in one `/sitemap.xml`; each URL that exists in several languages lists its versions as `hreflang` alternates.

## 404 page per language

Zola renders `404.html` only for the default language. To get `/en/404.html`, `zola.toml` lists it in `[languages.en] feed_filenames`: Zola then renders the template as an English "feed", with `lang = "en"` and `feed_url` set instead of `page`/`section`. `templates/base.html` derives the page path from `feed_url` in that case.
