#!/usr/bin/env python3
"""Sync Browneye specs with the current BLFS book (r13.1 trunk).

Reads the BLFS book entities (version + md5sum + download-URL) from the
~/repos/blfs checkout, compares each target spec's Version/Source0 and the
sources file against it, and mechanically:

  * bumps ``Version:`` (and ``Summary:``/``License:`` when provided)
  * rewrites ``Source0:`` to the upstream tarball basename
  * updates the matching line in the ``sources`` file (md5 + URL)
  * prepends a %changelog entry when one exists
  * with --convert-files, replaces a literal ``%files`` list with the
    static ``%files -f %{_sourcedir}/<spec>.filelist`` form the base set
    uses (the list itself is generated from BUILDROOT at build time)

Anything else (configure changes, patches, subpackage files) is left alone.

Usage:
    python3 scripts/sync_blfs_spec.py               # report only
    python3 scripts/sync_blfs_spec.py --write       # apply
    python3 scripts/sync_blfs_spec.py --stage       # fetch tarballs into
                                                    # ~/rpmbuild/SOURCES
    python3 scripts/sync_blfs_spec.py <package>...  # subset
"""

import argparse
import concurrent.futures
import datetime
import hashlib
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(ROOT, "package_specs")
SOURCES_DIR = os.path.expanduser("~/rpmbuild/SOURCES")
BOOK = os.path.expanduser("~/repos/blfs")

ENTITY_RE = re.compile(r"<!ENTITY\s+([A-Za-z0-9_.+%-]+)\s+\"([^\"]*)\"\s*>")
REF_RE = re.compile(r"&([A-Za-z0-9_.+-]+);")

# spec directory name -> entity stem used by the book (case matters)
ENTITY_NAMES = {
    "libxaw": "libXaw",
    "libxv": "libXv",
    "libxpm": "libXpm",
}

# tarball subdirectory under x.org/pub/individual for packages that are not
# in the standard app/ or lib/ trees
UTIL_PACKAGES = {"bdftopcf": "util"}

# Pages that carry each target's entities (order = precedence on conflicts).
BOOK_FILES = [
    "x/installing/x7app.xml",
    "x/installing/x7lib.xml",
    "x/installing/x7font.xml",
    "x/installing/x7legacy.xml",
    "x/installing/xbitmaps.xml",
    "x/installing/xcursor-themes.xml",
    "x/installing/luit.xml",
    "x/installing/xterm.xml",
    "packages.ent",
]

# Per-package Summary/License overrides written into the spec by --write.
META = {
    "bdftopcf": ("Convert X11 BDF bitmap fonts into PCF format", "MIT"),
    "xbitmaps": ("Core X11 bitmap image data", "MIT"),
    "xcursor-themes": ("Default X11 cursor themes", "MIT"),
    "libxaw": ("Athena widget set based on the X Toolkit Intrinsics", "MIT"),
    "libxv": ("X11 Video extension library (Xv)", "MIT"),
    "libxpm": ("X11 Pixmap (XPM) library", "MIT"),
    "luit": ("Encoding converter for X11 terminals", "MIT"),
    "xterm": ("X11 terminal emulator", "MIT"),
    "sessreg": ("Register user sessions in utmp/wtmp", "MIT"),
    "setxkbmap": ("Set the X11 keyboard layout", "MIT"),
    "smproxy": ("X11 session manager proxy", "MIT"),
    "xcmsdb": ("Query and modify the X11 colour raster database", "MIT"),
    "xcursorgen": ("Generate X11 cursor files from PNGs", "MIT"),
    "xdpyinfo": ("Display information about an X server", "MIT"),
    "xdriinfo": ("Query DRI drivers on an X server", "MIT"),
    "xev": ("Print the content of X11 events", "MIT"),
    "xgamma": ("Set the X11 gamma correction", "MIT"),
    "xinput": ("Configure and test X11 input devices", "MIT"),
    "xkbevd": ("X11 keyboard event daemon", "MIT"),
    "xkbutils": ("X11 keyboard utility programs", "MIT"),
    "xkill": ("Ask an X server to terminate a client", "MIT"),
    "xlsatoms": ("List interned X atoms", "MIT"),
    "xlsclients": ("List the clients connected to an X server", "MIT"),
    "xmessage": ("Display X11 text messages or question dialogs", "MIT"),
    "xpr": ("Print X11 window dumps", "MIT"),
    "xprop": ("Display window and font properties of an X server", "MIT"),
    "xrandr": ("Command line interface to the X11 RandR extension", "MIT"),
    "xrefresh": ("Refresh the X11 screen", "MIT"),
    "xsetroot": ("Set the X11 root window background and cursor", "MIT"),
    "xvinfo": ("Query the X11 Video extension (Xv)", "MIT"),
    "xwud": ("Display an X11 image dumped by xwd", "MIT"),
    "font-adobe-utopia-type1": ("Adobe Utopia Type1 fonts for X11", "MIT"),
    "font-bh-type1": ("Bigelow & Holmes Type1 fonts for X11", "MIT"),
    "font-ibm-type1": ("IBM Type1 fonts for X11", "MIT"),
    "font-misc-ethiopic": ("Unicode Ethiopic fonts (Abyssinica SIL-based)", "MIT"),
    "font-xfree86-type1": ("CrossUnicode Type1 fonts for X11", "MIT"),
    "font-ttf-unifont": ("GNU Unifont: bitmap+outline coverage of the Unicode code points", "OFL"),
    "font-terminus": ("Terminus console bitmap + TTF font family", "OFL"),
    "font-ubuntu-font-family": ("Ubuntu UI font family (TTF)", "NASA-Ubuntu-1.3"),
    "font-siji": ("A bitmap icon font for terminal fonts", "WTFPL"),
    "font-noto-cjk": ("Noto Sans/Serif CJK variable fonts", "OFL"),
}


