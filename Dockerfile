FROM jekyll/jekyll:latest as build
COPY . /srv/jekyll
ENV JEKYLL_ENV=production
RUN jekyll build

FROM nginx:alpine
COPY --from=build /srv/jekyll/_site /usr/share/nginx/html/
COPY _nginx/default.conf /etc/nginx/conf.d/
