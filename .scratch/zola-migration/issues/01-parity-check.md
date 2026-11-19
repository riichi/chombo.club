# 01: Parity check

**What to build:** The single test seam for the migration (see spec, "Parity check"). It's a standalone Python script (stdlib + `lxml`) that takes a Baseline directory and a Zola output directory and reports, per file: missing, extra, Render-equivalent, or different, with a readable diff. It ends with a summary and a non-zero exit code when anything differs that isn't a known exception. It also documents how to rebuild the Baseline: `docker build --target build` at the Baseline commit using the pre-migration Dockerfile, then copy `/output` out to a directory outside the worktree. The Baseline for `ae8d366` already exists at `../zola-baseline/site` relative to the worktree.

The script can filter by URL family or path prefix, so later tickets can check only their slice.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] HTML compared as trees, ignoring whitespace outside `pre`/`textarea`/`script`, attribute order, void-tag syntax, character references vs literal characters, quoting style and comments
- [ ] kramdown code-block wrappers and the `language-plaintext`/`highlighter-rouge`/`highlight` classes normalised away
- [ ] JSON-LD / embedded JSON compared as parsed JSON; feeds and sitemaps as normalised XML; CSS after the same minifier on both sides; everything else byte-identical
- [ ] `pagefind/` only checked for existence; feed `<updated>` and footer year ignored
- [ ] Known exceptions are listed in one place, each with a reason: dropped `/en/` static-file copies, EN pages referencing root assets, sitemap without static files
- [ ] Path-prefix filter supported
- [ ] Self-test: Baseline vs itself is clean; Baseline vs an empty directory reports every file missing; a hand-edited copy with a changed word is reported, while one with only reindented whitespace is not