def resolve(value, ents, depth=0):
    if depth > 8:
        return value
    return REF_RE.sub(lambda m: resolve(ents.get(m.group(1), m.group(0)),
                                        ents, depth + 1), value)


def load_entities():
    ents = {}
    for rel in BOOK_FILES:
        path = os.path.join(BOOK, rel)
        if not os.path.isfile(path):
            print("warning: missing book file {}".format(rel), file=sys.stderr)
            continue
        with open(path, encoding="utf-8", errors="replace") as fd:
            text = fd.read()
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        for key, value in ENTITY_RE.findall(text):
            ents.setdefault(key, value)
    return ents


def book_entry(pkg, ents):
    stem = ENTITY_NAMES.get(pkg, pkg)
    version = ents.get(stem + "-version")
    md5 = ents.get(stem + "-md5sum")
    if not version:
        return None
    url_ent = ents.get(stem + "-download-http")
    if url_ent:
        url = resolve(url_ent, ents)
    elif stem.startswith("lib"):
        url = ("https://www.x.org/pub/individual/lib/{}-{}.tar.xz"
               .format(stem, version))
    elif pkg in ("xbitmaps", "xcursor-themes"):
        url = ("https://www.x.org/pub/individual/data/{}-{}.tar.xz"
               .format(pkg, version))
    elif pkg.startswith("font-"):
        url = ("https://www.x.org/pub/individual/font/{}-{}.tar.xz"
               .format(pkg, version))
    elif pkg in UTIL_PACKAGES:
        url = ("https://www.x.org/pub/individual/util/{}-{}.tar.xz"
               .format(pkg, version))
    else:
        url = ("https://www.x.org/pub/individual/app/{}-{}.tar.xz"
               .format(pkg, version))
    return {"stem": stem, "version": version, "md5": md5, "url": url}


def spec_path(pkg):
    return os.path.join(SPECS, pkg, pkg + ".spec")


def read_sources(pkg):
    path = os.path.join(SPECS, pkg, "sources")
    if not os.path.isfile(path):
        return []
    rows = []
    for line in open(path, encoding="utf-8"):
        fields = line.split()
        if fields:
            rows.append(fields)
    return rows


