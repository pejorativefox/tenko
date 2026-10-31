#!/usr/bin/env python3
"""Generate a static %files list from a built RPM.

The output is suitable for `%files -f <name>.filelist`.  It records every
path the current build installs, including implicitly-owned directories and
%config/%doc flags, so switching a spec from directory globs to the generated
list does not change package contents.

Usage:
    ./scripts/gen_filelist.py --rpm path/to/pkg.rpm \
        [--output package_specs/pkg/files/pkg.filelist] [--stdout]
"""

import argparse
import os
import subprocess
import sys

QUERY = "[%{FILENAMES}\\t%{FILEFLAGS:fflags}\\t%{FILEMODES:perms}\\n]"

# Directories that are owned by the filesystem/base layout rather than a
# package; never emit %dir for them.
SKIP_DIRS = {"/", "/usr", "/etc", "/var", "/var/lib", "/var/log", "/var/cache", "/var/run"}


def rpm_files(rpm):
    out = subprocess.check_output(
        ["rpm", "-qp", "--qf", QUERY, rpm], text=True
    )
    for line in out.splitlines():
        if not line.strip():
            continue
        path, flags, perms = line.split("\t")
        yield path, flags, perms


def render(entries):
    lines = []
    for path, flags, perms in sorted(entries):
        if os.path.basename(path) in (".build-id",):
            continue
        is_dir = perms.startswith("d")
        if is_dir:
            if path in SKIP_DIRS:
                continue
            lines.append("%dir " + path)
            continue
        prefix = ""
        # 'c' = config, 'n' = config(noreplace), 'd' = doc
        if "n" in flags:
            prefix = "%config(noreplace) "
        elif "c" in flags:
            prefix = "%config "
        elif "d" in flags:
            prefix = "%doc "
        lines.append(prefix + path)
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rpm", required=True, help="built RPM to inspect")
    parser.add_argument("--output", help="filelist path to write")
    parser.add_argument("--stdout", action="store_true", help="print instead of write")
    args = parser.parse_args()

    if not os.path.isfile(args.rpm):
        sys.exit("no such rpm: " + args.rpm)

    lines = render(list(rpm_files(args.rpm)))
    text = "\n".join(lines) + "\n"
    if args.stdout or not args.output:
        sys.stdout.write(text)
        return

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(text)
    print("{}: {} entries".format(args.output, len(lines)))


if __name__ == "__main__":
    main()
