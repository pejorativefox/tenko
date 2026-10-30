import os
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from process import run_process

SOURCES_DIR = os.path.expanduser("~/rpmbuild/SOURCES")

# Parallel source downloads. Cores on this box: 16; cap download workers so we
# do not saturate the mirror or the network.
DOWNLOAD_WORKERS = max(4, min(12, (os.cpu_count() or 4)))


def get_md5(filename):
    """Get an md5 for a file on the filesystem by running the md5sum tool.

    Args:
        param1 (str) filename: the full path of the file

    Returns:
        str: the md5sum of the specified file.

    """
    import subprocess
    md5 = subprocess.check_output(["md5sum", filename]).rstrip().decode('ascii').split(" ")[0]
    return md5


def parse_sources(sources_filename):
    """Parse a 'sources' file to get a list of files that need to be downloaded
    for a package.

    Args:
        param1 (str) sources_filename: the full path to a valid sources file

    Returns:
        list of (str:md5sum, str:url, str:override_filename)

    Blank lines and lines starting with '#' are ignored.
    """
    sources = []
    with open(sources_filename, "r") as fd:
        for line in fd:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            split_line = line.split()
            line_length = len(split_line)
            if line_length not in (2, 3):
                print("{} appears to have a mangled line...".format(sources_filename))
                exit()
            md5 = split_line[0]
            url = split_line[1]
            filename = split_line[2] if line_length == 3 else None
            sources.append([md5, url, filename])
    return sources


BASE_PATH = os.path.expanduser('~') # TODO: maybe not best location


def _fetch_one(source):
    md5, url, override_filename = source
    if override_filename:
        filename = override_filename
    else:
        filename = os.path.basename(urlparse(url).path)
    out_file = os.path.join(SOURCES_DIR, filename)

    if os.path.isfile(out_file):
        print("  + Already present (cached): {}".format(filename))
    else:
        print("Downloading {} to {}".format(url, out_file))
        cmd = ["curl", "-fL", "-o", out_file, url]
        if os.getenv("USE_PROXYCHAINS"):
            cmd = ["proxychains4", "-q"] + cmd
        return_code = run_process(cmd)
        if return_code != 0:
            return False

    target_md5 = get_md5(out_file)
    if md5 == target_md5:
        print("  + md5 good: {}".format(filename))
        return True
    print("Bad md5 for {}: {}".format(filename, target_md5))
    return False


def fetch_sources(sources, override_filename=None):
    os.makedirs(SOURCES_DIR, exist_ok=True)
    if not sources:
        return True
    workers = min(DOWNLOAD_WORKERS, len(sources))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(_fetch_one, sources))
    return all(results)
