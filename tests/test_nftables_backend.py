import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "package_specs"


def read(relative):
    with open(SPECS / relative, encoding="utf-8") as handle:
        return handle.read()


class NftablesBackendTest(unittest.TestCase):
    """netavark's default firewall driver has a working nft (issue #68)."""

    def test_netavark_requires_nftables(self):
        self.assertRegex(read("netavark/netavark.spec"),
                         r"(?m)^Requires:\s+nftables\s*$")

    def test_nft_is_built_with_json(self):
        # netavark's nftables crate pipes JSON rule sets to `nft -j -f -`;
        # without jansson nft rejects -j and every bridge network fails.
        spec = read("nftables/nftables.spec")
        self.assertIn("--with-json", spec)
        self.assertRegex(spec, r"(?m)^BuildRequires:\s+jansson\s*$")

    def test_nft_and_service_are_shipped(self):
        filelist = read("nftables/files/nftables.filelist").splitlines()
        self.assertIn("/usr/bin/nft", filelist)
        self.assertIn("/usr/lib/systemd/system/nftables.service", filelist)
        self.assertIn("%config(noreplace) /etc/nftables/osf/pf.os", filelist)

    def test_nftables_service_is_not_enabled_by_a_preset(self):
        for preset in SPECS.glob("*/files/*.preset"):
            self.assertNotRegex(preset.read_text(encoding="utf-8"),
                                r"(?m)^enable\s+nftables\.service",
                                preset)


if __name__ == "__main__":
    unittest.main()
