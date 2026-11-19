# Zola replaces Jekyll, measured by render-equivalence

The site moved from Jekyll (Ruby, jekyll-polyglot, kramdown) to Zola so that building it needs a single pinned binary instead of a Ruby toolchain and five plugins. The migration was accepted when the Zola output was Render-equivalent to the Jekyll Baseline (a browser shows the same thing), not byte-identical: kramdown and pulldown-cmark serialise HTML differently, and chasing bytes would have meant reproducing kramdown quirks in templates for no visible gain.

## Consequences

- Every post carries an explicit `path` because Zola has no permalink pattern; existing URLs were preserved exactly, including ones whose date differs from the filename (a Jekyll Europe/Warsaw timezone artefact).
- Heading IDs are written explicitly (`{#id}`) in existing content to keep kramdown-style anchors; new headings get Zola's IDs.
- The `/en/` copies of static files that jekyll-polyglot produced (`/en/assets/…`, `/en/pralka/`, …) were dropped deliberately; only generated pages live under `/en/`.
- Translations no longer inherit front matter from the Original; each file is self-contained and the templates fail the build when a pair disagrees.
