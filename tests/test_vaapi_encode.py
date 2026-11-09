import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")


def read(relative):
    with open(os.path.join(SPECS, relative), encoding="utf-8") as handle:
        return handle.read()


def spec_body(relative):
    return read(relative).split("%changelog", 1)[0]


def requires(text):
    names = set()
    for line in text.splitlines():
        match = re.match(r"^(?:Build)?Requires:\s+(.*)$", line)
        if not match:
            continue
        for item in match.group(1).split(","):
            name = item.strip().split()[0] if item.strip() else ""
            if name and not name.startswith("%"):
                names.add(name)
    return names


class VaapiEncodeTest(unittest.TestCase):
    """gpu-screen-recorder asks FFmpeg for h264_vaapi and libx264, and the
    h264_vaapi encoder needs Mesa's gallium VA driver.  If either side loses
    the encoder, the recorder builds but cannot record."""

    def test_mesa_builds_the_va_driver(self):
        body = spec_body("mesa/mesa.spec")
        self.assertIn("-Dgallium-va=enabled", body,
                      "mesa must build the Gallium VA-API frontend")
        match = re.search(r"-Dvideo-codecs=([^\s\\]+)", body)
        self.assertIsNotNone(match, "mesa.spec has no -Dvideo-codecs")
        codecs = set(match.group(1).split(","))
        self.assertEqual({"h264enc", "h265enc"} - codecs, set(),
                         "mesa must build the H.264 and HEVC encoders")
        self.assertIn("libva", requires(body),
                      "mesa must build against libva")

    def test_mesa_filelist_ships_the_va_driver(self):
        entries = {
            os.path.basename(line.strip())
            for line in read("mesa/files/mesa.filelist").splitlines()
        }
        for driver in ("radeonsi_drv_video.so", "r600_drv_video.so"):
            self.assertIn(driver, entries,
                          "mesa filelist is missing %s" % driver)

    def test_ffmpeg_builds_vaapi_and_x264(self):
        body = spec_body("ffmpeg/ffmpeg.spec")
        self.assertIn("--enable-vaapi", body)
        self.assertIn("--enable-libx264", body)
        required = requires(body)
        self.assertIn("libva", required)
        self.assertIn("libx264", required)

    def test_recorder_is_wired_to_the_new_encoders(self):
        body = spec_body("gpu-screen-recorder/gpu-screen-recorder.spec")
        self.assertRegex(body, r"(?m)^Version:\s+6\.1\.7$")
        self.assertIn("Requires:   ffmpeg >= 9.0.2-3", body)
        self.assertIn("Requires:   mesa >= 26.2.3-8", body)
        self.assertIn(
            "setcap cap_sys_admin+ep /usr/bin/gsr-kms-server", body)
        self.assertIn("-Dsystemd=true", body)
        self.assertIn("-Dnvidia_suspend_fix=true", body)
        entries = read("gpu-screen-recorder/files/gpu-screen-recorder.filelist")
        self.assertIn("/usr/lib/systemd/user/gpu-screen-recorder.service", entries)
        self.assertIn("/usr/lib/modprobe.d/gsr-nvidia.conf", entries)

    def test_recorder_records_its_source(self):
        sources = read("gpu-screen-recorder/sources")
        self.assertIn(
            "https://dec05eba.com/snapshot/gpu-screen-recorder.git.6.1.7.tar.gz",
            sources)
        self.assertIn("gpu-screen-recorder-6.1.7.tar.gz", sources)


if __name__ == "__main__":
    unittest.main()
