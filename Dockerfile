FROM ruby:3.0-bullseye AS build
WORKDIR /srv/jekyll
COPY . /srv/jekyll
RUN bundler install
ENV JEKYLL_ENV=production
RUN jekyll build && mv _site /output

FROM nginx:alpine
WORKDIR /usr/share/nginx/html/
COPY --from=build /output .
COPY _nginx/default.conf /etc/nginx/conf.d/
