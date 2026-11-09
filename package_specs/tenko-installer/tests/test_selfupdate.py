"""Tests for updating and restarting the running live installer."""

from __future__ import annotations

import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "files"))

import selfupdate  # noqa: E402
from runner import CommandError, Result  # noqa: E402


class FakeRunner:
    def __init__(
        self,
        *,
        current: str = "1:6-12",
        candidate: str = "1:6-13",
        query_rc: int = 0,
        upgrade_rc: int = 0,
        upgrade_error: Exception | None = None,
    ) -> None:
        self.current = current
        self.candidate = candidate
        self.query_rc = query_rc
        self.upgrade_rc = upgrade_rc
        self.upgrade_error = upgrade_error
        self.calls: list[tuple[str, ...]] = []

    @staticmethod
    def _result(argv, rc: int, output: str = "") -> Result:
        return Result(tuple(argv), rc, output, 0)

    def run(self, argv, **kwargs):
        argv = tuple(argv)
        self.calls.append(argv)
        if argv[0] == "rpm":
            output = self.current + "\n" if self.current else ""
            return self._result(argv, 0 if self.current else 1, output)
        if "repoquery" in argv:
            output = self.candidate + "\n" if self.candidate else ""
            return self._result(argv, self.query_rc, output)
        raise AssertionError("unexpected command: {}".format(argv))

    def run_streaming(self, argv, on_line, **kwargs):
        argv = tuple(argv)
        self.calls.append(argv)
        if self.upgrade_error is not None:
            raise self.upgrade_error
        on_line("Upgrading tenko-installer")
        return self._result(argv, self.upgrade_rc, "done")


class FakeProgress:
    def __init__(self, ui, title, total) -> None:
        self.ui = ui
        self.title = title
        self.steps: list[tuple[int, int, str]] = []
        self.lines: list[str] = []
        self.finished = False

    def set_step(self, index, total, name):
        self.steps.append((index, total, name))

    def line(self, text):
        self.lines.append(text)

    def finish(self):
        self.finished = True


class FakeUI:
    def __init__(self, choice: int = 0) -> None:
        self.choice = choice
        self.progress_views: list[FakeProgress] = []
        self.menus: list[tuple[str, list[str]]] = []
        self.messages: list[tuple[str, list[str]]] = []

    def progress(self, title, total):
        view = FakeProgress(self, title, total)
        self.progress_views.append(view)
        return view

    def menu(self, title, subtitle, rows, **kwargs):
        self.menus.append((title, [row.text for row in rows]))
        return self.choice

    def message(self, title, lines, **kwargs):
        self.messages.append((title, list(lines)))
        return 0


class FakeLogger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []
        self.console = None

    def info(self, event, **fields):
        self.events.append((event, fields))

    def error(self, event, **fields):
        self.events.append((event, fields))


class RepoCommandTest(unittest.TestCase):
    def test_repo_source_prefixes_local_paths_only(self):
        self.assertEqual(
            selfupdate.repo_source("/srv/repo"), "file:///srv/repo"
        )
        self.assertEqual(
            selfupdate.repo_source("https://example.invalid/6/"),
            "https://example.invalid/6/",
        )

    def test_available_update_returns_candidate(self):
        runner = FakeRunner(candidate="1:6-13")
        candidate = selfupdate.available_update(
            runner, "https://example.invalid/6/"
        )
        self.assertEqual(candidate, "1:6-13")
        repoquery = runner.calls[-1]
        self.assertIn("--nogpgcheck", repoquery)
        self.assertIn(
            "--repofrompath=tenko-live,https://example.invalid/6/",
            repoquery,
        )
        self.assertIn("--upgrades", repoquery)
        self.assertIn("tenko-installer", repoquery)

    def test_available_update_ignores_dnf_warnings(self):
        runner = FakeRunner(candidate="warning: something odd\n1:6-13\n")
        self.assertEqual(
            selfupdate.available_update(
                runner, "https://example.invalid/6/"
            ),
            "1:6-13",
        )

    def test_available_update_none_when_repoquery_fails(self):
        runner = FakeRunner(query_rc=1)
        self.assertIsNone(
            selfupdate.available_update(runner, "https://example.invalid/6/")
        )

    def test_installed_evr(self):
        runner = FakeRunner(current="1:6-12")
        self.assertEqual(selfupdate.installed_evr(runner), "1:6-12")


class OfferUpdateTest(unittest.TestCase):
    def make(self, **kwargs):
        ui = FakeUI(choice=kwargs.pop("choice", 0))
        runner = FakeRunner(**kwargs)
        logger = FakeLogger()
        return ui, runner, logger

    def test_accept_updates_and_requests_a_restart(self):
        ui, runner, logger = self.make()
        updated = selfupdate.offer_update(
            ui, runner, logger, "https://example.invalid/6/"
        )
        self.assertTrue(updated)
        upgrade = runner.calls[-1]
        self.assertIn("upgrade", upgrade)
        self.assertIn("tenko-installer", upgrade)
        self.assertEqual(
            ui.messages[-1][0],
            "Installer updated",
        )
        self.assertIn("restart", ui.messages[-1][1][-1].lower())
        self.assertIn(
            ("self-update", {"status": "updated", "candidate": "1:6-13"}),
            logger.events,
        )

    def test_declining_keeps_the_current_installer(self):
        ui, runner, logger = self.make(choice=1)
        updated = selfupdate.offer_update(
            ui, runner, logger, "https://example.invalid/6/"
        )
        self.assertFalse(updated)
        self.assertFalse(
            any("upgrade" in argv for argv in runner.calls)
        )
        self.assertEqual(ui.messages, [])

    def test_no_candidate_skips_the_menu(self):
        ui, runner, logger = self.make(candidate="")
        updated = selfupdate.offer_update(
            ui, runner, logger, "https://example.invalid/6/"
        )
        self.assertFalse(updated)
        self.assertEqual(ui.menus, [])
        self.assertEqual(ui.messages, [])

    def test_update_failure_continues_with_current_installer(self):
        ui, runner, logger = self.make(
            upgrade_error=CommandError(
                ("dnf", "upgrade"), 1, "network went away"
            )
        )
        updated = selfupdate.offer_update(
            ui, runner, logger, "https://example.invalid/6/"
        )
        self.assertFalse(updated)
        self.assertEqual(ui.messages[-1][0], "Installer update failed")
        self.assertTrue(
            any(
                event == "self-update"
                and fields.get("status") == "failed"
                for event, fields in logger.events
            )
        )


if __name__ == "__main__":
    unittest.main()
