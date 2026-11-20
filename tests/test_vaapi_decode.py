import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")


def spec_body(relative):
    with open(os.path.join(SPECS, relative), encoding="utf-8") as handle:
        return handle.read().split("%changelog", 1)[0]


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


class VaapiDecodeTest(unittest.TestCase):
    """mpv plays through FFmpeg's VAAPI decoders.  Without its EGL/VAAPI
    interop the decoders still run, but every decoded frame is copied back
    through system memory (vaapi-copy): the player builds and plays, so the
    loss is silent."""

    def test_mpv_builds_the_vaapi_interop(self):
        body = spec_body("mpv/mpv.spec")
        self.assertIn("-Dvaapi=enabled", body,
                      "mpv must build the EGL/VAAPI interop")
        self.assertIn("-Degl=enabled", body,
                      "the VAAPI interop shares surfaces with EGL")
        self.assertIn("-Ddrm=enabled", body,
                      "drm plus egl builds the GL dmabuf interop")
        self.assertIn("libva", requires(body),
                      "mpv must build against libva")
        self.assertIn("libdrm", requires(body),
                      "the GL dmabuf interop builds against libdrm")
        self.assertIn("libdisplay-info", requires(body),
                      "the drm feature needs libdisplay-info")


if __name__ == "__main__":
    unittest.main()
