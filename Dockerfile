FROM ruby:3.3-bullseye AS build

WORKDIR /srv/jekyll
COPY Gemfile Gemfile.lock /srv/jekyll/
RUN bundler install

COPY . /srv/jekyll
ENV JEKYLL_ENV=production
RUN jekyll build && mv _site /output

FROM nginx:alpine

WORKDIR /usr/share/nginx/html/
COPY --from=build /output .
COPY _nginx/default.conf /etc/nginx/conf.d/
