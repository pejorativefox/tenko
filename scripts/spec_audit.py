#!/usr/bin/env python3
"""Audit the specs against the books and the published repository.

The main input is a repodata primary.xml.zst from the published repository;
it supplies both the RPM names and the source-package versions, so no local
RPM tree is needed.

    curl -sO .../repodata/repomd.xml
    curl -s -o primary.xml.zst .../repodata/<hash>-primary.xml.zst
    python3 scripts/spec_audit.py --primary primary.xml.zst

The report it prints is the data behind spec-audit.md.  Book versions come
from the local ~/repos/lfs and ~/repos/blfs checkouts: every *-version
entity, LFS first (so name collisions such as xml-parser prefer the LFS
chapter-8 version).  Packages whose page hard-codes its version instead of
using an entity (htop, gstreamer, several binary bundles) show up as
NO-BOOK; that means "not comparable by entity", not "not in the books".
"""
import argparse
import glob
import io
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import audit_versions as av  # noqa: E402

NS = {"c": "http://linux.duke.edu/metadata/common",
      "rpm": "http://linux.duke.edu/metadata/rpm"}
H = os.path.expanduser("~")

# book entities that are known under a different name than our spec
ALIASES = {"gnupg": "gnupg2", "freetype": "freetype2", "icu4c": "icu",
           "libglu": "glu", "python-setuptools": "setuptools",
           "gtkmm": "gtkmm3", "gtk+": "gtk3", "webp": "libwebp"}


def repo_data(path):
    data = subprocess.run(["zstd", "-dc", path], check=True,
                          stdout=subprocess.PIPE).stdout
    pkgs, sources = {}, {}
    for _ev, el in ET.iterparse(io.BytesIO(data)):
        if not el.tag.endswith("}package"):
            continue
        name = el.find("c:name", NS).text
        v = el.find("c:version", NS)
        srpm = el.find("c:format/rpm:sourcerpm", NS)
        pkgs[name] = (v.get("ver"), v.get("rel"))
        if srpm is not None:
            m = re.match(r"(.+)-([^-]+)-([^-]+)\.src\.rpm$", srpm.text)
            if m:
                sources[m.group(1)] = (m.group(2), m.group(3))
        el.clear()
    return pkgs, sources


def book_versions():
    ents_re = re.compile(r'<!ENTITY\s+([A-Za-z0-9_.+-]+)\s+"([^"]*)"\s*>')
    ref_re = re.compile(r"&([A-Za-z0-9_.+-]+);")
    paths = [H + "/repos/lfs/packages.ent"]
    # every entity file in the BLFS root: general.ent, packages.ent and the
    # per-chapter files (gnome.ent, xfce.ent, ...), which hold the GNOME and
    # desktop package versions
    paths += sorted(glob.glob(H + "/repos/blfs/*.ent"))
    paths += [p for p in glob.glob(H + "/repos/blfs/**/*.xml", recursive=True)
              if "/archive/" not in p]
    ents = {}
    for path in paths:
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        for name, value in ents_re.findall(text):
            ents.setdefault(name, value)

    def resolve(value, depth=0):
        if depth > 12:
            return value
        return ref_re.sub(
            lambda m: resolve(ents.get(m.group(1), m.group(0)), depth + 1),
            value)

    out = {}
    for name, value in ents.items():
        if not name.endswith("-version"):
            continue
        key = av.norm(name[:-8])
        if key in out:  # LFS is parsed first and wins collisions
            continue
        value = resolve(value)
        if key == "sqlite" and re.fullmatch(r"\d{7,}", value):
            value = "{}.{}.{}.{}".format(value[0], value[1:3], value[3:5],
                                         value[5:]).rstrip(".0")
        out[key] = value
    return out


