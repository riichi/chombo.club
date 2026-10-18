chombo.club
===========

[Kraków Chombo Club](https://chombo.club) website source. Built using [Jekyll](https://jekyllrb.com/).

## Quickstart

```
gem install jekyll bundler
bundle install
jekyll serve
```

Search is built by [Pagefind](https://pagefind.app/) after Jekyll, so `jekyll serve` has no search index.
To try search locally, build the site and index it:

```
bundle exec jekyll build
npx pagefind@1.3.0 --site _site --serve
```

## Theme

The theme lives in this repository (no theme gem): `_layouts/`, `_includes/`, `_sass/` and `assets/js/site.js`.
UI labels for both languages are in `_data/ui-text.yml`; navigation in `_data/{pl,en}/navigation.yml`.
Long posts and pages get a table of contents automatically (3+ headings); set `toc: false` in front matter to hide it.

## Testing Docker image locally
Using `docker-compose`:
```
$ docker-compose up --build
```
Then visit [localhost:8000](http://localhost:8000) to see the webpage.
