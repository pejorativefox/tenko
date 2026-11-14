#!/usr/bin/env python3
"""Drop packages from repository metadata (used by `tenko publish remove`).

Reads the decompressed primary, filelists and other XML from SRC, writes
them to DST without the packages named on the command line, and prints the
RPM file names (location hrefs) of the removed entries, one per line.

Refuses (exit 1) when a name is not in the metadata, or when a package that
stays requires a capability that only a removed package provides.

Usage:
    remove_packages.py SRC DST NAME...
"""

import os
import re
import sys

PACKAGE = re.compile(r"<package[ >].*?</package>\n?", re.S)
ENTRY = re.compile(r'<rpm:entry name="([^"]+)"')


def section(block, tag):
    match = re.search(r"<rpm:%s>(.*?)</rpm:%s>" % (tag, tag), block, re.S)
    return set(ENTRY.findall(match.group(1))) if match else set()


def primary_info(block):
    name = re.search(r"<name>([^<]+)</name>", block).group(1)
    pkgid = re.search(r'<checksum [^>]*pkgid="YES">([^<]+)<', block).group(1)
    href = re.search(r'<location [^>]*href="([^"]+)"', block).group(1)
    files = set(re.findall(r"<file[^>]*>([^<]+)</file>", block))
    return {"name": name, "pkgid": pkgid, "href": href,
            "provides": section(block, "provides") | {name} | files,
            "requires": section(block, "requires")}


def rewrite(text, keep):
    """Return text with only the <package> blocks keep() accepts."""
    blocks = PACKAGE.findall(text)
    kept = [b for b in blocks if keep(b)]
    head = text[:text.index(blocks[0])] if blocks else text
    tail = text[text.rindex(blocks[-1]) + len(blocks[-1]):] if blocks else ""
    head = re.sub(r'packages="\d+"', 'packages="%d"' % len(kept), head, count=1)
    return head + "".join(kept) + tail, len(blocks) - len(kept)


def main():
    src, dst, names = sys.argv[1], sys.argv[2], set(sys.argv[3:])
    if not names:
        sys.exit(__doc__)
    with open(os.path.join(src, "primary.xml"), encoding="utf-8") as handle:
        primary = handle.read()

    infos = [primary_info(b) for b in PACKAGE.findall(primary)]
    removed = [i for i in infos if i["name"] in names]
    staying = [i for i in infos if i["name"] not in names]
    missing = names - {i["name"] for i in removed}
    if missing:
        sys.exit("error: not in the repository: " + ", ".join(sorted(missing)))

    still_provided = set().union(*(i["provides"] for i in staying))
    gone = set().union(*(i["provides"] for i in removed)) - still_provided
    broken = sorted("%s (requires %s)" % (i["name"], cap)
                    for i in staying for cap in i["requires"] & gone)
    if broken:
        sys.exit("error: packages that stay would lose a dependency:\n  "
                 + "\n  ".join(broken))

    pkgids = {i["pkgid"] for i in removed}
    os.makedirs(dst, exist_ok=True)
    for mdtype in ("primary", "filelists", "other"):
        with open(os.path.join(src, mdtype + ".xml"), encoding="utf-8") as handle:
            text = handle.read()
        if mdtype == "primary":
            keep = lambda b: primary_info(b)["pkgid"] not in pkgids  # noqa: E731
        else:
            keep = lambda b: re.search(r'pkgid="([^"]+)"', b).group(1) not in pkgids  # noqa: E731
        text, dropped = rewrite(text, keep)
        if dropped != len(removed):
            sys.exit("error: %s.xml: dropped %d entries, expected %d"
                     % (mdtype, dropped, len(removed)))
        with open(os.path.join(dst, mdtype + ".xml"), "w", encoding="utf-8") as handle:
            handle.write(text)

    for info in removed:
        print(info["href"])


if __name__ == "__main__":
    main()
