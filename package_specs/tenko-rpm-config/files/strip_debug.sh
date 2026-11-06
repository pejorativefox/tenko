#!/bin/sh
# Strip writable executables in a buildroot without failing on read-only files.
set -e
BUILDROOT="${1:?usage: strip_debug.sh <buildroot>}"
find "$BUILDROOT" -type f -writable -executable \
    -exec sh -c "file '{}' | grep -q 'not stripped'" \; -print |
while IFS= read -r f; do
    strip -v -g "$f" || true
done
