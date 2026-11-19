# 03: All Polish posts

**What to build:** Every Original post is moved to Zola and passes the Parity check at its existing URL.

- A one-time migration script, kept until ticket 10, that for each Polish post:
  - renames it with `git mv` (`x.pl.md` → `x.md`, under a posts section grouped by year)
  - converts the front matter to TOML
  - sets an explicit `path` taken from the post's Baseline URL. This keeps Warsaw-time date shifts and slug casing such as `Mahjong-parlors-in-japan-a-blog-post`
  - writes `{#id}` on every heading using the Baseline's IDs
- `figure` shortcode replacing all `{% include figure.html %}`, and also the hand-written capture/markdownify figure blocks in the instant-ramen post. `relative_url` uses become plain root paths.
- Visible renderer differences fixed in the source: the `\\` line breaks in the brief-history post, loose/tight list items (mostly saki-cards 2022), and anything else the Parity check reveals.
- `{% comment %}` / `{% raw %}` blocks get Zola equivalents. Content inside HTML comments doesn't need to match.
- Previous/next links work between Polish posts, by date.
- Build-time check (Tera `throw`): a post's `path` must match its date (Europe/Warsaw) and category.
- `lang-exclusive` kept as a front-matter field on how-to-buy.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] All 25 Polish post URLs exist and pass the Parity check
- [ ] No Liquid syntax remains in the migrated posts
- [ ] A post whose `path` disagrees with its date or category fails `zola build` with a clear message (verified in a scratch copy)
- [ ] File history preserved (renames show up in `git log --follow`)
