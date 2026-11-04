#!/usr/bin/env python3
"""Rewrite a spec's single %files section from an installed buildroot.

The tree ships static file lists (no %dir entries, no globs): every regular
file and symlink installed under BUILDROOT appears in %files.  This helper
regenerates that list after a version bump whose %install tree changed.

Usage:
    scripts/regen_files.py --spec package_specs/flac/flac.spec \\
        --buildroot build/d7/out2/build/flac/BUILDROOT/flac-1.5.0-1.x86_64

Only specs with exactly one %files section are supported; multi-package
specs are reported and must be edited by hand.  With --write the spec is
updated in place, otherwise the new section is printed.
"""

import argparse
import os
import sys


def files_under(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in dirnames:
            path = os.path.join(dirpath, name)
            if os.path.islink(path):
                out.append(os.path.relpath(path, root))
        for name in filenames:
            path = os.path.join(dirpath, name)
            out.append(os.path.relpath(path, root))
    return sorted(out)


def section_bounds(lines):
    starts = [i for i, line in enumerate(lines) if line.startswith("%files")]
    if len(starts) != 1:
        return None
    start = starts[0]
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("%"):
            return start, i
    return start, len(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--buildroot", required=True)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    text = open(args.spec, encoding="utf-8").read()
    lines = text.splitlines()
    bounds = section_bounds(lines)
    if not bounds:
        print("error: %s does not have exactly one %%files section" % args.spec,
              file=sys.stderr)
        return 1
    start, end = bounds
    if not os.path.isdir(args.buildroot):
        print("error: no buildroot %s" % args.buildroot, file=sys.stderr)
        return 1

    files = files_under(args.buildroot)
    if not files:
        print("error: %s is empty" % args.buildroot, file=sys.stderr)
        return 1

    header = lines[start]
    new = [header] + ["/" + f for f in files] + [""]
    old = lines[start:end]
    print("--- %s" % args.spec)
    print("files: %d (was %d)" % (len(files), max(0, len(old) - 1)))
    for line in old:
        if line and line not in new:
            print("- " + line)
    for line in new:
        if line and line not in old:
            print("+ " + line)

    if args.write:
        lines[start:end] = new
        open(args.spec, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print("wrote %s" % args.spec)
    return 0


if __name__ == "__main__":
    sys.exit(main())
