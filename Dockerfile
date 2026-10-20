FROM ruby:3.4.11-trixie AS build

WORKDIR /srv/jekyll
COPY Gemfile Gemfile.lock /srv/jekyll/
RUN bundler install

ARG PAGEFIND_VERSION=1.3.0
RUN curl -fsSL "https://github.com/Pagefind/pagefind/releases/download/v${PAGEFIND_VERSION}/pagefind_extended-v${PAGEFIND_VERSION}-x86_64-unknown-linux-musl.tar.gz" \
    | tar -xz -C /usr/local/bin pagefind_extended

COPY . /srv/jekyll
ENV JEKYLL_ENV=production
# Previews override the site url so canonical/OG/feed links point at the preview
ARG SITE_URL=
RUN if [ -n "$SITE_URL" ]; then \
      printf 'url: "%s"\n' "$SITE_URL" > /tmp/_config.preview.yml; \
      jekyll build --config _config.yml,/tmp/_config.preview.yml; \
    else \
      jekyll build; \
    fi \
    && pagefind_extended --site _site && mv _site /output

FROM nginx:alpine

WORKDIR /usr/share/nginx/html/
COPY --from=build /output .
COPY _nginx/default.conf /etc/nginx/conf.d/
