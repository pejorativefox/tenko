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


ALIASES = {"libglu": "glu", "cairomm": "cairomm10", "gnupg": "gnupg2",
           "gstreamer": "gstreamer10", "gstpluginsbase": "gst10pluginsbase",
           "freetype": "freetype2", "icu4c": "icu",
           "python-flit-core": "flit-core",
           "python-markupsafe": "markupsafe",
           "python-setuptools": "setuptools"}

MD5_SUFFIXES = ("-md5sum", "-md5", "-http-md5sum", "-download-md5sum")
URL_SUFFIXES = ("-download-http", "-url", "-download-ftp")


def entity_map():
    """Every entity defined in the two books, with the defining file."""
    ents, where, byfile = {}, {}, {}
    paths = [os.path.join(LFS, "packages.ent")]
    paths += [os.path.join(BLFS, "packages.ent"), os.path.join(BLFS, "general.ent")]
    paths += glob.glob(os.path.join(LFS, "**", "*.xml"), recursive=True)
    paths += glob.glob(os.path.join(BLFS, "*.ent"))
    paths += [p for p in glob.glob(os.path.join(BLFS, "**", "*.xml"), recursive=True)
              if os.sep + "archive" + os.sep not in p]
    for path in paths:
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        for name, value in ENTITY_RE.findall(text):
            # The book sometimes defines the same entity in a "-3" page
            # (e.g. libsigc++ and libsigc++3); keep the first definition for
            # the global map but also remember per-file definitions so the
            # URL is read from the page that owns the checksum.
            ents.setdefault(name, value)
            where.setdefault(name, path)
            byfile.setdefault(path, {})[name] = value
    return ents, where, byfile


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


def book_artifacts(stem, bver, ents, byfile):
    """Return (md5, url) from the book page that matches *bver*.

    A few BLFS pages reuse the same entity names for different major
    versions (libsigc++ 2.x and 3.x both define libsigc-md5sum), so the
    global map can point at the wrong checksum.  Prefer a page whose
    resolved download URL names the requested version.
    """
    fallback = None
    for local in byfile.values():
        merged = dict(ents)
        merged.update(local)
        for suffix in MD5_SUFFIXES:
            if stem + suffix not in local:
                continue
            md5 = audit_versions.resolve(local[stem + suffix], merged)
            url = None
            for usuffix in URL_SUFFIXES:
                raw = local.get(stem + usuffix)
                if not raw:
                    continue
                candidate = audit_versions.resolve(raw, merged).strip()
                if candidate.startswith("http"):
                    url = candidate
                    break
            if url and bver in url:
                return md5, url
            if fallback is None:
                fallback = (md5, url)
            break
    return fallback or (None, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date", default=None, help="changelog date (YYYY-MM-DD)")
    ap.add_argument("packages", nargs="+")
    args = ap.parse_args()
    day = args.date or datetime.date.today().strftime("%a %b %d %Y")

    book = audit_versions.book_versions()
    ents, where, byfile = entity_map()
    changed, skipped = [], []

    for pkg in args.packages:
        try:
            spec = spec_path(pkg)
        except SystemExit as exc:
            skipped.append((pkg, str(exc)))
            continue
        text, name, ver, rel = read_spec(spec)
        key = audit_versions.norm(name)
        hit = book.get(ALIASES.get(key, key))
        if not hit:
            skipped.append((pkg, "no book entry"))
            continue
        bver, src, entity = hit
        if audit_versions.vcmp(ver, bver) >= 0:
            skipped.append((pkg, "already %s (book %s)" % (ver, bver)))
            continue
        stem = entity[: -len("-version")]
        want, book_url = book_artifacts(stem, bver, ents, byfile)
        if not want:
            skipped.append((pkg, "book has no checksum for %s" % stem))
            continue

        srcfile = os.path.join(os.path.dirname(spec), "sources")
        if not os.path.isfile(srcfile):
            skipped.append((pkg, "no sources file"))
            continue
        lines = [l.rstrip("\n") for l in open(srcfile) if l.strip()]
        new_lines, ok, why = [], True, ""
        versioned = [l for l in lines
                     if len(l.split()) >= 2 and l.split()[1].startswith("http")
                     and ver in l.split()[1]]
        if len(versioned) > 1:
            skipped.append((pkg, "several versioned sources; update by hand"))
            continue
        for line in lines:
            parts = line.split()
            if len(parts) < 2 or not parts[1].startswith("http"):
                new_lines.append(line)
                continue
            old_md5, url = parts[0], parts[1]
            fname = parts[2] if len(parts) > 2 else os.path.basename(url)
            if ver not in url:
                # Patches and side sources stay untouched.
                new_lines.append(line)
                continue
            got, how, url2, fname2 = None, "dry-run", None, None
            candidates = []
            if book_url:
                candidates.append(book_url)
            candidates.append(url.replace(ver, bver))
            if args.dry_run:
                url2 = candidates[0]
                fname2 = fname.replace(ver, bver)
            else:
                for cand in candidates:
                    url2 = cand
                    fname2 = os.path.basename(cand.split("?")[0])
                    if not fname2 or fname2 == "download":
                        fname2 = fname.replace(ver, bver)
                    got, how = download(url2, want, fname2)
                    if got:
                        break
                if not got:
                    ok, why = False, how
                    break
            new_lines.append("%s %s %s" % (want, url2, fname2))
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
