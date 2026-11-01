#!/usr/bin/env python3
"""Generate a static %files list from an installed buildroot tree.

Use this when a package is rebuilt at a new version and its previous static
filelist no longer matches: run `rpmbuild -bi` (or `make install
DESTDIR=...`), point --root at the populated buildroot, then package with
`rpmbuild -bb --short-circuit` and the generated list.

Usage:
    ./scripts/gen_filelist_tree.py --root path/to/BUILDROOT/pkg-ver-rel.arch \
        [--output package_specs/pkg/files/pkg.filelist] [--stdout]
"""

import argparse
import os
import sys

SKIP_DIRS = {"/", "/usr", "/etc", "/var", "/var/lib", "/var/log", "/var/cache", "/var/run"}


def walk(root):
    entries = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        base = "/" if rel == "." else "/" + rel
        for d in dirnames:
            path = base.rstrip("/") + "/" + d
            if os.path.basename(path) == ".build-id":
                continue
            if path not in SKIP_DIRS:
                entries.append("%dir " + path)
        for f in filenames:
            path = base.rstrip("/") + "/" + f
            if os.path.basename(path) in (".build-id",):
                continue
            entries.append(path)
    return entries


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True)
    ap.add_argument("--output")
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        sys.exit("no such buildroot: " + args.root)
    lines = sorted(set(walk(args.root)))
    text = "\n".join(lines) + "\n"
    if args.stdout or not args.output:
        sys.stdout.write(text)
        return 0
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(text)
    print("{}: {} entries".format(args.output, len(lines)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
