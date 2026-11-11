"""podman-bin's containers.conf finds every helper the bundle ships."""

import re
import unittest
from pathlib import Path

PKG = Path(__file__).resolve().parents[1] / "package_specs" / "podman-bin"


class PodmanHelperPathsTest(unittest.TestCase):
    def test_helper_dirs_cover_pasta(self):
        conf = (PKG / "files" / "containers.conf").read_text()
        match = re.search(r"^helper_binaries_dir\s*=\s*\[(.*)\]", conf, re.M)
        self.assertIsNotNone(match)
        dirs = re.findall(r'"([^"]+)"', match.group(1))
        shipped = (PKG / "files" / "podman-bin.filelist").read_text().split()
        for helper in ("pasta", "passt", "netavark", "aardvark-dns", "conmon"):
            found = [d for d in dirs
                     if any(re.fullmatch(r"/opt/podman(-[\d.]+)?" + re.escape(
                         d[len("/opt/podman"):]) + "/" + helper, f)
                         for f in shipped)]
            self.assertTrue(found, "{} is not in helper_binaries_dir {}".format(
                helper, dirs))


if __name__ == "__main__":
    unittest.main()
