#!/usr/bin/env python3
"""Regenerate the tenko-base Requires block from package_specs/base.json.

The base meta used to carry ~100 hand-written Requires lines that had to be
updated by hand whenever the base list changed.  This script expands
base.json's package list (mapped through its aliases) plus the explicit
extras in package_specs/tenko-base/requires-extra, and rewrites the block
between the GENERATED REQUIRES markers in the spec.

Usage:
    tenko base-requires           # rewrite the spec in place
    tenko base-requires --check   # exit 1 if the block is stale
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, "package_specs", "base.json")
SPEC = os.path.join(ROOT, "package_specs", "tenko-base", "tenko-base.spec")
EXTRA = os.path.join(ROOT, "package_specs", "tenko-base", "requires-extra")

BEGIN = "# BEGIN GENERATED REQUIRES"
END = "# END GENERATED REQUIRES"

# Base package names that are split into several binary packages.
SPLIT = {
    "dbus": ["dbus-daemon", "dbus-libs"],
    "vim": ["vim-minimal"],
}


def read_extra():
    names = []
    with open(EXTRA, encoding="utf-8") as handle:
        for line in handle:
            name = line.split("#", 1)[0].strip()
            if name:
                names.append(name)
    return names


def requires():
    with open(BASE, encoding="utf-8") as handle:
        base = json.load(handle)
    aliases = base.get("aliases", {})
    names = []
    for name in base["packages"]:
        names.extend(SPLIT.get(name, [aliases.get(name, name)]))
    seen = set(names)
    for name in read_extra():
        if name not in seen:
            names.append(name)
            seen.add(name)
    return names


def block(names):
    lines = [
        BEGIN + ": generated from package_specs/base.json + requires-extra",
        "# Run ./tenko base-requires after changing either file.",
    ]
    lines += ["Requires:   " + name for name in names]
    lines.append(END)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    with open(SPEC, encoding="utf-8") as handle:
        text = handle.read()
    if BEGIN not in text or END not in text:
        sys.exit("missing generated-requires markers in " + SPEC)

    start = text.index(BEGIN)
    stop = text.index(END) + len(END)
    new_text = text[:start] + block(requires()) + text[stop:]

    if args.check:
        if new_text != text:
            print("tenko-base requires are stale; run ./tenko base-requires",
                  file=sys.stderr)
            sys.exit(1)
        print("tenko-base requires are up to date (%d)" % len(requires()))
        return

    with open(SPEC, "w", encoding="utf-8") as handle:
        handle.write(new_text)
    print("updated %s (%d requires)" % (SPEC, len(requires())))


if __name__ == "__main__":
    main()
