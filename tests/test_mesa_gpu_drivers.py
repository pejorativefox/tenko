import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MESA = os.path.join(REPO_ROOT, "package_specs", "mesa")

# Software/virtual drivers plus the hardware drivers needed by the GPUs the
# distro targets: Intel Gen4-7.5 (crocus), Intel Gen8+ (iris), AMD GCN1+
# (radeonsi) and AMD R600-Evergreen (r600).
EXPECTED_DRIVERS = {
    "llvmpipe", "virgl", "crocus", "iris", "radeonsi", "r600",
}
EXPECTED_DRI_FILES = {
    "crocus_dri.so", "iris_dri.so", "radeonsi_dri.so", "r600_dri.so",
}


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def spec_body():
    text = read(os.path.join(MESA, "mesa.spec"))
    return text.split("%changelog", 1)[0]


class MesaGpuDriversTest(unittest.TestCase):
    """The mesa package must build and ship hardware gallium drivers.

    A build restricted to llvmpipe/virgl looks fine on a VM but leaves real
    Intel/AMD systems on the software rasterizer.
    """

    def test_gallium_drivers_include_hardware(self):
        match = re.search(r"-Dgallium-drivers=([^\s\\]+)", spec_body())
        self.assertIsNotNone(match, "mesa.spec has no -Dgallium-drivers")
        drivers = set(match.group(1).split(","))
        self.assertEqual(EXPECTED_DRIVERS - drivers, set())

    def test_filelist_ships_hardware_dri_drivers(self):
        filelist = read(os.path.join(MESA, "files", "mesa.filelist"))
        files = {os.path.basename(line.strip()) for line in filelist.splitlines()}
        self.assertEqual(EXPECTED_DRI_FILES - files, set())


if __name__ == "__main__":
    unittest.main()
