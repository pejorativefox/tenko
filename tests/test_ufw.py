"""UFW is opt-in and restores rules before networking without late-boot cycles."""

import os
import re
import subprocess
import unittest
import uuid
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1] / "package_specs" / "ufw"


class UfwPackagingTest(unittest.TestCase):
    def test_installation_does_not_activate_the_firewall(self):
        spec = (PACKAGE / "ufw.spec").read_text()
        body = spec.split("\n%changelog", 1)[0]
        self.assertNotRegex(body, r"(?m)^%(?:post|pre|postun|preun)\b")
        filelist = (PACKAGE / "files" / "ufw.filelist").read_text()
        self.assertNotIn(".target.wants/", filelist)
        self.assertNotIn("/system-preset/", filelist)
        self.assertIn('ENABLED=no', spec)
        self.assertIn('IPV6=yes', spec)
        self.assertIn('do_checks = True', spec)

    def test_service_is_early_boot_and_uses_packaged_helpers(self):
        unit = (PACKAGE / "files" / "ufw.service").read_text()
        self.assertIn("DefaultDependencies=no", unit)
        self.assertIn("Before=network-pre.target", unit)
        self.assertIn("Wants=network-pre.target", unit)
        self.assertIn("After=local-fs.target", unit)
        self.assertIn("After=systemd-sysctl.service", unit)
        self.assertIn("Conflicts=shutdown.target", unit)
        self.assertIn("Before=shutdown.target", unit)
        self.assertIn("RemainAfterExit=yes", unit)
        self.assertIn("ExecStart=/usr/lib/ufw/ufw-init start quiet", unit)
        self.assertIn("ExecStop=/usr/lib/ufw/ufw-init stop", unit)
        self.assertIn("ExecReload=/usr/lib/ufw/ufw-init force-reload", unit)

    def test_all_shipped_configuration_preserves_local_edits(self):
        entries = (PACKAGE / "files" / "ufw.filelist").read_text().splitlines()
        config = [line for line in entries
                  if "/etc/" in line and not line.startswith("%dir ")]
        self.assertTrue(config)
        self.assertTrue(all(line.startswith("%config(noreplace) ")
                            for line in config), config)
        for name in ("ufw.conf", "user.rules", "user6.rules"):
            self.assertIn("%config(noreplace) /etc/ufw/" + name, entries)

    def test_build_checks_cannot_run_root_firewall_tests(self):
        spec = (PACKAGE / "ufw.spec").read_text()
        check = re.search(r"(?ms)^%check\n(.*?)^%files", spec).group(1)
        commands = [line for line in check.splitlines()
                    if line.strip() and not line.startswith("#")]
        self.assertEqual(commands, ["python3 tests/unit/runner.py"])
        self.assertNotIn("UFW_SKIP_CHECKS=", spec)


@unittest.skipUnless(os.environ.get("TENKO_UFW_RPM"),
                     "set TENKO_UFW_RPM to test the built RPM in an isolated container")
class UfwRpmTest(unittest.TestCase):
    def test_installed_firewall_in_private_network_namespace(self):
        root = PACKAGE.parents[1]
        common = subprocess.check_output(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=root, text=True).strip()
        mirror = Path(os.environ.get(
            "TENKO_REPO_CACHE", str(Path(common).parent / "build/cache/repo")))
        rpm = Path(os.environ["TENKO_UFW_RPM"]).resolve(strict=True)
        script = r"""
set -eu
test "$(readlink /proc/self/ns/net)" != "$HOST_NETNS"
dnf -y --disablerepo='*' --repofrompath=cache,file:///repo/cache \
    --setopt=cache.gpgcheck=0 --nogpgcheck install /package.rpm
ufw version
ufw app list
ufw --dry-run allow 22/tcp
ufw --dry-run allow from 2001:db8::/32 to any port 443 proto tcp
grep -qx 'ENABLED=no' /etc/ufw/ufw.conf
grep -qx 'IPV6=yes' /etc/default/ufw
python3 -c 'import ufw.common; assert ufw.common.do_checks; assert ufw.common.state_dir == "/usr/lib/ufw"'
test "$(systemctl is-enabled ufw.service || :)" = disabled
systemd-analyze verify --man=no /usr/lib/systemd/system/ufw.service
if [ "$KERNEL_TESTS" = 1 ]; then
    ufw status | grep -Fx 'Status: inactive'
    ufw allow 22/tcp
    ufw allow from 2001:db8::/32 to any port 443 proto tcp
    ufw limit 2222/tcp
    ufw --force enable
    ufw status verbose
    iptables -S ufw-user-input | grep -- '--dport 22 -j ACCEPT'
    ip6tables -S ufw6-user-input | grep -- '--dport 443 -j ACCEPT'
    iptables -S ufw-user-input | grep -- '--dport 2222.*--set'
    iptables -S ufw-user-input | grep -- '--dport 2222.*--update'
    ufw reload
    /usr/lib/ufw/ufw-init stop
    /usr/lib/ufw/ufw-init start
    ufw status | grep -Fx 'Status: active'
    ip6tables -S ufw6-user-input | grep -- '--dport 443 -j ACCEPT'
    ufw --force disable
    ufw status | grep -Fx 'Status: inactive'
fi
"""
        name = "tenko-ufw-test-" + uuid.uuid4().hex
        try:
            result = subprocess.run([
                "podman", "run", "--rm", "--name=" + name,
                "--network=none", "--cap-add=NET_ADMIN",
                "-e", "HOST_NETNS=" + os.readlink("/proc/self/ns/net"),
                "-e", "KERNEL_TESTS=" + os.environ.get("TENKO_UFW_KERNEL_TESTS", "0"),
                "-v", str(mirror.resolve()) + ":/repo/cache:ro,z",
                "-v", str(rpm) + ":/package.rpm:ro,z",
                os.environ.get("BUILDROOT_IMAGE", "localhost/tenko/buildroot:r6"),
                "/usr/bin/bash", "-c", script,
            ], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
        finally:
            subprocess.run(["podman", "rm", "--force", name],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
