#!/bin/sh
# Verifies the post path guard: a post whose path disagrees with its date or category must fail `zola build`.
# Usage: sh _migrate/check_path_guard.sh   (delete in ticket 10)
set -u
src=$(pwd); fail=0
for mutation in 's/^date = 2019-12-24T12/date = 2019-12-25T12/' 's/^categories = \["other"\]/categories = ["tournaments"]/' 's/^date = 2019-12-24T12:00:00+01:00/date = 2019-12-24T23:30:00-01:00/'; do
  tmp=$(mktemp -d); cp -r "$src/." "$tmp"; rm -rf "$tmp/public"
  # mutate the Translation too, so the translation guard stays quiet
  sed -i "$mutation" "$tmp/content/posts/2019/2019-12-24-merry-christmas.md" "$tmp/content/posts/2019/2019-12-24-merry-christmas.en.md"
  out=$(docker run --rm -u "$(id -u):$(id -g)" -v /usr/share/zoneinfo:/usr/share/zoneinfo:ro -v "$tmp:/app" -w /app ghcr.io/getzola/zola:v0.23.6 build 2>&1)
  if echo "$out" | grep -q "does not match its date"; then echo "ok   $mutation"; else echo "FAIL $mutation"; echo "$out" | tail -5; fail=1; fi
  rm -rf "$tmp"
done
exit $fail
