"""Python packages require their interpreter and the modules they import.

Tenko generates only `python(abi) = X.Y` (tenko-rpm-config's python.attr);
dependencies between Python modules are written by hand in the specs.  The
generator is tested directly.  The repository checks read the RPMs in the
offline mirror (`tenko sync`) and are skipped when there is none:

* every package with files under /usr/lib*/pythonX.Y/ requires python(abi)
  (or python itself), so it cannot be installed without its interpreter;
* every unconditional Requires-Dist in a package's top-level .dist-info is
  covered by a Requires on the package that ships that distribution.
"""

import email.parser
import os
import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RPM_CONFIG = REPO_ROOT / "package_specs" / "tenko-rpm-config"
GENERATOR = RPM_CONFIG / "files" / "tenko-pythondeps.sh"

PY_LIB = re.compile(r"^/usr/lib(64)?/python(\d+\.\d+)/")
TOP_DIST_INFO = re.compile(
    r"^/usr/lib(64)?/python\d+\.\d+/site-packages/[^/]+\.dist-info/METADATA$")


def mirror_dir():
    env = os.environ.get("TENKO_REPO_CACHE")
    if env:
        return Path(env)
    try:
        common = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--path-format=absolute",
             "--git-common-dir"], capture_output=True, text=True, check=True
        ).stdout.strip()
        return Path(common).parent / "build" / "cache" / "repo"
    except (OSError, subprocess.CalledProcessError):
        return REPO_ROOT / "build" / "cache" / "repo"


def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def rpm_query(path, *args):
    return subprocess.run(["rpm", "-qp", *args, str(path)], capture_output=True,
                          text=True, check=True).stdout.splitlines()


class GeneratorTest(unittest.TestCase):
    def run_generator(self, mode, paths, buildroot=""):
        env = dict(os.environ, RPM_BUILD_ROOT=buildroot)
        return subprocess.run(
            ["sh", str(GENERATOR), mode], input="\n".join(paths) + "\n",
            capture_output=True, text=True, check=True, env=env
        ).stdout.split("\n")[:-1]

    def test_module_files_require_the_abi(self):
        root = "/builddir/BUILDROOT/x"
        out = self.run_generator("--requires", [
            root + "/usr/lib64/python3.15/site-packages/foo/__init__.py",
            root + "/usr/lib/python3.15/site-packages/bar.py",
            root + "/usr/share/doc/foo/README",
        ], buildroot=root)
        self.assertEqual(out, ["python(abi) = 3.15"])

    def test_interpreter_provides_the_abi(self):
        out = self.run_generator("--provides", [
            "/usr/bin/python3.15", "/usr/bin/python3", "/usr/bin/pip3"])
        self.assertEqual(out, ["python(abi) = 3.15"])

    def test_rpm_config_ships_the_generator(self):
        spec = (RPM_CONFIG / "tenko-rpm-config.spec").read_text()
        attr = (RPM_CONFIG / "files" / "python.attr").read_text()
        self.assertIn("%{_fileattrsdir}/python.attr", spec)
        self.assertIn("%{_rpmconfigdir}/tenko-pythondeps.sh", spec)
        self.assertIn("tenko-pythondeps.sh --requires", attr)
        self.assertIn("tenko-pythondeps.sh --provides", attr)


class RepositoryPythonRequiresTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mirror = mirror_dir()
        if not (mirror / "repodata" / "repomd.xml").is_file():
            raise unittest.SkipTest("no offline mirror (run ./tenko sync)")
        cls.packages = {}
        for path in sorted(mirror.glob("*.rpm")):
            files = rpm_query(path, "-l")
            if not any(PY_LIB.match(f) for f in files):
                continue
            name = rpm_query(path, "--qf", "%{NAME}")[0]
            cls.packages[name] = {
                "path": path,
                "files": files,
                "requires": rpm_query(path, "--requires"),
            }
        cls.dists = {}  # normalized distribution name -> package
        cls.metadata = {}  # package -> list of parsed METADATA
        for name, info in cls.packages.items():
            wanted = [f for f in info["files"] if TOP_DIST_INFO.match(f)]
            if not wanted:
                continue
            cpio = subprocess.run(
                "rpm2cpio '{}' | cpio -i --quiet --to-stdout {}".format(
                    info["path"], " ".join("'.{}'".format(f) for f in wanted)),
                shell=True, capture_output=True, check=True).stdout
            texts = cpio.decode("utf-8", "replace").split("Metadata-Version:")[1:]
            parsed = [email.parser.Parser().parsestr("Metadata-Version:" + t)
                      for t in texts]
            cls.metadata[name] = parsed
            for meta in parsed:
                cls.dists[normalize(meta["Name"] or "")] = name

    def test_python_packages_require_the_interpreter(self):
        missing = []
        for name, info in sorted(self.packages.items()):
            names = {r.split()[0] for r in info["requires"]}
            if not any(r.startswith("python(abi)") for r in info["requires"]) \
                    and "python" not in names and name != "python":
                missing.append(name)
        self.assertEqual(missing, [], "packages with Python modules that do "
                         "not require python(abi): rebuild them with "
                         "tenko-rpm-config >= 6-4")

    def test_declared_module_dependencies_are_required(self):
        problems = []
        for name, metas in sorted(self.metadata.items()):
            names = {r.split()[0] for r in self.packages[name]["requires"]}
            for meta in metas:
                for req in meta.get_all("Requires-Dist") or []:
                    if ";" in req:
                        continue  # extras and environment markers
                    dist = normalize(re.split(r"[\s<>=!~(\[]", req.strip(), maxsplit=1)[0])
                    provider = self.dists.get(dist)
                    if provider is None:
                        problems.append("{} needs {}, which no package "
                                        "ships".format(name, dist))
                    elif provider != name and provider not in names:
                        problems.append("{} needs {}: add Requires: {}".format(
                            name, dist, provider))
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