def spec_info(path):
    name = ver = None
    subs, patches = set(), []
    for line in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"^Name:\s*(\S+)", line)
        if m and not name:
            name = m.group(1)
        m = re.match(r"^Version:\s*(\S+)", line)
        if m and not ver:
            ver = m.group(1)
        m = re.match(r"^%package(?:\s+-n\s+|\s+)(\S+)", line)
        if m:
            subs.add(m.group(1).rstrip(","))
        m = re.match(r"^Patch\d*:\s*(\S+)", line)
        if m:
            patches.append(m.group(1))
    return name, ver, subs, patches


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", required=True,
                    help="repodata primary.xml.zst of the published repo")
    args = ap.parse_args()

    _pkgs, sources = repo_data(args.primary)
    book = book_versions()

    def lookup(name):
        key = av.norm(name)
        hit = book.get(key)
        if not hit and name in ALIASES:
            hit = book.get(av.norm(ALIASES[name]))
        return hit

    rows = []
    for spec in sorted(glob.glob(os.path.join(ROOT, "package_specs", "*", "*.spec"))):
        d = os.path.basename(os.path.dirname(spec))
        name, ver, subs, patches = spec_info(spec)
        if not name or not ver:
            continue
        shipped = sources.get(name, (None,))[0] == ver or any(
            s in sources and sources[s][0] == ver for s in subs)
        bver = lookup(name)
        if bver:
            c = av.vcmp(ver, bver)
            status = "OK" if c == 0 else ("BELOW" if c < 0 else "ABOVE")
        else:
            status = "NO-BOOK"
        sfile = os.path.join(ROOT, "package_specs", d, "sources")
        bad_src = None
        if os.path.exists(sfile):
            for line in open(sfile, encoding="utf-8", errors="replace"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    base = os.path.basename(parts[1])
                    digits = re.sub(r"[^0-9]", "", ver)
                    if not (digits and digits in re.sub(r"[^0-9]", "", base)
                            or ver in base):
                        bad_src = base
                break
        missing = []
        for p in patches:
            # Patch lines may use %{name}/%{version}; expand them so a
            # vendored patch is not reported missing under its literal name.
            expanded = p.replace("%{name}", name or "").replace(
                "%{version}", ver or "")
            sref = open(sfile).read() if os.path.exists(sfile) else ""
            if os.path.exists(
                    os.path.join(ROOT, "package_specs", d, "files", expanded)):
                continue
            if expanded in sref or p in sref:
                continue
            missing.append(p)
        rows.append(dict(dir=d, name=name, ver=ver, shipped=shipped,
                         status=status, bver=bver, bad_src=bad_src,
                         missing=missing,
                         has_sources=os.path.exists(sfile),
                         nosources=os.path.exists(
                             os.path.join(ROOT, "package_specs", d, "nosources"))))

    shipped = [r for r in rows if r["shipped"]]
    unbuilt = [r for r in rows if not r["shipped"]]

    def counts(group):
        out = {}
        for r in group:
            out[r["status"]] = out.get(r["status"], 0) + 1
        return out

    print("specs:", len(rows), "shipped:", len(shipped), "unbuilt:", len(unbuilt))
    print("source packages in repo:", len(sources))
    print("shipped:", counts(shipped))
    print("unbuilt:", counts(unbuilt))
    print("\nshipped BELOW book:",
          [(r["name"], r["ver"], r["bver"]) for r in shipped if r["status"] == "BELOW"])
    print("shipped ABOVE book:",
          [(r["name"], r["ver"], r["bver"]) for r in shipped if r["status"] == "ABOVE"])
    print("unbuilt ABOVE book:",
          [(r["name"], r["ver"], r["bver"]) for r in unbuilt if r["status"] == "ABOVE"])
    print("\nsources/version mismatches (review manually):")
    for r in shipped + unbuilt:
        if r["bad_src"]:
            print(f"  {r['name']}: spec {r['ver']} source {r['bad_src']}")
    print("\nmissing patches:",
          [(r["name"], r["missing"]) for r in rows if r["missing"]] or "none")
    print("specs without sources/nosources:",
          [r["dir"] for r in rows if not r["has_sources"] and not r["nosources"]]
          or "none")
    todo_s = todo_d = 0
    for spec in glob.glob(os.path.join(ROOT, "package_specs", "*", "*.spec")):
        t = open(spec, encoding="utf-8", errors="replace").read()
        if re.search(r"^Summary:\s*TODO\s*$", t, re.M):
            todo_s += 1
        if re.search(r"^%description\s*\n.*?TODO", t, re.M | re.S):
            todo_d += 1
    print(f"TODO metadata: summary={todo_s} description={todo_d}")
    print("\nshipped no-book:", " ".join(sorted(r["name"] for r in shipped
                                                if r["status"] == "NO-BOOK")))
    print("\nunbuilt no-book:", " ".join(sorted(r["name"] for r in unbuilt
                                                if r["status"] == "NO-BOOK")))


if __name__ == "__main__":
    main()
