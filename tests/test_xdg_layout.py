import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "package_specs"


def read(relative):
    with open(REPO_ROOT / relative, encoding="utf-8") as handle:
        return handle.read()


def heredoc(text, path, marker="EOF2"):
    pattern = re.compile(
        r"cat > %%\{buildroot\}%s <<'%s'\n(.*?)\n%s"
        % (re.escape(path), re.escape(marker), re.escape(marker)),
        re.S,
    )
    match = pattern.search(text)
    if match is None:
        raise AssertionError("spec does not write " + path)
    return match.group(1)


def files_section(text):
    match = re.search(r"^%files(?: [^\n]*)?\n(.*?)(?=^%[a-zA-Z])", text,
                      re.S | re.MULTILINE)
    if match is None:
        raise AssertionError("spec has no %files section")
    return [line.strip() for line in match.group(1).splitlines() if line.strip()]


class XdgLayoutTest(unittest.TestCase):
    """XDG user dirs, ~/.local/bin and the remaining FHS directories."""

    def test_xdg_user_dirs_tracks_latest_stable(self):
        spec = read("package_specs/xdg-user-dirs/xdg-user-dirs.spec")
        sources = read("package_specs/xdg-user-dirs/sources")
        self.assertIn("Version:    0.20", spec)
        self.assertIn("GPL-2.0-or-later", spec)
        self.assertIn(
            "d1d1354a518bf7fff8e304871e2e164f "
            "https://user-dirs.freedesktop.org/releases/"
            "xdg-user-dirs-0.20.tar.xz xdg-user-dirs-0.20.tar.xz",
            sources,
        )

    def test_desktop_profiles_install_xdg_user_dirs(self):
        for name in ("xfce-desktop", "xfce-desktop-core"):
            spec = read("package_specs/%s/%s.spec" % (name, name))
            self.assertIn("Requires:   xdg-user-dirs", spec, name)

    def test_user_dirs_autostart_and_unit_are_shipped(self):
        filelist = read(
            "package_specs/xdg-user-dirs/files/xdg-user-dirs.filelist"
        )
        self.assertIn("/etc/xdg/autostart/xdg-user-dirs.desktop", filelist)
        self.assertIn("/usr/lib/systemd/user/xdg-user-dirs.service", filelist)

    def test_local_bin_is_on_path_in_login_and_interactive_shells(self):
        spec = read("package_specs/tenko-sysconfig/tenko-sysconfig.spec")
        bashrc = heredoc(spec, "/etc/bashrc")
        skel = heredoc(spec, "/etc/skel/.bashrc")
        guard = 'case ":$PATH:" in'
        self.assertIn(guard, bashrc)
        self.assertIn('*:$HOME/.local/bin:*)', bashrc)
        self.assertIn('PATH="$HOME/.local/bin:$PATH"', bashrc)
        self.assertIn("export PATH", bashrc)
        # The guard must not append unconditionally on every source.
        self.assertEqual(bashrc.count(guard), 1)
        # Both startup paths reach the shared file.
        self.assertIn(". /etc/bashrc", heredoc(spec, "/etc/profile"))
        self.assertIn(". /etc/bashrc", skel)

    def test_basefs_creates_the_remaining_fhs_directories(self):
        spec = read("package_specs/tenko-basefs/tenko-basefs.spec")
        mkdir = next(
            line for line in spec.splitlines()
            if line.startswith("mkdir -p %{buildroot}/{")
        )
        self.assertIn(",media}", mkdir)
        self.assertIn("lib,local}", mkdir)
        self.assertIn(
            "local/{bin,etc,games,include,lib,man,sbin,share,src}", mkdir
        )
        entries = files_section(spec)
        for path in (
            "/media",
            "/var/local",
            "/usr/local/etc",
            "/usr/local/games",
            "/usr/local/include",
            "/usr/local/man",
            "/usr/local/share",
            "/usr/local/src",
        ):
            self.assertIn(path, entries)

    def test_var_run_and_var_lock_come_from_systemd_tmpfiles(self):
        filelist = read("package_specs/systemd/files/systemd.filelist")
        self.assertIn("/usr/lib/tmpfiles.d/var.conf", filelist)
        self.assertIn("/usr/lib/tmpfiles.d/legacy.conf", filelist)

    def test_matrix_marks_the_xdg_rows_implemented(self):
        matrix = read("docs/freedesktop.md")
        for row in ("`basedir`", "`fhs`", "`XDG user dirs`"):
            pattern = re.compile(
                r"^\| " + re.escape(row) + r" \|[^|]*\| ([^|]+?) \|", re.MULTILINE
            )
            match = pattern.search(matrix)
            self.assertIsNotNone(match, row)
            self.assertEqual(match.group(1).strip(), "implemented", row)

    @unittest.skipUnless(
        shutil.which("rpm2cpio") and shutil.which("cpio"),
        "rpm2cpio/cpio not installed",
    )
    def test_user_dirs_update_creates_and_preserves_directories(self):
        binary_dir = self._extract_user_dirs()
        if binary_dir is None:
            self.skipTest("no built xdg-user-dirs RPM and no host xdg-user-dirs")
        home = Path(tempfile.mkdtemp(prefix="xdg-user-dirs-test-"))
        self.addCleanup(shutil.rmtree, home, True)
        env = os.environ.copy()
        env.update({
            "HOME": str(home),
            "XDG_CONFIG_HOME": str(home / ".config"),
            "XDG_CONFIG_DIRS": str(binary_dir.parent.parent / "etc" / "xdg"),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
        })
        update = binary_dir / "xdg-user-dirs-update"
        query = binary_dir / "xdg-user-dir"
        subprocess.run([str(update), "--force"], env=env, check=True)
        self.assertTrue((home / ".config" / "user-dirs.dirs").is_file())
        for name in ("Desktop", "Documents", "Downloads", "Music",
                     "Pictures", "Videos"):
            self.assertTrue((home / name).is_dir(), name)
        result = subprocess.run(
            [str(query), "DESKTOP"], env=env, check=True,
            capture_output=True, text=True,
        )
        self.assertEqual(result.stdout.strip(), str(home / "Desktop"))
        # Existing files are not moved or overwritten on a later run.
        marker = home / "Desktop" / "keep.txt"
        marker.write_text("keep\n", encoding="utf-8")
        subprocess.run([str(update), "--force"], env=env, check=True)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep\n")

    def _extract_user_dirs(self):
        host = shutil.which("xdg-user-dirs-update")
        if host:
            return Path(host).parent
        rpms = sorted(
            REPO_ROOT.glob("build/**/xdg-user-dirs-0.20-1*.rpm"),
            key=lambda path: path.stat().st_mtime,
        )
        if not rpms:
            return None
        tmp = Path(tempfile.mkdtemp(prefix="xdg-user-dirs-rpm-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        producer = subprocess.Popen(
            ["rpm2cpio", str(rpms[-1])], stdout=subprocess.PIPE
        )
        subprocess.run(
            ["cpio", "-idm", "--quiet", "./usr/bin/*", "./etc/xdg/*"],
            stdin=producer.stdout, cwd=tmp, check=False,
        )
        if producer.stdout:
            producer.stdout.close()
        producer.wait()
        return tmp / "usr" / "bin"


if __name__ == "__main__":
    unittest.main()
