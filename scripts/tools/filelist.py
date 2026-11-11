#!/usr/bin/env python3
"""Generate a static %files list from a built RPM or an installed buildroot.

The list records every path the package installs, including the directories
it owns (%dir) and, from an RPM, the %config/%doc flags, so switching a spec
from globs to the generated list does not change package contents.

Sources (pick one):
    --rpm PKG.rpm         read paths and flags from a built RPM
    --tree BUILDROOT      walk an installed buildroot (rpmbuild -bi, or
                          make install DESTDIR=...) after a version bump

Destinations:
    (default)             print to stdout
    --output FILE         write a `%files -f` list, e.g.
                          package_specs/pkg/files/pkg.filelist
    --spec SPEC           replace the spec's single %files section (prints a
                          diff; add --write to update the spec in place)

Usage:
    tenko filelist --rpm build/x/RPMS/x86_64/flac-1.5.0-1.x86_64.rpm \\
        --output package_specs/flac/files/flac.filelist
    tenko filelist --tree build/x/build/flac/BUILDROOT/flac-1.5.0-1.x86_64 \\
        --spec package_specs/flac/flac.spec --write
"""

import argparse
import os
import subprocess
import sys

RPM_QUERY = "[%{FILENAMES}\\t%{FILEFLAGS:fflags}\\t%{FILEMODES:perms}\\n]"

# Directories owned by the filesystem layout rather than a package; never
# emit %dir for them.
SKIP_DIRS = {"/", "/usr", "/etc", "/var", "/var/lib", "/var/log",
             "/var/cache", "/var/run"}


def quote_path(path):
    if " " in path or "\t" in path:
        return '"' + path.replace('"', '\\"') + '"'
    return path


def from_rpm(rpm):
    """Yield (path, is_dir, flags) for every file in a built RPM."""
    out = subprocess.check_output(["rpm", "-qp", "--qf", RPM_QUERY, rpm],
                                  text=True)
    for line in out.splitlines():
        if line.strip():
            path, flags, perms = line.split("\t")
            yield path, perms.startswith("d"), flags


def from_tree(root):
    """Yield (path, is_dir, flags) for every entry under a buildroot."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        rel = os.path.relpath(dirpath, root)
        base = "" if rel == "." else "/" + rel
        for name in dirnames:
            # os.walk does not descend into symlinked directories; the link
            # itself is a file entry.
            is_link = os.path.islink(os.path.join(dirpath, name))
            yield base + "/" + name, not is_link, ""
        for name in filenames:
            yield base + "/" + name, False, ""


def render(entries, dirs=True):
    lines = []
    for path, is_dir, flags in sorted(set(entries)):
        if ".build-id" in path.split("/"):
            continue
        if is_dir:
            if dirs and path not in SKIP_DIRS:
                lines.append("%dir " + quote_path(path))
            continue
        prefix = ""
        # 'n' = config(noreplace), 'c' = config, 'd' = doc
        if "n" in flags:
            prefix = "%config(noreplace) "
        elif "c" in flags:
            prefix = "%config "
        elif "d" in flags:
            prefix = "%doc "
        lines.append(prefix + quote_path(path))
    return lines


def replace_spec_files(spec, lines, write):
    with open(spec, encoding="utf-8") as handle:
        text = handle.read().splitlines()
    starts = [i for i, line in enumerate(text) if line.startswith("%files")]
    if len(starts) != 1:
        sys.exit("error: {} has {} %files sections; use --output for "
                 "multi-package specs".format(spec, len(starts)))
    start = starts[0]
    end = next((i for i in range(start + 1, len(text))
                if text[i].startswith("%")), len(text))
    old = text[start:end]
    new = [text[start]] + lines + [""]
    print("--- {}: {} entries (was {})".format(
        spec, len(lines), sum(1 for line in old[1:] if line.strip())))
    for line in old:
        if line and line not in new:
            print("- " + line)
    for line in new:
        if line and line not in old:
            print("+ " + line)
    if write:
        text[start:end] = new
        with open(spec, "w", encoding="utf-8") as handle:
            handle.write("\n".join(text) + "\n")
        print("wrote " + spec)


def main():
    parser = argparse.ArgumentParser(
        prog="tenko filelist", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--rpm", help="built RPM to read")
    source.add_argument("--tree", help="installed buildroot to walk")
    dest = parser.add_mutually_exclusive_group()
    dest.add_argument("--output", help="filelist to write")
    dest.add_argument("--spec", help="spec whose single %%files section to replace")
    parser.add_argument("--write", action="store_true",
                        help="with --spec, update the spec in place")
    parser.add_argument("--no-dirs", action="store_true",
                        help="omit %%dir entries")
    args = parser.parse_args()

    if args.rpm:
        if not os.path.isfile(args.rpm):
            sys.exit("no such rpm: " + args.rpm)
        entries = list(from_rpm(args.rpm))
    else:
        if not os.path.isdir(args.tree):
            sys.exit("no such buildroot: " + args.tree)
        entries = list(from_tree(args.tree))
    lines = render(entries, dirs=not args.no_dirs)
    if not lines:
        sys.exit("error: no files found")

    if args.spec:
        replace_spec_files(args.spec, lines, args.write)
    elif args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        print("{}: {} entries".format(args.output, len(lines)))
    else:
        sys.stdout.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
