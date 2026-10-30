import logging
import os
import glob
import shutil
from concurrent.futures import ThreadPoolExecutor

from db import PackageDatabase
from process import run_process
from package import (
    Package,
    discover_packages,
    load_aliases,
    load_order,
    resolve_package_name,
)
from sources import parse_sources, fetch_sources
import util

log = logging.getLogger("BUILD")

RPMBUILD_DIRS = ("BUILD", "BUILDROOT", "RPMS", "SOURCES", "SPECS", "SRPMS")


def ensure_rpmbuild_tree():
    """Create the rpmbuild tree before sources are fetched into SOURCES."""
    topdir = os.path.expanduser("~/rpmbuild")
    for directory in RPMBUILD_DIRS:
        os.makedirs(os.path.join(topdir, directory), exist_ok=True)
    return topdir


class PackageBuilder(object):
    def __init__(self):
        self.rpmbuild = ensure_rpmbuild_tree()
        self.package_db = PackageDatabase()
        self.packages = {}
        self.aliases = load_aliases()
        for package in discover_packages():
            self.package_db.add_package(package.name)
            self.packages[package.name] = package

    def _copy_files(self, package):
        files_path = package.get_files_path()
        if not os.path.isdir(files_path):
            return
        print("has files")
        for filename in sorted(glob.glob("{}/*".format(files_path))):
            print("  * Copying:", filename)
            shutil.copy(filename, os.path.join(self.rpmbuild, "SOURCES"))

    def _build_package(self, package):
        print("Building Package ({})".format(package.name))
        util.set_term_title("Building Package ({})".format(package.name))

        if not package.is_buildable():
            print("Package {} has neither a sources nor a nosources file.".format(
                package.name))
            return False

        if package.needs_download():
            sources = parse_sources(package.get_full_sources_path())
            if fetch_sources(sources) is not True:
                return False

        self._copy_files(package)

        cmd = ["rpmbuild", "-bb", "--clean", package.get_full_spec_path()]
        print("Running: ", cmd)
        return_code = run_process(cmd)
        if return_code != 0:
            return False
        return True

    def _record(self, package, success):
        if success:
            self.package_db.set_built(package.name)
            util.print_success_message(
                "Sucessfully built: {}".format(package.name))
        else:
            self.package_db.set_failed(package.name)
            util.print_fail_message(
                "Failed to build: {}".format(package.name))

    def build_package(self, package_name):
        resolved = resolve_package_name(package_name, self.packages, self.aliases)
        if resolved is None:
            print("Package {} not found.".format(package_name))
            return False
        package = self.packages[resolved]
        success = self._build_package(package)
        self._record(package, success)
        return success

    def build_spec(self, spec_path):
        """Build an out-of-tree spec file (used by the base container)."""
        spec_path = os.path.abspath(spec_path)
        package_path = os.path.dirname(spec_path)
        package = Package(
            os.path.basename(spec_path)[:-len(".spec")],
            package_path,
            os.path.basename(spec_path),
        )
        success = self._build_package(package)
        self._record(package, success)
        return success

    @staticmethod
    def default_jobs():
        """Parallel package builds. Each rpmbuild itself gets -j<ncpus>."""
        cpus = os.cpu_count() or 4
        return max(4, min(8, cpus // 2))

    def build_packages(self, names, jobs=0):
        jobs = jobs or self.default_jobs()
        if jobs <= 1 or len(names) <= 1:
            results = []
            for name in names:
                results.append(self.build_package(name))
            return results
        print("Building {} packages with {} workers.".format(len(names), jobs))
        with ThreadPoolExecutor(max_workers=min(jobs, len(names))) as pool:
            return list(pool.map(self.build_package, names))

    def build_all(self, jobs=0):
        order = load_order()
        seen = set()
        queue = []
        for name in order:
            resolved = resolve_package_name(name, self.packages, self.aliases)
            if resolved is None:
                print("Skipping {} (no spec found).".format(name))
                continue
            seen.add(resolved)
            if self.package_db.is_built(resolved):
                print(resolved, "is already built, skipping.")
                continue
            queue.append(resolved)

        # Anything not listed in ORDER still gets built, in discovery order.
        for package_name in self.packages:
            if package_name in seen:
                continue
            if self.package_db.is_built(package_name):
                print(package_name, "is already built, skipping.")
                continue
            queue.append(package_name)

        self.build_packages(queue, jobs=jobs)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
