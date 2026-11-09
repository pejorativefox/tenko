"""Tests for the preflight network setup/retry helpers."""

from __future__ import annotations

import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "files"))

import main  # noqa: E402
from probe import Check  # noqa: E402


class FakeRunner:
    def __init__(self, output: str = "") -> None:
        self.output = output
        self.calls = []
        self.env = {"PATH": "/usr/bin:/usr/sbin:/bin:/sbin"}

    def run(self, argv, **kwargs):
        self.calls.append(list(argv))
        return SimpleNamespace(output=self.output)


class FakeUI:
    def __init__(self, answers) -> None:
        self.answers = list(answers)
        self.menus = []
        self.messages = []

    def menu(self, title, subtitle, rows, **kwargs) -> int:
        self.menus.append((title, [row.text for row in rows]))
        return self.answers.pop(0)

    def message(self, title, lines, **kwargs) -> int:
        self.messages.append((title, list(lines)))
        return 0


class NetworkStatusTest(unittest.TestCase):
    def test_terse_fields_unescape_colons(self):
        self.assertEqual(
            main._split_nmcli_fields("wlan0:wifi:connected:Home\\:Net"),
            ["wlan0", "wifi", "connected", "Home:Net"],
        )

    def test_status_lines_are_formatted(self):
        runner = FakeRunner("wlan0:wifi:connected:Home\\:Net\n")
        with mock.patch(
            "main.shutil.which", return_value="/usr/bin/nmcli"
        ):
            lines = main.network_status_lines(runner)
        self.assertEqual(len(lines), 1)
        self.assertIn("wlan0", lines[0])
        self.assertIn("connected", lines[0])
        self.assertIn("Home:Net", lines[0])
        self.assertEqual(runner.calls[0][0], "nmcli")

    def test_missing_nmcli_is_reported(self):
        with mock.patch("main.shutil.which", return_value=None):
            lines = main.network_status_lines(FakeRunner())
        self.assertIn("not installed", lines[0])


class RepositoryCheckTest(unittest.TestCase):
    def test_only_a_failed_repository_counts(self):
        self.assertTrue(
            main.repository_check_failed(
                [Check(False, "package repository", "unreachable")]
            )
        )
        self.assertFalse(
            main.repository_check_failed(
                [Check(True, "package repository", "ok")]
            )
        )
        self.assertFalse(
            main.repository_check_failed([Check(False, "Secure Boot", "on")])
        )


class NetworkSetupScreenTest(unittest.TestCase):
    def setUp(self):
        self.runner = FakeRunner("eth0:ethernet:connected:wired\n")

    def test_choose_retry(self):
        ui = FakeUI([1])
        with mock.patch("main.launch_nmtui") as launch:
            self.assertTrue(
                main.network_setup_screen(ui, self.runner, mock.Mock())
            )
        launch.assert_not_called()
        self.assertEqual(ui.menus[0][0], "Network required")

    def test_choose_exit(self):
        ui = FakeUI([2])
        self.assertFalse(
            main.network_setup_screen(ui, self.runner, mock.Mock())
        )

    def test_choose_nmtui_then_retry(self):
        ui = FakeUI([0])
        with mock.patch("main.launch_nmtui", return_value=True) as launch:
            self.assertTrue(
                main.network_setup_screen(ui, self.runner, mock.Mock())
            )
        launch.assert_called_once()

    def test_unavailable_nmtui_returns_to_the_menu(self):
        ui = FakeUI([0, 1])
        with mock.patch("main.launch_nmtui", return_value=False):
            self.assertTrue(
                main.network_setup_screen(ui, self.runner, mock.Mock())
            )
        self.assertEqual(ui.messages[0][0], "Network setup is unavailable")
        self.assertEqual(len(ui.menus), 2)


class NmtuiLaunchTest(unittest.TestCase):
    def setUp(self):
        self.runner = FakeRunner()
        self.runner.env = {"LC_ALL": "C", "LANG": "C", "PATH": "/usr/bin"}

    def test_environment_is_utf8(self):
        env = main.nmtui_env(self.runner)
        self.assertEqual(env["LC_ALL"], "C.UTF-8")
        self.assertEqual(env["LANG"], "C.UTF-8")
        self.assertNotIn("LC_CTYPE", env)
        self.assertEqual(env["TERM"], "kmscon")

    def test_runs_nmtui_in_kmscon_on_a_spare_vt(self):
        programs = {
            "nmtui-connect": "/usr/bin/nmtui-connect",
            "kmscon": "/usr/bin/kmscon",
            "chvt": "/usr/bin/chvt",
        }
        calls = []

        def fake_run(argv, **kwargs):
            calls.append((list(argv), kwargs.get("env", {})))
            return SimpleNamespace(returncode=0)

        with mock.patch(
            "main.shutil.which",
            side_effect=lambda name, path=None: programs.get(name),
        ), mock.patch("main.subprocess.run", fake_run):
            self.assertTrue(
                main.launch_nmtui(self.runner, mock.Mock(), ui=None)
            )
        self.assertEqual(calls[0][0], ["/usr/bin/chvt", "3"])
        self.assertEqual(calls[1][0][0], "/usr/bin/kmscon")
        self.assertIn("--vt=tty3", calls[1][0])
        self.assertIn("--oneshot", calls[1][0])
        self.assertIn("--no-reset-env", calls[1][0])
        self.assertIn("/usr/bin/nmtui-connect", calls[1][0])
        self.assertEqual(calls[2][0], ["/usr/bin/chvt", "1"])
        self.assertEqual(calls[1][1]["LC_ALL"], "C.UTF-8")

    def test_falls_back_to_the_current_tty(self):
        calls = []

        def fake_run(argv, **kwargs):
            calls.append(list(argv))
            return SimpleNamespace(returncode=0)

        with mock.patch(
            "main.shutil.which",
            side_effect=lambda name, path=None: (
                "/usr/bin/nmtui" if name in ("nmtui", "nmtui-connect")
                else None
            ),
        ), mock.patch("main.subprocess.run", fake_run):
            self.assertTrue(
                main.launch_nmtui(self.runner, mock.Mock(), ui=None)
            )
        self.assertEqual(calls, [["/usr/bin/nmtui"]])


class PlainRetryTest(unittest.TestCase):
    def test_quit_keeps_the_failed_checks(self):
        checks = [Check(False, "package repository", "unreachable")]
        with mock.patch("main._ask", return_value="q"):
            returned, ok = main.plain_network_retry(
                mock.Mock(),
                SimpleNamespace(repo="https://example.invalid/"),
                mock.Mock(),
                FakeRunner(),
                checks,
                False,
            )
        self.assertEqual(returned, checks)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
