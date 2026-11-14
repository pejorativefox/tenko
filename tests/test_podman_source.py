"""The source-built podman installs under /usr and relies on its defaults."""

import re
import unittest
from pathlib import Path

PKG = Path(__file__).resolve().parents[1] / "package_specs" / "podman"


class PodmanSourceTest(unittest.TestCase):
    def setUp(self):
        self.conf = (PKG / "files" / "containers.conf").read_text()
        self.spec = (PKG / "podman.spec").read_text()
        self.files = (PKG / "files" / "podman.filelist").read_text().split()

    def test_no_opt_paths(self):
        for name, text in (("containers.conf", self.conf),
                           ("podman.spec", self.spec),
                           ("podman.filelist", " ".join(self.files))):
            self.assertNotIn("/opt", text, name)

    def test_helpers_use_builtin_search_paths(self):
        """Helpers sit at podman's default paths; no overrides needed."""
        for key in ("conmon_path", "helper_binaries_dir"):
            self.assertIsNone(re.search(r"^\s*" + key + r"\s*=", self.conf,
                                        re.M), key)
        self.assertRegex(self.conf, r'(?m)^runtime = "crun"$')
        self.assertRegex(self.conf, r'(?m)^cgroup_manager = "cgroupfs"$')
        for req in ("conmon", "crun", "netavark", "aardvark-dns",
                    "catatonit", "pasta"):
            self.assertRegex(self.spec, r"(?m)^Requires:\s+" +
                             re.escape(req) + r"$")

    def test_journald_logging(self):
        self.assertRegex(self.conf, r'(?m)^log_driver = "journald"$')
        self.assertRegex(self.conf, r'(?m)^events_logger = "journald"$')

    def test_etc_config_is_noreplace(self):
        for name in ("containers.conf", "storage.conf", "policy.json",
                     "registries.conf", "seccomp.json"):
            path = "/etc/containers/" + name
            lines = (PKG / "files" / "podman.filelist").read_text().splitlines()
            self.assertIn("%config(noreplace) " + path, lines, path)

    def test_replaces_podman_bin(self):
        self.assertRegex(self.spec, r"(?m)^Obsoletes:\s+podman-bin < ")
        self.assertRegex(self.spec, r"(?m)^Provides:\s+podman-bin = ")

    def test_units_and_generators_under_usr_lib(self):
        for path in ("/usr/lib/systemd/system/podman.socket",
                     "/usr/lib/systemd/user/podman.socket",
                     "/usr/lib/systemd/system-generators/podman-system-generator",
                     "/usr/lib/systemd/user-generators/podman-user-generator",
                     "/usr/libexec/podman/quadlet"):
            self.assertIn(path, self.files, path)


if __name__ == "__main__":
    unittest.main()
