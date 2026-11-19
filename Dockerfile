FROM ghcr.io/getzola/zola:v0.23.6 AS zola

FROM debian:trixie-slim AS build

# tzdata: Europe/Warsaw date formatting in templates; the Zola image has none
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl tzdata \
    && rm -rf /var/lib/apt/lists/*

ARG PAGEFIND_VERSION=1.3.0
RUN curl -fsSL "https://github.com/Pagefind/pagefind/releases/download/v${PAGEFIND_VERSION}/pagefind_extended-v${PAGEFIND_VERSION}-x86_64-unknown-linux-musl.tar.gz" \
    | tar -xz -C /usr/local/bin pagefind_extended

COPY --from=zola /zola /usr/local/bin/zola

WORKDIR /srv/site
COPY . /srv/site
# Zola always renders the taxonomy list page; the Baseline has no /categories/ index, so it is deleted.
# Previews override the site url so canonical/OG/feed links point at the preview
ARG SITE_URL=
RUN if [ -n "$SITE_URL" ]; then \
      zola build --base-url "$SITE_URL" --output-dir /output; \
    else \
      zola build --output-dir /output; \
    fi \
    && rm /output/categories/index.html /output/en/categories/index.html \
    && pagefind_extended --site /output

FROM nginx:alpine

WORKDIR /usr/share/nginx/html/
COPY --from=build /output .
COPY _nginx/default.conf /etc/nginx/conf.d/
