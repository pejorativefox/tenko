#!/usr/bin/env bash
# Keep only the newest version of each package in an RPM repository.
# Requires rpmdev-vercmp (rpmdevtools).
set -euo pipefail
repo=${1:?repo directory}
[ -d "$repo" ] || exit 0

declare -A best
declare -A bestfile

for rpm in "$repo"/*.rpm; do
    [ -e "$rpm" ] || continue
    read -r name evr < <(rpm -qp --qf '%{NAME} %{VERSION}-%{RELEASE}\n' "$rpm" 2>/dev/null) || continue
    [ -n "${name:-}" ] || continue
    if [ -z "${best[$name]:-}" ]; then
        best[$name]=$evr
        bestfile[$name]=$rpm
        continue
    fi
    if rpmdev-vercmp "${best[$name]}" "$evr" >/dev/null 2>&1; then
        : # equal
    elif [ $? -eq 12 ]; then
        # evr is newer
        rm -f "${bestfile[$name]}"
        best[$name]=$evr
        bestfile[$name]=$rpm
    else
        rm -f "$rpm"
    fi
done
