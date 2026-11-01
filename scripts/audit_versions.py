#!/usr/bin/env python3
"""Compare every local RPM/spec version against the LFS/BLFS book versions.

Usage: python3 scripts/audit_versions.py [--rpm-dir DIR]
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")
LFS = os.path.join(HOME, "repos", "lfs")
BLFS = os.path.join(HOME, "repos", "blfs")

ENTITY_RE = re.compile(r'<!ENTITY\s+([A-Za-z0-9_.+-]+)\s+"([^"]*)"\s*>')
REF_RE = re.compile(r"&([A-Za-z0-9_.+-]+);")


def parse_entities(paths):
    ents = {}
    for path in paths:
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        for name, value in ENTITY_RE.findall(text):
            ents.setdefault(name, value)
    return ents


def resolve(value, ents, depth=0):
    if depth > 12:
        return value
    return REF_RE.sub(lambda m: resolve(ents.get(m.group(1), m.group(0)), ents, depth + 1), value)


def book_versions():
    lfs_ents = parse_entities([os.path.join(LFS, "packages.ent")])
    blfs_paths = [os.path.join(BLFS, "packages.ent"), os.path.join(BLFS, "general.ent")]
    blfs_paths += glob.glob(os.path.join(BLFS, "x", "installing", "*.xml"))
    blfs_paths += glob.glob(os.path.join(BLFS, "general", "**", "*.xml"), recursive=True)
    blfs_ents = parse_entities(blfs_paths)
    vers = {}
    for src, ents in (("lfs", lfs_ents), ("blfs", blfs_ents)):
        for name, value in ents.items():
            if not name.endswith("-version"):
                continue
            pkg = name[: -len("-version")]
            v = resolve(value, ents)
            if re.fullmatch(r"[\d][\w.+-]*", v or ""):
                key = norm(pkg)
                if key == "glib2":
                    key = "glib"
                if key == "sqlite" and v.isdigit() and len(v) == 7:
                    v = v[0] + "." + v[1:3] + "." + v[3]
                # LFS wins for base packages; BLFS fills the rest.
                vers.setdefault(key, (v, src, name))
    return vers


def norm(name):
    n = name.lower()
    n = n.replace("libx11", "libx11")
    return re.sub(r"[^a-z0-9]", "", n)


def vkey(v):
    parts = re.split(r"[._+~-]", v)
    out = []
    for p in parts:
        m = re.match(r"(\d+)(.*)", p)
        if m:
            out.append(int(m.group(1)))
            if m.group(2):
                out.append(m.group(2))
        elif p:
            out.append(p)
    return out


def vcmp(a, b):
    ka, kb = vkey(a), vkey(b)
    for x, y in zip(ka, kb):
        if type(x) is int and type(y) is int:
            if x != y:
                return -1 if x < y else 1
        else:
            xs, ys = str(x), str(y)
            if xs != ys:
                return -1 if xs < ys else 1
    if len(ka) != len(kb):
        return -1 if len(ka) < len(kb) else 1
    return 0


def local_rpms(rpm_dir):
    pkgs = {}
    for path in glob.glob(os.path.join(rpm_dir, "*.rpm")):
        base = os.path.basename(path)[:-4]
        if base.endswith(".src"):
            base = base[:-4]
        if "debug" in base:
            continue
        m = re.match(r"(.+)-([^-]+)-([^-]+)\.(x86_64|noarch|i686|aarch64)$", base)
        if not m:
            continue
        name, ver, rel = m.group(1), m.group(2), m.group(3)
        pkgs[name] = (ver, path)
    return pkgs


def local_specs(spec_dir):
    out = {}
    for path in glob.glob(os.path.join(spec_dir, "*", "*.spec")):
        name = ver = None
        for line in open(path, encoding="utf-8", errors="replace"):
            m = re.match(r"^(Name|Version):\s*(\S+)", line)
            if not m:
                continue
            if m.group(1) == "Name":
                name = m.group(2)
            else:
                ver = m.group(2)
            if name and ver:
                break
        if name and ver:
            out[name] = (ver, path)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpm-dir", default=os.path.join(ROOT, "build", "repo-all"))
    args = ap.parse_args()

    book = book_versions()
    rpms = local_rpms(args.rpm_dir)
    specs = local_specs(os.path.join(ROOT, "package_specs"))

    rows = []
    for name, (ver, path) in sorted(rpms.items()):
        key = norm(name)
        hit = book.get(key)
        # aliases used by the books
        if not hit:
            for alias in {
                "linux-api-headers": "linux",
                "glibc-locales": "glibc",
                "browneye-base": "",
                "browneye-sysconfig": "",
                "browneye-desktop-config": "",
                "xfce-desktop": "",
            }.get(name, "").split():
                hit = book.get(norm(alias))
                if hit:
                    break
        if not hit:
            rows.append(("NO-BOOK", name, ver, "-", "-", path))
            continue
        bver, src, entity = hit
        c = vcmp(ver, bver)
        status = "OK" if c == 0 else ("OUTDATED" if c < 0 else "NEWER")
        rows.append((status, name, ver, bver, f"{src}:{entity}", path))

    # specs that have no RPM yet
    have = {norm(n) for n in rpms}
    for name, (ver, path) in sorted(specs.items()):
        if norm(name) in have:
            continue
        hit = book.get(norm(name))
        if hit:
            bver, src, entity = hit
            c = vcmp(ver, bver)
            status = "OK" if c == 0 else ("OUTDATED" if c < 0 else "NEWER")
            rows.append((status + "/SPEC-ONLY", name, ver, bver, f"{src}:{entity}", path))
        else:
            rows.append(("NO-BOOK/SPEC-ONLY", name, ver, "-", "-", path))

    order = {"OUTDATED": 0, "OUTDATED/SPEC-ONLY": 1, "OK": 2, "OK/SPEC-ONLY": 3,
             "NEWER": 4, "NEWER/SPEC-ONLY": 5, "NO-BOOK": 6, "NO-BOOK/SPEC-ONLY": 7}
    rows.sort(key=lambda r: (order.get(r[0], 9), r[1]))

    counts = {}
    for r in rows:
        counts[r[0]] = counts.get(r[0], 0) + 1
    print(f"# version audit vs LFS/BLFS trunk ({len(rows)} local packages)\n")
    for k in sorted(counts):
        print(f"- {k}: {counts[k]}")
    print()
    print("| status | package | local | book | source |")
    print("|---|---|---|---|---|")
    for status, name, ver, bver, src, path in rows:
        if status.startswith("OK"):
            continue
        print(f"| {status} | {name} | {ver} | {bver} | {src} |")

    print("\n## full list (including OK)\n")
    print("| status | package | local | book | source |")
    print("|---|---|---|---|---|")
    for status, name, ver, bver, src, path in rows:
        print(f"| {status} | {name} | {ver} | {bver} | {src} |")


if __name__ == "__main__":
    sys.exit(main())
