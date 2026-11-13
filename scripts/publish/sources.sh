#!/usr/bin/env bash
# Upload the source bundles Tenko generates itself (vendored Rust/Go
# dependencies from `tenko vendor`) to the public site and the LAN mirror.
#
# For each package, every `sources` line whose URL is
# $PUBLIC_URL/sources/<pkg>/<file> is taken from the sources cache, checked
# against its recorded md5 and uploaded to sources/<pkg>/ on both targets,
# so `tenko fetch` works on any host.
#
# Usage:
#   tenko publish sources gh restic
#   tenko publish sources --all       # every package with hosted sources
#
# Environment: DRY_RUN=1 uploads nothing; MIRROR=0 skips the LAN mirror
# (local-only tests); R2, MIRROR, MIRROR_PUBLIC override the targets.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
. scripts/lib/publish.sh

prefix=$PUBLIC_URL/sources/

if [ "${1:-}" = --all ]; then
    mapfile -t pkgs < <(grep -l -F "$prefix" package_specs/*/sources |
                        xargs -r -n1 dirname | xargs -r -n1 basename)
else
    pkgs=("$@")
fi
[ ${#pkgs[@]} -gt 0 ] || die "usage: tenko publish sources PKG... | --all"

for pkg in "${pkgs[@]}"; do
    pkg=${pkg%/}
    pkg=${pkg##*/}
    sources=package_specs/$pkg/sources
    [ -f "$sources" ] || die "no sources file: $sources"
    files=()
    while read -r md5 url _; do
        case "$md5" in ''|'#'*) continue ;; esac
        case "$url" in "$prefix$pkg/"*) ;; *) continue ;; esac
        file=$TENKO_SOURCES_DIR/${url##*/}
        [ -f "$file" ] || die "$pkg: ${url##*/} is not in $TENKO_SOURCES_DIR (run tenko vendor $pkg)"
        [ "$(md5sum <"$file" | cut -d' ' -f1)" = "$md5" ] ||
            die "$pkg: ${url##*/} does not match the md5 in $sources"
        files+=("$file")
    done <"$sources"
    [ ${#files[@]} -gt 0 ] || die "$pkg: $sources lists nothing under $prefix$pkg/"
    publish_files "sources/$pkg" "${files[@]}"
    [ "$DRY_RUN" = 1 ] && continue
    for file in "${files[@]}"; do
        echo "  $prefix$pkg/${file##*/}"
        mirror_enabled && echo "  $MIRROR_URL/sources/$pkg/${file##*/}"
    done
done
