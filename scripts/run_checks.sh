#!/bin/sh
# Local/CI entry point for the checks that must pass before publishing.
#
# The freedesktop audit is static here (specs and file lists); a release
# candidate should also be audited against the built RPMs:
#
#   python3 scripts/fdo_audit.py --rpm-dir build/repo-publish/6
#
set -eu
cd "$(dirname "$0")/.."

python3 -m unittest discover -s tests
scripts/gen_base_requires.py --check
python3 scripts/fdo_audit.py --no-rpm
