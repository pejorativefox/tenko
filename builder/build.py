import glob
import logging
import os
import shutil
import subprocess
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


def spec_nevra(spec_path):
    """Return NAME-VERSION-RELEASE for a spec, or None if rpm cannot parse it.

    Used to refuse building two specs that would write the same RPM (for
    example a bootstrap and a final variant of the same package): the second
    build silently replaces the first in ~/rpmbuild/RPMS.
    """
    try:
        output = subprocess.check_output(
            ["rpm", "-q", "--specfile", "--qf",
             "%{NAME}-%{VERSION}-%{RELEASE}\n", spec_path],
            stderr=subprocess.DEVNULL, text=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    for line in output.splitlines():
        if line.strip():
            return line.strip()
    return None


def new_result():
    return {"ok": [], "failed": [], "unknown": [], "conflicts": {}}


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
            if not fetch_sources(sources):
                return False

        self._copy_files(package)

        command = ["rpmbuild", "-bb", "--clean", package.get_full_spec_path()]
        print("Running: ", command)
        return run_process(command) == 0

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
        try:
            success = self._build_package(package)
        except Exception as exc:  # always record a failure, never crash the run
            log.exception("build of %s failed: %s", package.name, exc)
            success = False
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
        try:
            success = self._build_package(package)
        except Exception as exc:
            log.exception("build of %s failed: %s", package.name, exc)
            success = False
        self._record(package, success)
        return success

    @staticmethod
    def default_jobs():
        """Parallel package builds. Each rpmbuild itself gets -j<ncpus>."""
        cpus = os.cpu_count() or 4
        return max(4, min(8, cpus // 2))

    def _resolve(self, names):
        resolved, unknown, seen = [], [], set()
        for name in names:
            match = resolve_package_name(name, self.packages, self.aliases)
            if match is None:
                unknown.append(name)
                continue
            if match in seen:
                continue
            seen.add(match)
            resolved.append(match)
        return resolved, unknown

    def _find_conflicts(self, resolved):
        by_nevra = {}
        for name in resolved:
            nevra = spec_nevra(self.packages[name].get_full_spec_path())
            if nevra:
                by_nevra.setdefault(nevra, []).append(name)
        return {nevra: names for nevra, names in by_nevra.items()
                if len(names) > 1}

    def build_packages(self, names, jobs=0):
        result = new_result()
        resolved, result["unknown"] = self._resolve(names)

        result["conflicts"] = self._find_conflicts(resolved)
        if result["conflicts"]:
            for nevra, clashing in sorted(result["conflicts"].items()):
                print("Refusing to build {}: they all produce {}".format(
                    ", ".join(clashing), nevra))
            clashing = {n for names in result["conflicts"].values()
                        for n in names}
            resolved = [n for n in resolved if n not in clashing]

        if not resolved:
            return result

        jobs = jobs or self.default_jobs()
        if jobs <= 1 or len(resolved) <= 1:
            pairs = [(name, self.build_package(name)) for name in resolved]
        else:
            print("Building {} packages with {} workers.".format(
                len(resolved), min(jobs, len(resolved))))
            with ThreadPoolExecutor(max_workers=min(jobs, len(resolved))) as pool:
                pairs = list(zip(resolved, pool.map(self.build_package, resolved)))

        for name, success in pairs:
            result["ok" if success else "failed"].append(name)
        return result

    def build_all(self, jobs=0):
        """Build the ORDER (base system) set, skipping built packages.

        This deliberately no longer appends every discovered spec: building
        desktop packages on the host must be an explicit choice.
        """
        order = load_order()
        queue = []
        for name in order:
            resolved = resolve_package_name(name, self.packages, self.aliases)
            if resolved is None:
                print("Skipping {} (no spec found).".format(name))
                continue
            if self.package_db.is_built(resolved):
                print(resolved, "is already built, skipping.")
                continue
            queue.append(resolved)
        print("Base set from ORDER: {} packages to build.".format(len(queue)))
        return self.build_packages(queue, jobs=jobs)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
