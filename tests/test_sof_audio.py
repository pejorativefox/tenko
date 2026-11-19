"""Intel SOF audio: firmware, topology and the UCM profile.

The kernel binds Skylake-era Intel HDA controllers to sof-audio-pci, which
loads intel/sof/<platform>.ri and the matching topology from
/usr/lib/firmware/intel.  Upstream linux-firmware stopped carrying those
files, so they ship in sof-firmware; alsa-ucm-conf supplies the
Intel/sof-hda-dsp profile libasound needs to route speakers and headphones.
"""

import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")


def read(relative):
    with open(os.path.join(SPECS, relative), encoding="utf-8") as handle:
        return handle.read()


def spec_body(relative):
    return read(relative).split("%changelog", 1)[0]


def spec_lines(relative):
    lines = read(relative).splitlines()
    end = next((i for i, line in enumerate(lines)
                if line.startswith("%changelog")), len(lines))
    return lines[:end]


def has_field(lines, field, name):
    return any(line.startswith(field + ":") and
               line.split(":", 1)[1].strip() == name for line in lines)


class SofFirmwareTest(unittest.TestCase):
    def test_firmware_and_topology_files_are_listed(self):
        files = read("sof-firmware/files/sof-firmware.filelist")
        # sof-cfl is a symlink to the signed Cannon Lake image; CFL and CNL
        # are the platforms whose HDA controllers bind to SOF.
        for path in ("/usr/lib/firmware/intel/sof/sof-cfl.ri",
                     "/usr/lib/firmware/intel/sof/sof-cnl.ri",
                     "/usr/lib/firmware/intel/sof/intel-signed/sof-cnl.ri",
                     "/usr/lib/firmware/intel/sof-tplg/sof-hda-generic-4ch.tplg",
                     "/usr/lib/firmware/intel/sof-ipc4-tplg/"
                     "sof-hda-generic-4ch.tplg"):
            self.assertIn(path, files)

    def test_firmware_is_not_stripped(self):
        # The images are ELF containers; strip or a debug package would
        # corrupt them.
        body = spec_body("sof-firmware/sof-firmware.spec")
        for macro in ("%global debug_package %{nil}", "%global __strip /bin/true"):
            self.assertIn(macro, body)

    def test_desktop_profiles_carry_the_audio_stack(self):
        lines = spec_lines("xfce-desktop/xfce-desktop.spec")
        self.assertTrue(has_field(lines, "Requires", "alsa-ucm-conf"),
                        "xfce-desktop must require alsa-ucm-conf")
        self.assertTrue(has_field(lines, "Recommends", "sof-firmware"),
                        "xfce-desktop must recommend sof-firmware")
        hardware = spec_lines("xfce-desktop-hardware/xfce-desktop-hardware.spec")
        self.assertTrue(has_field(hardware, "Requires", "sof-firmware"),
                        "xfce-desktop-hardware must require sof-firmware")

    def test_ucm_conf_ships_the_sof_hda_profile(self):
        files = read("alsa-ucm-conf/files/alsa-ucm-conf.filelist")
        for path in ("/usr/share/alsa/ucm2/ucm.conf",
                     "/usr/share/alsa/ucm2/Intel/sof-hda-dsp/sof-hda-dsp.conf",
                     "/usr/share/alsa/ucm2/Intel/sof-hda-dsp/HiFi.conf",
                     "/usr/share/alsa/ucm2/conf.d/sof-hda-dsp/sof-hda-dsp.conf"):
            self.assertIn(path, files)
        body = spec_body("alsa-ucm-conf/alsa-ucm-conf.spec")
        self.assertIn("Requires:   alsa-lib", body)


if __name__ == "__main__":
    unittest.main()
