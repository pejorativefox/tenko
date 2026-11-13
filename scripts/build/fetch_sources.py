#!/usr/bin/env python3
"""Download and md5-verify the sources listed in package_specs/<pkg>/sources.

rpmbuild does not download the tarballs a spec lists, so every one must
already be in the sources cache.  `tenko build` calls this helper for each
spec before starting the container.

A tarball already present with the right md5 in a seed directory
(TENKO_SOURCES_SEED, default ~/rpmbuild/SOURCES, the old shared cache) is
hard-linked instead of downloaded.

With --stage-root, each package then gets a private source directory,
ROOT/<spec-name>/SOURCES, holding hard links to just its own tarballs and
files/ (patches, units, filelists), so builds cannot pick up another
package's files.

A package directory with no `sources` file, or with a `nosources` marker, is
skipped.  Each `sources` line is `md5 url [filename]`; the optional third
field overrides the basename taken from the URL.  Downloads run in parallel
and are written to a .part file, verified against the md5 and only then
renamed, so a failed or corrupted transfer cannot poison the cache.

Usage:
    tenko fetch curl/curl.spec
    tenko fetch package_specs/curl
    tenko fetch curl
    tenko fetch --dest /tmp/SOURCES curl/curl.spec
    tenko fetch --stage-root build/out/build curl/curl.spec
"""

import argparse
import glob
import hashlib
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPECS_DIR = os.path.join(REPO_ROOT, "package_specs")
DEFAULT_SOURCES_DIR = os.environ.get(
    "TENKO_SOURCES_DIR", os.path.join(REPO_ROOT, "build", "sources"))
SEED_DIRS = os.environ.get(
    "TENKO_SOURCES_SEED", os.path.expanduser("~/rpmbuild/SOURCES")).split(":")

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


def source_filename(source):
    md5, url, override_filename = source
    return override_filename or os.path.basename(urlparse(url).path)


def link_or_copy(src, dst):
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def _fetch_one(source, dest):
    md5, url, override_filename = source
    filename = source_filename(source)
    if not filename:
        print("  ! cannot derive a filename from {}".format(url))
        return False

    os.makedirs(dest, exist_ok=True)
    out_file = os.path.join(dest, filename)
    part_file = out_file + ".part"

    if os.path.isfile(out_file):
        if get_md5(out_file) == md5:
            print("  + cached: {}".format(filename))
            return True
        print("  ! cached {} has the wrong md5; re-downloading".format(filename))
        os.unlink(out_file)

    for seed in SEED_DIRS:
        seeded = os.path.join(seed, filename)
        if seed and os.path.realpath(seed) != os.path.realpath(dest) and \
                os.path.isfile(seeded) and get_md5(seeded) == md5:
            link_or_copy(seeded, out_file)
            print("  + seeded: {} (from {})".format(filename, seed))
            return True

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


def stage(paths, package_dirs, sources_dir, root):
    """Link each package's tarballs and files/ into ROOT/<name>/SOURCES."""
    for path, package_dir in zip(paths, package_dirs):
        if path.endswith(".spec"):
            names = [os.path.basename(path)[:-len(".spec")]]
        else:
            names = [os.path.basename(spec)[:-len(".spec")] for spec in
                     sorted(glob.glob(os.path.join(package_dir, "*.spec")))]
        wanted = []
        if os.path.isdir(os.path.join(package_dir, "files")):
            wanted += sorted(glob.glob(os.path.join(package_dir, "files", "*")))
        items, _ = collect_sources([package_dir])
        wanted += [os.path.join(sources_dir, source_filename(item))
                   for item in items]
        for name in names:
            target = os.path.join(root, name, "SOURCES")
            if os.path.isdir(target):
                shutil.rmtree(target)
            os.makedirs(target)
            for src in wanted:
                if os.path.isfile(src):
                    link_or_copy(src, os.path.join(target, os.path.basename(src)))


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
        "--stage-root",
        help="also link each package's sources into ROOT/<name>/SOURCES")
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

    if items:
        print("fetching {} source file(s) into {}".format(len(items), args.dest))
        if not fetch_sources(items, args.dest, jobs=args.jobs):
            return 1
    if args.stage_root:
        stage(args.paths, package_dirs, args.dest, args.stage_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
