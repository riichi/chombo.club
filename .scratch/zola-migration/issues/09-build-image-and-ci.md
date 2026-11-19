# 09: Build image and CI without Ruby

**What to build:** The Docker build and deployment run on Zola.
- The Dockerfile build stage copies the Zola binary from `ghcr.io/getzola/zola:v0.23.6` into a slim base with Pagefind (same pinned version as today). It runs `zola build`, with `--base-url "$SITE_URL"` when the `SITE_URL` build arg is set, then Pagefind, and keeps the nginx final stage.
- `docker-compose up --build` still serves the site on localhost:8000.
- The GitHub Pages and Cloudflare preview workflows still work. Adjust them only if they reference Jekyll.
- Dependabot: remove the `bundler` entry; the `docker` entry now tracks the Zola image.

**Blocked by:** 02

**Status:** done

- [x] `docker build .` succeeds with no Ruby in any stage
- [x] Search works in the built image (Pagefind indexes `data-pagefind-body` content)
- [x] Building with `SITE_URL` set makes canonical/OG/feed URLs point at that URL
- [x] `docker-compose up --build` serves the site