def rewrite_spec(pkg, book, write=False, convert_files=False):
    path = spec_path(pkg)
    if not os.path.isfile(path):
        return "{} spec missing task".format(pkg)
    text = open(path, encoding="utf-8").read()
    original = text
    notes = []

    version = book["version"]
    tarball = os.path.basename(book["url"])

    text = re.sub(r"^Version:\s*\S+\s*$",
                  "Version:    {}".format(version), text, count=1,
                  flags=re.M)
    if not re.search(r"^Source0:\s*{}\s*$".format(re.escape(tarball)),
                     text, flags=re.M):
        text = re.sub(r"^Source0:\s*.+?$", "Source0:    {}".format(tarball),
                      text, count=1, flags=re.M)
    if convert_files:
        block = re.compile(r"^\%files.*?(?=^\%changelog|\Z)", flags=re.M | re.S)
        files_block = block.search(text)
        if files_block and ".filelist" not in files_block.group(0):
            replacement = "%files -f %{{_sourcedir}}/{}.filelist\n".format(pkg)
            text = (text[:files_block.start()]
                    + replacement
                    + text[files_block.end():])
    meta = META.get(pkg)
    if meta:
        if re.search(r"^Summary:\s*(TODO)?\s*$", text, flags=re.M):
            text = re.sub(r"^Summary:\s*(TODO)?\s*$",
                          "Summary:    {}".format(meta[0]), text, count=1,
                          flags=re.M)
    if write and text != original:
        with open(path, "w", encoding="utf-8") as fd:
            fd.write(text)

    # sources file: these dormant packages carry one current tarball each;
    # stale rows would only confuse the staging helper.
    rows = read_sources(pkg)
    keep = [[book["md5"], book["url"]]] if book["md5"] else rows
    changed = keep != rows
    src_path = os.path.join(SPECS, pkg, "sources")
    if write and changed:
        with open(src_path, "w", encoding="utf-8") as fd:
            for row in keep:
                fd.write(" ".join(row) + "\n")

    # changelog entry only where one is already maintained
    if write:
        cl = re.search(r"^\%changelog\s*\n((?:\* .*\n.*\n)+)", text, flags=re.M)
        if cl and "- Sync with BLFS r13.1" not in cl.group(1).split("\n")[0]:
            today = datetime.date(2026, 11, 2)
            head, rest = cl.group(1).split("\n", 1)
            entry = ("* {} browneye <build@browneye.invalid> {}\n"
                     "- Sync with BLFS r13.1 ({} {})\n"
                     .format(today.strftime("%a %b %d %Y"), version, pkg,
                             book["version"]))
            text = (text[:cl.start(1)] + entry + head + "\n" + rest
                    + text[cl.end():])
            with open(path, "w", encoding="utf-8") as fd:
                fd.write(text)
    elif text != original:
        notes.append("spec dirty")

    status = []
    detail = "book {}:{}".format(book["stem"], version)
    if book["md5"] and not any(row[0] == book["md5"] for row in keep):
        status.append("sources-outdated")
    elif not book["md5"]:
        status.append("book-md5-missing")
    return "{} {}{}: {}".format(pkg, status and "[" + ",".join(status) + "] ",
                                detail, "; ".join(notes) or "ok")


def stage_tarballs(entries, workers=12):
    os.makedirs(SOURCES_DIR, exist_ok=True)

    def fetch(job):
        pkg, book = job
        out = os.path.join(SOURCES_DIR, os.path.basename(book["url"]))
        if os.path.isfile(out):
            md5 = hashlib.md5()
            with open(out, "rb") as fd:
                for chunk in iter(lambda: fd.read(1 << 20), b""):
                    md5.update(chunk)
            return "{} cached {}".format(pkg, "ok"
                                         if md5.hexdigest() == book["md5"]
                                         else "MD5 MISMATCH")
        rc = subprocess.run(["curl", "-fsSL", "-o", out + ".part",
                             book["url"]])
        if rc.returncode != 0:
            try:
                os.remove(out + ".part")
            except OSError:
                pass
            return "{} fetch FAILED".format(pkg)
        md5 = hashlib.md5()
        with open(out + ".part", "rb") as fd:
            for chunk in iter(lambda: fd.read(1 << 20), b""):
                md5.update(chunk)
        if md5.hexdigest() != book["md5"]:
            os.remove(out + ".part")
            return "{} md5 MISMATCH".format(pkg)
        os.replace(out + ".part", out)
        return "{} staged {}".format(pkg, os.path.basename(out))

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        for line in pool.map(fetch, entries):
            print(line)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packages", nargs="*")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--stage", action="store_true",
                        help="also fetch tarballs into ~/rpmbuild/SOURCES")
    parser.add_argument("--convert-files", action="store_true")
    args = parser.parse_args(argv)

    ents = load_entities()
    order = ["x7app", "x7lib", "x7legacy", "xbitmaps", "xcursor-themes",
             "luit", "xterm"]
    packages = args.packages or list(META)
    entries = []
    for pkg in sorted(packages):
        book = book_entry(pkg, ents)
        if not book:
            print("{}: no book entities — needs a manual sync".format(pkg))
            continue
        entries.append((pkg, book))
        print(rewrite_spec(pkg, book, write=args.write,
                           convert_files=args.convert_files))
    if args.stage:
        stage_tarballs(entries)
    return 0


if __name__ == "__main__":
    sys.exit(main())
