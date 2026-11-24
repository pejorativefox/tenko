"""The official Java 21 JDK is a complete, shell-independent /opt bundle."""

import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

PKG = Path(__file__).resolve().parents[1] / "package_specs" / "temurin21-bin"
PROFILE = PKG / "files" / "temurin21.sh"


class Temurin21ProfileTest(unittest.TestCase):
    def test_profile_is_posix_silent_idempotent_and_exports_stable_java_home(self):
        # An unavailable PATH catches accidental dependencies on outside tools.
        # A child shell checks that JAVA_HOME is exported, not just assigned.
        script = '''
            set -eu
            . "$1"
            . "$1"
            /bin/sh -c 'printf "%s\\n%s\\n" "$JAVA_HOME" "$PATH"'
        '''
        for path in ("/usr/bin:/bin", "/unavailable", ""):
            for java_home in (None, "/opt/another-jdk"):
                with self.subTest(path=path, java_home=java_home):
                    env = {"PATH": path}
                    if java_home is not None:
                        env["JAVA_HOME"] = java_home
                    result = subprocess.run(
                        ["/bin/sh", "-c", script, "sh", str(PROFILE)],
                        env=env, capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                    self.assertEqual(result.stdout, "/opt/temurin21\n" + path + "\n")

    def test_profile_does_not_create_a_path_only_entrypoint(self):
        text = PROFILE.read_text(encoding="utf-8")
        # JAVA_HOME is the only environment integration needed by this bundle.
        active = "\n".join(line for line in text.splitlines()
                           if not line.lstrip().startswith("#"))
        self.assertNotRegex(active, r"\bPATH\s*=")


class Temurin21PackageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = (PKG / "temurin21-bin.spec").read_text(encoding="utf-8")
        cls.body = cls.spec.split("%changelog", 1)[0]
        cls.filelist = (PKG / "files" / "temurin21-bin.filelist").read_text(
            encoding="utf-8")

    def header(self, name):
        match = re.search(r"(?m)^" + re.escape(name) + r":\s+(\S+)", self.spec)
        self.assertIsNotNone(match, "missing " + name)
        return match.group(1)

    def build_number(self):
        match = re.search(r"(?m)^%(?:global|define)\s+jdk_build\s+(\d+)\s*$",
                          self.spec)
        self.assertIsNotNone(match, "missing numeric jdk_build macro")
        return match.group(1)

    def expanded_filelist(self):
        # Filelists may use either the standard path macros or spec globals.
        macros = dict(re.findall(
            r"(?m)^%(?:global|define)\s+(\w+)\s+([^\n]+)", self.body))
        macros.update(version=self.header("Version"), name="temurin21-bin",
                      _prefix="/usr", _bindir="/usr/bin", _sysconfdir="/etc")
        text = self.filelist
        for _ in range(10):
            expanded = re.sub(r"%\{(\w+)\}",
                              lambda m: macros.get(m.group(1), m.group(0)), text)
            if expanded == text:
                break
            text = expanded
        return text

    def payload_paths(self):
        return {line.split()[-1] for line in self.expanded_filelist().splitlines()
                if line.strip() and not line.lstrip().startswith("#")}

    def home(self):
        return "/opt/temurin21-" + self.header("Version") + "+" + self.build_number()

    def test_java21_official_full_jdk_binary_source_is_pinned(self):
        self.assertEqual(self.header("Name"), "temurin21-bin")
        version = self.header("Version")
        self.assertRegex(version, r"^21(?:\.\d+)+$")
        build = self.build_number()
        records = [line.split() for line in
                   (PKG / "sources").read_text(encoding="utf-8").splitlines()
                   if line.strip() and not line.lstrip().startswith("#")]
        assets = [record for record in records
                  if "OpenJDK21U-jdk_" in record[1]]
        self.assertEqual(len(assets), 1, "one official full-JDK archive is required")
        digest, url, *_ = assets[0]
        self.assertRegex(digest, r"^[0-9a-fA-F]{32}$")
        parsed = urlsplit(url)
        self.assertEqual((parsed.scheme, parsed.netloc), ("https", "github.com"))
        self.assertEqual(
            unquote(parsed.path),
            "/adoptium/temurin21-binaries/releases/download/jdk-" +
            version + "+" + build +
            "/OpenJDK21U-jdk_x64_linux_hotspot_" + version + "_" + build + ".tar.gz")
        self.assertEqual(parsed.query, "")
        self.assertEqual(parsed.fragment, "")

    def test_versioned_payload_and_stable_home_are_owned(self):
        paths = self.payload_paths()
        self.assertIn(self.home(), paths)
        self.assertIn("/opt/temurin21", paths)
        self.assertIn("ln -s", self.body)
        self.assertIn("/opt/temurin21", self.body)

    def test_all_shipped_jdk_commands_have_usr_bin_entrypoints(self):
        paths = self.payload_paths()
        prefix = self.home() + "/bin/"
        commands = {path[len(prefix):] for path in paths
                    if path.startswith(prefix) and "/" not in path[len(prefix):]}
        # Check both developer tools and runtime/diagnostic commands, rather
        # than accepting a JRE with just java and keytool.
        self.assertTrue(
            {"java", "javac", "jar", "javadoc", "javap", "jshell", "jcmd",
             "jlink", "jmod", "jpackage", "jconsole", "keytool"} <= commands,
            "the payload must contain the full JDK command set")
        for command in sorted(commands):
            with self.subTest(command=command):
                self.assertIn("/usr/bin/" + command, paths)
        self.assertTrue("%{_bindir}" in self.body or "/usr/bin" in self.body)

    def test_full_modules_and_desktop_native_libraries_are_preserved(self):
        paths = self.payload_paths()
        for relative in ("lib/modules", "jmods/java.base.jmod",
                         "jmods/java.desktop.jmod", "jmods/jdk.compiler.jmod",
                         "lib/libawt.so", "lib/libawt_xawt.so",
                         "lib/libsplashscreen.so", "lib/server/libjvm.so"):
            with self.subTest(relative=relative):
                self.assertIn(self.home() + "/" + relative, paths)

    def test_gtk_integration_uses_the_actual_tenko_package_name(self):
        # gtk3 is the spec directory; its RPM is named gtk+.
        self.assertRegex(self.body, r"(?m)^Recommends:\s+gtk\+\s*$")

    def test_upstream_configuration_is_preserved_on_upgrade(self):
        # Stable configuration paths keep edits active when a patch update
        # redirects /opt/temurin21 to a differently versioned payload.
        prefix = "/etc/temurin21/"
        lines = self.expanded_filelist().splitlines()
        configs = [line for line in lines if line.split() and
                   line.split()[-1].startswith(prefix) and
                   not line.startswith("%dir ")]
        self.assertTrue(configs, "the full upstream conf directory is required")
        for line in configs:
            with self.subTest(config=line):
                self.assertTrue(line.startswith("%config(noreplace) "), line)
        for relative in ("net.properties", "security/java.security"):
            self.assertIn(prefix + relative, self.payload_paths())
        self.assertIn(self.home() + "/conf", self.payload_paths())
        self.assertRegex(
            self.body,
            r"ln\s+-s\s+(?:%\{_sysconfdir\}|/etc)/temurin21\s+"
            r"\S*%\{java_payload\}/conf")

    def test_java_uses_the_system_managed_ca_store(self):
        self.assertRegex(self.body, r"(?m)^Requires:\s+make-ca\s*$")
        self.assertIn(self.home() + "/lib/security/cacerts", self.payload_paths())
        self.assertRegex(
            self.body,
            r"ln\s+-s[fnhv]*\s+/etc/pki/tls/java/cacerts\s+"
            r"(?:\\\n\s*)?\S*lib/security/cacerts")

    def test_profile_is_installed_as_preserved_configuration(self):
        self.assertRegex(self.body, r"(?m)^Source\d*:\s+temurin21\.sh\s*$")
        self.assertIn("/profile.d/temurin21.sh", self.body)
        self.assertIn(
            "%config(noreplace) /etc/profile.d/temurin21.sh",
            self.expanded_filelist().splitlines())

    def test_static_filelist_has_no_wildcards(self):
        self.assertRegex(
            self.body,
            r"(?m)^%files\s+-f\s+%\{_sourcedir\}/temurin21-bin\.filelist\s*$")
        for line in self.filelist.splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                self.assertNotRegex(line, r"[*?\[]", line)

    def test_no_server_service_eula_or_devel_split(self):
        self.assertNotRegex(self.body, r"(?m)^%package\b")
        for path in self.payload_paths():
            self.assertNotRegex(path, r"/systemd/|/init\.d/|\.service$|\.socket$")
            self.assertNotRegex(path, r"(?i)(?:^|/)eula(?:[./]|$)")
        self.assertNotRegex(self.body, r"(?m)^\s*(?:systemctl|useradd|groupadd)\b")


if __name__ == "__main__":
    unittest.main()
