#!/usr/bin/env bash
# Run the checks that must pass before publishing: the unit tests, the
# tenko-base Requires block and the static freedesktop audit.
#
# Usage:
#   tenko check
#
# The freedesktop audit is static here (specs and file lists); audit a
# release candidate against the built RPMs as well:
#
#   tenko audit --rpm-dir build/repo-publish/6
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"

python3 -m unittest discover -s tests
python3 scripts/check/base_requires.py --check
python3 scripts/check/fdo_audit.py --no-rpm
