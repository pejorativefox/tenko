import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from process import run_process

SOURCES_DIR = os.path.expanduser("~/rpmbuild/SOURCES")

# Parallel source downloads. Cores on this box: 16; cap download workers so we
# do not saturate the mirror or the network.
DOWNLOAD_WORKERS = max(4, min(12, (os.cpu_count() or 4)))


def get_md5(filename):
    """Return the md5 of a file without shelling out to md5sum."""
    digest = hashlib.md5()
    with open(filename, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_sources(sources_filename):
    """Parse a 'sources' file into a list of (md5, url, filename-or-None).

    Blank lines and lines starting with '#' are ignored.  A mangled line is a
    hard error: the previous implementation called exit() (status 0).
    """
    sources = []
    with open(sources_filename, "r", encoding="utf-8") as fd:
        for lineno, raw in enumerate(fd, start=1):
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


def _fetch_one(source):
    md5, url, override_filename = source
    filename = override_filename or os.path.basename(urlparse(url).path)
    if not filename:
        print("  ! cannot derive a filename from {}".format(url))
        return False

    out_file = os.path.join(SOURCES_DIR, filename)
    part_file = out_file + ".part"

    if os.path.isfile(out_file):
        if get_md5(out_file) == md5:
            print("  + Already present (cached): {}".format(filename))
            return True
        # A partial or corrupted download must not poison the cache forever.
        print("  ! cached {} has the wrong md5; re-downloading".format(filename))
        os.unlink(out_file)

    print("Downloading {} to {}".format(url, out_file))
    command = ["curl", "-fL", "--retry", "2", "-o", part_file, url]
    if os.getenv("USE_PROXYCHAINS"):
        command = ["proxychains4", "-q"] + command
    if run_process(command) != 0:
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


def _unlink(path):
    try:
        os.unlink(path)
    except OSError:
        pass


def fetch_sources(sources):
    os.makedirs(SOURCES_DIR, exist_ok=True)
    if not sources:
        return True
    workers = min(DOWNLOAD_WORKERS, len(sources))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(_fetch_one, sources))
    return all(results)
