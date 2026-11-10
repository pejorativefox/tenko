import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")


def read(relative):
    with open(os.path.join(SPECS, relative), encoding="utf-8") as handle:
        return handle.read()


def spec_body(relative):
    return read(relative).split("%changelog", 1)[0]


class BluetoothStackTest(unittest.TestCase):
    """The desktop ships a Bluetooth stack: BlueZ, the systemd/D-Bus/udev
    integration, and the PulseAudio BlueZ backend as a separate module
    package.  Firmware stays in the vendor packs."""

    def test_bluez_build_features(self):
        body = spec_body("bluez/bluez.spec")
        for flag in ("--enable-library", "--enable-tools", "--enable-client",
                     "--enable-monitor", "--enable-systemd", "--enable-udev",
                     "--enable-datafiles", "--enable-hid2hci"):
            self.assertIn(flag, body)
        for flag in ("--disable-obex", "--disable-cups", "--disable-mesh",
                     "--disable-sixaxis", "--disable-deprecated",
                     "--disable-experimental"):
            self.assertIn(flag, body)

    def test_bluez_ships_the_service_integration(self):
        files = read("bluez/files/bluez.filelist")
        for path in ("/usr/lib/systemd/system/bluetooth.service",
                     "/usr/share/dbus-1/system-services/org.bluez.service",
                     "/etc/dbus-1/system.d/bluetooth.conf",
                     "/usr/lib/systemd/system-preset/40-tenko-bluetooth.preset",
                     "/usr/lib64/libbluetooth.so.3",
                     "/usr/lib/udev/hid2hci",
                     "/var/lib/bluetooth"):
            self.assertIn(path, files)
        self.assertIn("%config(noreplace) /etc/bluetooth/main.conf", files)

    def test_preset_enables_bluetooth_service(self):
        rules = [line.strip() for line in
                 read("bluez/files/40-tenko-bluetooth.preset").splitlines()
                 if line.strip() and not line.startswith("#")]
        self.assertIn("enable bluetooth.service", rules)

    def test_audio_modules_are_a_separate_package(self):
        body = spec_body("pulseaudio-bluez/pulseaudio-bluez.spec")
        self.assertIn("-D bluez5=enabled", body)
        self.assertIn("-D man=false", body)
        self.assertIn("Requires:   pulseaudio = %{version}", body)
        for module in ("module-bluetooth-discover", "module-bluetooth-policy",
                       "module-bluez5-discover", "module-bluez5-device",
                       "libbluez5-util"):
            self.assertIn(module, body)
        self.assertIn("default.pa.d/50-bluez.pa", body)
        # The main pulseaudio build keeps bluez5 off: the same module files
        # cannot be owned by two packages.
        main = spec_body("pulseaudio/pulseaudio.spec")
        self.assertIn("-D bluez5=disabled", main)
        self.assertNotIn("module-bluez5-device", main)

    def test_bluez_snippet_loads_the_modules(self):
        snippet = read("pulseaudio-bluez/files/50-bluez.pa")
        for line in ("load-module module-bluetooth-policy",
                     "load-module module-bluetooth-discover"):
            self.assertIn(line, snippet)
        # The installed pulseaudio default.pa has no Bluetooth block, so the
        # snippet is the only thing that loads the modules on a normal boot.
        self.assertEqual(snippet.count(".ifexists"), 2)

    def test_desktop_requires_the_stack(self):
        body = spec_body("xfce-desktop/xfce-desktop.spec")
        self.assertRegex(body, r"(?m)^Requires:\s+bluez\s*$")
        self.assertRegex(body, r"(?m)^Requires:\s+pulseaudio-bluez\s*$")

    def test_sources_are_pinned(self):
        self.assertIn("bluez-5.88.tar.xz", read("bluez/sources"))
        self.assertIn("sbc-2.2.tar.xz", read("sbc/sources"))
        self.assertIn("pulseaudio-17.0.tar.xz",
                      read("pulseaudio-bluez/sources"))


if __name__ == "__main__":
    unittest.main()
