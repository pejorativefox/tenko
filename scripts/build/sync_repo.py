#!/usr/bin/env python3
"""Mirror the published Tenko repository into a local directory.

Every build installs from this mirror with the network off, so each RPM is
downloaded once.  A sync fetches repomd.xml; when it is unchanged nothing
else is downloaded.  Otherwise the new metadata is fetched, missing or
changed RPMs are downloaded and sha256-verified, RPMs the metadata no longer
references are deleted, and repodata/ is swapped in last, so an interrupted
sync leaves the previous consistent mirror in place.

The first URL that answers is used, so a reachable LAN mirror is preferred
over the public site.  If none answers and a mirror already exists, the sync
is skipped with a warning (offline builds keep working).

Usage:
    tenko sync
    tenko sync --dest build/cache/repo URL [URL...]
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

REPO_NS = "{http://linux.duke.edu/metadata/repo}"
COMMON_NS = "{http://linux.duke.edu/metadata/common}"
WORKERS = 8


def fetch(url, timeout=60):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read()


def download(url, path, timeout=300):
    """Download url to path through a .part file."""
    part = path + ".part"
    with urllib.request.urlopen(url, timeout=timeout) as response, \
            open(part, "wb") as handle:
        shutil.copyfileobj(response, handle, 1024 * 1024)
    os.replace(part, path)


def file_digest(path, algorithm):
    digest = hashlib.new(algorithm)
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decompress(path):
    with open(path, "rb") as handle:
        data = handle.read()
    if path.endswith(".zst"):
        try:
            from compression import zstd
            return zstd.decompress(data)
        except ImportError:
            return subprocess.run(["zstd", "-dc"], input=data, check=True,
                                  capture_output=True).stdout
    if path.endswith(".gz"):
        import gzip
        return gzip.decompress(data)
    if path.endswith(".xz"):
        import lzma
        return lzma.decompress(data)
    return data


def repomd_files(repomd):
    """Return {type: (href, checksum-type, checksum)} from repomd.xml bytes."""
    out = {}
    for data in ET.fromstring(repomd).iter(REPO_NS + "data"):
        location = data.find(REPO_NS + "location").get("href")
        checksum = data.find(REPO_NS + "checksum")
        out[data.get("type")] = (location, checksum.get("type"), checksum.text)
    return out


def packages(primary_xml):
    """Yield (href, checksum-type, checksum, size) for each package."""
    for _, el in ET.iterparse(__import__("io").BytesIO(primary_xml)):
        if el.tag == COMMON_NS + "package":
            checksum = el.find(COMMON_NS + "checksum")
            size = el.find(COMMON_NS + "size")
            yield (el.find(COMMON_NS + "location").get("href"),
                   checksum.get("type"), checksum.text,
                   int(size.get("package")))
            el.clear()


def pick_url(urls):
    for url in urls:
        url = url.rstrip("/") + "/"
        try:
            return url, fetch(url + "repodata/repomd.xml", timeout=5)
        except OSError as exc:
            print("  ! {} unreachable: {}".format(url, exc))
    return None, None


def sync(urls, dest):
    os.makedirs(dest, exist_ok=True)
    current = os.path.join(dest, "repodata", "repomd.xml")
    url, repomd = pick_url(urls)
    if url is None:
        if os.path.isfile(current):
            print("warning: no repository reachable; using the existing mirror")
            return 0
        print("error: no repository reachable and no mirror in " + dest,
              file=sys.stderr)
        return 1

    if os.path.isfile(current):
        with open(current, "rb") as handle:
            unchanged = handle.read() == repomd
    else:
        unchanged = False

    with tempfile.TemporaryDirectory(dir=dest, prefix=".sync-") as tmp:
        repodata = os.path.join(tmp, "repodata")
        os.makedirs(repodata)
        if unchanged:
            # Re-check the RPMs against the local metadata only.
            files = repomd_files(repomd)
            primary_path = os.path.join(dest, files["primary"][0])
        else:
            print("fetching metadata from " + url)
            files = repomd_files(repomd)
            for href, algorithm, checksum in files.values():
                path = os.path.join(tmp, href)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                download(url + href, path)
                if file_digest(path, algorithm) != checksum:
                    print("error: bad checksum for " + href, file=sys.stderr)
                    return 1
            with open(os.path.join(tmp, "repodata", "repomd.xml"), "wb") as handle:
                handle.write(repomd)
            primary_path = os.path.join(tmp, files["primary"][0])

        wanted = list(packages(decompress(primary_path)))
        missing = []
        for href, algorithm, checksum, size in wanted:
            path = os.path.join(dest, href)
            if not (os.path.isfile(path) and os.path.getsize(path) == size):
                missing.append((href, algorithm, checksum))
        if unchanged and not missing:
            print("mirror is current: {} packages in {}".format(len(wanted), dest))
            return 0

        missing_set = {m[0] for m in missing}
        total = sum(s for h, _, _, s in wanted if h in missing_set)
        print("downloading {} of {} packages ({:.1f} MiB) from {}".format(
            len(missing), len(wanted), total / 2**20, url))

        def get(item):
            href, algorithm, checksum = item
            path = os.path.join(dest, href)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            try:
                download(url + href, path)
            except OSError as exc:
                return "{}: {}".format(href, exc)
            if file_digest(path, algorithm) != checksum:
                os.unlink(path)
                return "{}: bad checksum".format(href)
            return None

        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            errors = [e for e in pool.map(get, missing) if e]
        if errors:
            for error in errors:
                print("  ! " + error, file=sys.stderr)
            print("error: {} download(s) failed; mirror metadata left as it was"
                  .format(len(errors)), file=sys.stderr)
            return 1

        if not unchanged:
            old = os.path.join(dest, "repodata")
            if os.path.isdir(old):
                shutil.rmtree(old)
            os.replace(repodata, old)

    keep = {os.path.normpath(href) for href, _, _, _ in wanted}
    removed = 0
    for name in os.listdir(dest):
        if name.endswith(".rpm") and name not in keep:
            os.unlink(os.path.join(dest, name))
            removed += 1
    print("mirror updated: {} packages, {} downloaded, {} removed".format(
        len(wanted), len(missing), removed))
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="tenko sync", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("urls", nargs="*", help="repository base URLs to try")
    parser.add_argument("--dest", default=os.environ.get(
        "TENKO_REPO_CACHE", "build/cache/repo"), help="mirror directory")
    args = parser.parse_args()
    urls = args.urls or os.environ.get("SYNC_URLS", "").split()
    if not urls:
        parser.error("no repository URL given (set SYNC_URLS or pass URLs)")
    return sync(urls, args.dest)


if __name__ == "__main__":
    sys.exit(main())
