#!/usr/bin/env bash
# Show the failed packages and the tail of each build log from a
# scripts/verify_base_in_container.sh run.
set -euo pipefail
OUT=${1:?usage: $0 build/container-rebuild-YYYYMMDD-N [lines]}
LINES=${2:-60}

if [ ! -d "$OUT/status" ]; then
    echo "no status directory: $OUT/status" >&2
    exit 1
fi

failures=0
for status in "$OUT"/status/*; do
    read -r state package rest <"$status"
    [ "$state" = fail ] || continue
    failures=$((failures + 1))
    echo "======================================================================"
    echo "FAIL: $package ($rest)"
    echo "log: $OUT/logs/$package.log"
    echo "----------------------------------------------------------------------"
    tail -n "$LINES" "$OUT/logs/$package.log" 2>/dev/null || echo "(missing log)"
done

if [ "$failures" -eq 0 ]; then
    echo "all packages passed"
else
    echo "$failures package(s) failed"
fi
