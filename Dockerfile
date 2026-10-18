FROM ruby:3.4-trixie AS build

WORKDIR /srv/jekyll
COPY Gemfile Gemfile.lock /srv/jekyll/
RUN bundler install

ARG PAGEFIND_VERSION=1.3.0
RUN curl -fsSL "https://github.com/Pagefind/pagefind/releases/download/v${PAGEFIND_VERSION}/pagefind_extended-v${PAGEFIND_VERSION}-x86_64-unknown-linux-musl.tar.gz" \
    | tar -xz -C /usr/local/bin pagefind_extended

COPY . /srv/jekyll
ENV JEKYLL_ENV=production
RUN jekyll build && pagefind_extended --site _site && mv _site /output

FROM nginx:alpine

WORKDIR /usr/share/nginx/html/
COPY --from=build /output .
COPY _nginx/default.conf /etc/nginx/conf.d/
