#!/bin/sh
# Verifies the translation guards: each mutation in a scratch copy must make `zola build` fail with the expected message.
# Usage: sh _migrate/check_translation_guard.sh   (delete in ticket 10)
set -u
src=$(pwd); fail=0
en=content/posts/2019/2019-12-24-merry-christmas.en.md
check() { # $1 = shell mutation run in the scratch copy, $2 = expected message fragment
  tmp=$(mktemp -d); cp -r "$src/." "$tmp"; rm -rf "$tmp/public"
  (cd "$tmp" && sh -c "$1")
  out=$(docker run --rm -u "$(id -u):$(id -g)" -v /usr/share/zoneinfo:/usr/share/zoneinfo:ro -v "$tmp:/app" -w /app ghcr.io/getzola/zola:v0.23.6 build 2>&1)
  if echo "$out" | grep -q "$2"; then echo "ok   $1"; else echo "FAIL $1"; echo "$out" | tail -5; fail=1; fi
  rm -rf "$tmp"
}
check "sed -i 's/^date = 2019-12-24T12:00:00+01:00/date = 2019-12-24T13:00:00+01:00/' $en" "date .* differs from its Original"
check "sed -i 's/^categories = \[\"other\"\]/categories = [\"blog\"]/' $en" "category .* differs from its Original"
check "sed -i 's|^path = \"en/other/2019/12/24/merry-christmas\"|path = \"en/other/2019/12/24/merry-xmas\"|' $en" "path .* differs from its Original"
check "rm $en" "has no en Translation"
exit $fail
