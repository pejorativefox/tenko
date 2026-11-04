#!/usr/bin/env python3
"""Resolve a package's download URL/md5 from the local LFS/BLFS books.

Usage:
    scripts/book_source.py <package> [--download DIR]

Prints "md5 url" on stdout.  The package name may be the book entity name
(e.g. xz, glib2, libX11); the spec name is tried first.  With --download the
source is fetched into DIR (default ~/rpmbuild/SOURCES) and the md5 of the
downloaded file is verified.
"""
import argparse
import glob
import os
import re
import subprocess
import sys

HOME = os.path.expanduser("~")
LFS = os.path.join(HOME, "repos", "lfs")
BLFS = os.path.join(HOME, "repos", "blfs")
ENTITY_RE = re.compile(r'<!ENTITY\s+([A-Za-z0-9_.+-]+)\s+"([^"]*)"\s*>')
REF_RE = re.compile(r"&([A-Za-z0-9_.+-]+);")


def load():
    paths = [os.path.join(LFS, "packages.ent"), os.path.join(LFS, "general.ent")]
    paths += [os.path.join(BLFS, "packages.ent"), os.path.join(BLFS, "general.ent")]
    paths += glob.glob(os.path.join(BLFS, "**", "*.xml"), recursive=True)
    paths += glob.glob(os.path.join(BLFS, "**", "*.ent"), recursive=True)
    ents = {}
    for path in paths:
        if "/archive/" in path:
            continue
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        for name, value in ENTITY_RE.findall(text):
            ents.setdefault(name, value)
    return ents


def resolve(value, ents, depth=0):
    if depth > 15:
        return value
    return REF_RE.sub(lambda m: resolve(ents.get(m.group(1), m.group(0)), ents, depth + 1), value)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("package")
    ap.add_argument("--download")
    args = ap.parse_args()
    ents = load()

    names = [args.package, args.package.lower()]
    url_name = md5_name = None
    lower = {k.lower(): k for k in ents}
    for n in names:
        for suffix in ("-url", "-download-http"):
            key = (n + suffix).lower()
            if key in lower:
                url_name = lower[key]
                break
        if url_name:
            md5_name = n + "-md5" if n + "-md5" in ents else n + "-md5sum"
            break
    if not url_name:
        sys.exit("no download entity for " + args.package)
    url = resolve(ents[url_name], ents)
    md5 = resolve(ents.get(md5_name, ""), ents) if md5_name else ""
    print(md5, url)
    if args.download:
        dest = os.path.join(args.download, os.path.basename(url))
        subprocess.run(["curl", "-fL", "--retry", "3", "-C", "-", "-o", dest, url], check=True)
        if md5:
            got = subprocess.check_output(["md5sum", dest], text=True).split()[0]
            print(("ok " if got == md5 else "MISMATCH {} != {} ".format(got, md5)) + dest, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
