#!/usr/bin/env python3
"""Bump package specs to the LFS/BLFS trunk versions.

For each package directory given on the command line this script:

1. looks the package up in the books (same logic as audit_versions.py);
2. reads the book's md5sum entity for it;
3. rewrites the ``sources`` file (md5, URL, filename) with the old version
   replaced by the book version, downloads the tarball into
   ``~/rpmbuild/SOURCES`` and verifies the book md5;
4. updates ``Version:`` in the spec, resets ``Release`` to 1 and adds a
   changelog entry.

If the download or the checksum fails nothing is written for that package and
the reason is reported.  A version bump alone does not prove a spec still
builds: rebuild and regenerate the static ``%files`` lists afterwards.

Usage:
    scripts/bump_to_book.py --dry-run wget nss
    scripts/bump_to_book.py wget nss
"""

import argparse
import datetime
import glob
import hashlib
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")
LFS = os.path.join(HOME, "repos", "lfs")
BLFS = os.path.join(HOME, "repos", "blfs")
SOURCES = os.path.join(HOME, "rpmbuild", "SOURCES")

ENTITY_RE = re.compile(r'<!ENTITY\s+([\w.+-]+)\s+"([^"]*)"')
REF_RE = re.compile(r"&([\w.+-]+);")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import audit_versions  # noqa: E402


def entity_map():
    """Every entity defined in the two books, with the defining file."""
    ents, where = {}, {}
    paths = [os.path.join(LFS, "packages.ent")]
    paths += [os.path.join(BLFS, "packages.ent"), os.path.join(BLFS, "general.ent")]
    paths += glob.glob(os.path.join(BLFS, "**", "*.xml"), recursive=True)
    for path in paths:
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        for name, value in ENTITY_RE.findall(text):
            ents.setdefault(name, value)
            where.setdefault(name, path)
    return ents, where


def spec_path(pkg):
    d = os.path.join(ROOT, "package_specs", pkg)
    spec = os.path.join(d, pkg + ".spec")
    if os.path.isfile(spec):
        return spec
    found = sorted(glob.glob(os.path.join(d, "*.spec")))
    if len(found) != 1:
        raise SystemExit("cannot pick a spec for %s: %s" % (pkg, found))
    return found[0]


def read_spec(spec):
    text = open(spec, encoding="utf-8", errors="replace").read()
    name = re.search(r"^Name:\s*(\S+)", text, re.M).group(1)
    ver = re.search(r"^Version:\s*(\S+)", text, re.M).group(1)
    rel = re.search(r"^Release:\s*(\S+)", text, re.M)
    return text, name, ver, (rel.group(1) if rel else None)


def download(url, want_md5, filename):
    tasks = []
    for name in {filename, os.path.basename(url)}:
        tasks.append(name)
    for name in tasks:
        path = os.path.join(SOURCES, name)
        if os.path.isfile(path):
            got = hashlib.md5(open(path, "rb").read()).hexdigest()
            if got == want_md5:
                return name, "cached"
            os.unlink(path)
        try:
            subprocess.run(
                ["curl", "-fsSL", "--retry", "3", "-o", path + ".part", url],
                check=True,
            )
        except subprocess.CalledProcessError:
            if os.path.exists(path + ".part"):
                os.unlink(path + ".part")
            continue
        got = hashlib.md5(open(path + ".part", "rb").read()).hexdigest()
        if got != want_md5:
            os.unlink(path + ".part")
            return None, "md5 %s != book %s (%s)" % (got, want_md5, url)
        os.replace(path + ".part", path)
        return name, "downloaded"
    return None, "download failed (%s)" % url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date", default=None, help="changelog date (YYYY-MM-DD)")
    ap.add_argument("packages", nargs="+")
    args = ap.parse_args()
    day = args.date or datetime.date.today().strftime("%a %b %d %Y")

    book = audit_versions.book_versions()
    ents, where = entity_map()
    changed, skipped = [], []

    for pkg in args.packages:
        try:
            spec = spec_path(pkg)
        except SystemExit as exc:
            skipped.append((pkg, str(exc)))
            continue
        text, name, ver, rel = read_spec(spec)
        hit = book.get(audit_versions.norm(name))
        if not hit:
            skipped.append((pkg, "no book entry"))
            continue
        bver, src, entity = hit
        if audit_versions.vcmp(ver, bver) >= 0:
            skipped.append((pkg, "already %s (book %s)" % (ver, bver)))
            continue
        md5_ent = entity[: -len("-version")] + "-md5sum"
        want = ents.get(md5_ent)
        if not want:
            skipped.append((pkg, "book has no %s" % md5_ent))
            continue
        want = audit_versions.resolve(want, ents)

        srcfile = os.path.join(os.path.dirname(spec), "sources")
        if not os.path.isfile(srcfile):
            skipped.append((pkg, "no sources file"))
            continue
        lines = [l.rstrip("\n") for l in open(srcfile) if l.strip()]
        new_lines, ok, why = [], True, ""
        for line in lines:
            parts = line.split()
            if len(parts) < 2 or not parts[1].startswith("http"):
                new_lines.append(line)
                continue
            old_md5, url = parts[0], parts[1]
            fname = parts[2] if len(parts) > 2 else os.path.basename(url)
            if ver not in url:
                new_lines.append(line)
                continue
            url2 = url.replace(ver, bver)
            fname2 = fname.replace(ver, bver)
            new_md5 = want if len(lines) == 1 else old_md5
            if len(lines) > 1:
                skipped.append((pkg, "multiple sources; update by hand"))
                ok = False
                break
            got, how = (None, "dry-run")
            if not args.dry_run:
                got, how = download(url2, new_md5, fname2)
                if not got:
                    ok, why = False, how
                    break
            new_lines.append("%s %s %s" % (new_md5, url2, fname2))
        if not ok:
            skipped.append((pkg, why or "unsupported sources layout"))
            continue
        if not new_lines:
            skipped.append((pkg, "nothing to rewrite"))
            continue

        if args.dry_run:
            print("%-24s %s -> %s  (would download %s, md5 %s)" % (pkg, ver, bver, new_lines[-1].split()[1], want))
            changed.append((pkg, ver, bver))
            continue

        open(srcfile, "w").write("\n".join(new_lines) + "\n")
        text = re.sub(r"^Version:\s*\S+", "Version:    " + bver, text, count=1, flags=re.M)
        if rel is not None:
            text = re.sub(r"^Release:\s*\S+", "Release:    1", text, count=1, flags=re.M)
        entry = "* %s browneye <build@browneye.invalid> %s-1\n- Sync with %s r13.1\n\n" % (
            day, bver, src.upper())
        text = text.replace("%changelog\n", "%changelog\n" + entry, 1)
        open(spec, "w").write(text)
        changed.append((pkg, ver, bver))
        print("%-24s %s -> %s  ok" % (pkg, ver, bver))

    for pkg, why in skipped:
        print("%-24s skip: %s" % (pkg, why), file=sys.stderr)
    print("\n%d bumped, %d skipped" % (len(changed), len(skipped)))
    return 0 if changed or not skipped else 1


if __name__ == "__main__":
    sys.exit(main())
