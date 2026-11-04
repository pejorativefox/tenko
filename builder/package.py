import glob
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LFS_LOCK = os.path.join(REPO_ROOT, "lfs.lock")
SPECS_DIR = os.path.join(REPO_ROOT, "package_specs")
ORDER_FILE = os.path.join(SPECS_DIR, "ORDER")


class Package(object):
    def __init__(self, name, path, spec_file):
        self.name = name
        self.path = path
        self.spec_file = spec_file
        self.has_sources = os.path.isfile(self.get_full_sources_path())
        self.has_nosources = os.path.isfile(os.path.join(path, "nosources"))
        self.needs_root = False

    def get_full_spec_path(self):
        return os.path.join(self.path, self.spec_file)

    def get_full_sources_path(self):
        return os.path.join(self.path, "sources")

    def get_files_path(self):
        return os.path.join(self.path, "files")

    def needs_download(self):
        return self.has_sources

    def is_buildable(self):
        return self.has_sources or self.has_nosources


def discover_packages(path=SPECS_DIR):
    packages = []
    for package_path in sorted(glob.glob(os.path.join(path, "*"))):
        if not os.path.isdir(package_path):
            continue
        specs = sorted(glob.glob(os.path.join(package_path, "*.spec")))
        if not specs:
            # Disabled packages (``.spec.disabled``) and empty directories are
            # intentionally skipped instead of aborting the whole run.
            continue
        for spec in specs:
            spec_file = os.path.basename(spec)
            package_name = spec_file[:-len(".spec")]
            packages.append(Package(package_name, package_path, spec_file))
    print("Found {} packages.".format(len(packages)))
    return packages


def load_aliases(path=LFS_LOCK):
    """Return LFS package name -> spec directory name mappings."""
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as exc:
        print("warning: could not read {}: {}".format(path, exc))
        return {}
    return data.get("aliases", {})


def load_order(path=ORDER_FILE):
    """Return the preferred build order as a list of package names."""
    if not os.path.isfile(path):
        return []
    order = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.split("#", 1)[0].strip()
            if line:
                order.append(line)
    return order


def resolve_package_name(name, packages, aliases=None):
    """Resolve an LFS or spec name to a discovered package name."""
    aliases = aliases or {}
    for candidate in (name, aliases.get(name)):
        if candidate and candidate in packages:
            return candidate
    return None


if __name__ == "__main__":
    for p in discover_packages():
        print(p.get_full_spec_path())
