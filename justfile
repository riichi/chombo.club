# Developer tasks. Tools are pinned in mise.toml: run `mise install` once, then `just <recipe>`.

set shell := ["bash", "-euo", "pipefail", "-c"]

# Run the tools pinned in mise.toml when mise is installed, even if it is not activated in the
# shell; otherwise whatever zola/pagefind is on PATH.
export PATH := `p=$(command -v mise >/dev/null && mise bin-paths | paste -sd: -) || true; echo "${p:+$p:}$PATH"`

# Nu HTML Checker image; only `latest` tracks the current HTML standard
vnu_image := "ghcr.io/validator/validator:latest"

# List the recipes
default:
    @just --list

# Live-reloading dev server at http://127.0.0.1:1111 (no search index)
serve:
    zola serve

# Build the site into public/ and index it for search. `base_url` overrides zola.toml's (PR previews).
build base_url="":
    zola build {{ if base_url != "" { "--base-url " + quote(base_url) } else { "" } }}
    # Zola always renders the taxonomy list page; the site has no category index.
    rm -f public/categories/index.html public/en/categories/index.html
    pagefind --site public

# Build, then serve public/ with search at http://127.0.0.1:1414
preview: build
    pagefind --site public --serve

# Check internal links and anchors (fast; no network)
check:
    zola check --skip-external-links

# Also check external links (slow; needs network)
check-external:
    zola check

# Validate the built HTML with the Nu HTML Checker (needs Docker). Run `just build` first.
validate:
    test -d public || { echo "public/ not found; run 'just build' first" >&2; exit 1; }
    # Skipped: Zola's /page/1/ redirect stubs. Filtered: "<img />"-style notices, which Zola's
    # Markdown renderer (pulldown-cmark) emits for images, <hr> and hard line breaks.
    cd public && find . -name '*.html' -not -path './page/1/*' -not -path './en/page/1/*' -print0 \
        | sort -z \
        | xargs -0 docker run --rm -v "$PWD:/site:ro" -w /site {{ vnu_image }} \
            vnu --Werror --format gnu --filterpattern '.*Trailing slash on void elements.*'

# Run the pre-commit hooks (djLint etc.) on all files, with prek or pre-commit
lint:
    if command -v prek >/dev/null; then prek run --all-files; else pre-commit run --all-files; fi

# Remove build output
clean:
    rm -rf public
