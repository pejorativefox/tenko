#!/usr/bin/env python3
"""Download and md5-verify the sources listed in package_specs/<pkg>/sources.

Release builds run rpmbuild with --network=none inside a container, so every
tarball must already be in ~/rpmbuild/SOURCES.  scripts/build_specs.sh calls
this helper for each spec before starting the container.

A package directory with no `sources` file, or with a `nosources` marker, is
skipped.  Each `sources` line is `md5 url [filename]`; the optional third
field overrides the basename taken from the URL.  Downloads run in parallel
and are written to a .part file, verified against the md5 and only then
renamed, so a failed or corrupted transfer cannot poison the cache.

Usage:
    scripts/fetch_sources.py curl/curl.spec
    scripts/fetch_sources.py package_specs/curl
    scripts/fetch_sources.py curl
    scripts/fetch_sources.py --dest /tmp/SOURCES curl/curl.spec
"""

import argparse
import hashlib
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS_DIR = os.path.join(REPO_ROOT, "package_specs")
DEFAULT_SOURCES_DIR = os.environ.get(
    "TENKO_SOURCES_DIR", os.path.expanduser("~/rpmbuild/SOURCES"))

# Cap parallel downloads so a large wave does not saturate the mirror.
DOWNLOAD_WORKERS = max(4, min(12, (os.cpu_count() or 4)))


def get_md5(filename):
    digest = hashlib.md5()
    with open(filename, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_sources(sources_filename):
    """Return a list of [md5, url, filename-or-None] entries."""
    sources = []
    with open(sources_filename, "r", encoding="utf-8") as handle:
        for lineno, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) not in (2, 3):
                raise ValueError(
                    "{}:{}: expected 'md5 url [filename]', got {!r}".format(
                        sources_filename, lineno, line))
            md5, url = fields[0], fields[1]
            filename = fields[2] if len(fields) == 3 else None
            sources.append([md5, url, filename])
    return sources


def _unlink(path):
    try:
        os.unlink(path)
    except OSError:
        pass


def _fetch_one(source, dest):
    md5, url, override_filename = source
    filename = override_filename or os.path.basename(urlparse(url).path)
    if not filename:
        print("  ! cannot derive a filename from {}".format(url))
        return False

    out_file = os.path.join(dest, filename)
    part_file = out_file + ".part"

    if os.path.isfile(out_file):
        if get_md5(out_file) == md5:
            print("  + cached: {}".format(filename))
            return True
        print("  ! cached {} has the wrong md5; re-downloading".format(filename))
        os.unlink(out_file)

    print("  > download: {}".format(filename))
    command = ["curl", "-fL", "--retry", "2", "-o", part_file, url]
    if os.getenv("USE_PROXYCHAINS"):
        command = ["proxychains4", "-q"] + command
    try:
        result = subprocess.run(command, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, check=False)
    except OSError as exc:
        print("  ! could not run curl: {}".format(exc))
        _unlink(part_file)
        return False
    if result.returncode != 0:
        print("  ! download failed: {}".format(url))
        _unlink(part_file)
        return False

    actual_md5 = get_md5(part_file)
    if actual_md5 != md5:
        print("  ! bad md5 for {}: {} (expected {})".format(
            filename, actual_md5, md5))
        _unlink(part_file)
        return False

    os.replace(part_file, out_file)
    print("  + md5 good: {}".format(filename))
    return True


def fetch_sources(sources, dest, jobs=0):
    """Fetch every entry into dest; return True only if all succeeded."""
    if not sources:
        return True
    os.makedirs(dest, exist_ok=True)
    workers = jobs or min(DOWNLOAD_WORKERS, len(sources))
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        results = list(pool.map(lambda item: _fetch_one(item, dest), sources))
    return all(results)


def resolve_package_dir(path):
    """Resolve a spec path, package directory or bare name to its spec dir."""
    if os.path.isdir(path):
        return path
    if path.endswith(".spec"):
        path = os.path.dirname(path)
    for candidate in (path, os.path.join(SPECS_DIR, path)):
        if os.path.isdir(candidate):
            return candidate
    return None


def collect_sources(package_dirs):
    """Return (items, skipped) for a list of resolved package directories."""
    items, skipped = [], []
    for package_dir in package_dirs:
        name = os.path.basename(os.path.normpath(package_dir))
        if os.path.isfile(os.path.join(package_dir, "nosources")):
            skipped.append(name)
            continue
        sources_file = os.path.join(package_dir, "sources")
        if not os.path.isfile(sources_file):
            skipped.append(name)
            continue
        items.extend(parse_sources(sources_file))
    return items, skipped


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Download and md5-verify package sources")
    parser.add_argument(
        "paths", nargs="+",
        help="spec path, package directory or package name")
    parser.add_argument(
        "--dest", default=DEFAULT_SOURCES_DIR,
        help="download directory (default: %(default)s)")
    parser.add_argument(
        "--jobs", type=int, default=0,
        help="parallel downloads (0 = auto, default)")
    args = parser.parse_args(argv)

    package_dirs = []
    for path in args.paths:
        resolved = resolve_package_dir(path)
        if resolved is None:
            print("error: cannot resolve package directory for {!r}".format(
                path), file=sys.stderr)
            return 2
        package_dirs.append(resolved)

    try:
        items, skipped = collect_sources(package_dirs)
    except (OSError, ValueError) as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 1

    if skipped:
        print("no sources to fetch: {}".format(", ".join(sorted(skipped))))
    if not items:
        return 0

    print("fetching {} source file(s) into {}".format(len(items), args.dest))
    if not fetch_sources(items, args.dest, jobs=args.jobs):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
