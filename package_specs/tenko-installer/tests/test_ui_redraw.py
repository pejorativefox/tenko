"""Tests for console repainting in the ncurses UI.

The installer runs on the kernel console (tty1/fbcon) on the live medium,
so kernel printk output is written straight over the curses screen.  The
UI must force full repaints and wake up while idle so that damage does not
stay on screen (especially the header and footer, first seen after the
filesystem-creation step).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "files"))

import curses  # noqa: E402

from ui import (  # noqa: E402
    REDRAW_INTERVAL_MS,
    CursesUI,
    ProgressView,
    Row,
)


class FakeScreen:
    def __init__(self, rows: int = 24, cols: int = 80, keys=None) -> None:
        self.rows = rows
        self.cols = cols
        self.keys = list(keys or [])
        self.clearok_calls: list[bool] = []
        self.timeout_calls: list[int] = []
        self.refreshes = 0
        self.cells: dict[tuple[int, int], str] = {}

    def getmaxyx(self):
        return self.rows, self.cols

    def clearok(self, flag):
        self.clearok_calls.append(flag)

    def erase(self):
        self.cells.clear()

    def addnstr(self, y, x, text, n, attr=0):
        for offset, char in enumerate(str(text)[:n]):
            if x + offset < self.cols:
                self.cells[(y, x + offset)] = char

    def refresh(self):
        self.refreshes += 1

    def timeout(self, ms):
        self.timeout_calls.append(ms)

    def getch(self):
        return self.keys.pop(0) if self.keys else -1

    def move(self, y, x):
        pass

    def nodelay(self, flag):
        pass

    def row_text(self, y: int) -> str:
        return "".join(
            self.cells.get((y, x), " ") for x in range(self.cols)
        ).rstrip()


def make_ui(screen: FakeScreen) -> CursesUI:
    ui = object.__new__(CursesUI)
    ui.screen = screen
    ui.rows = screen.rows
    ui.cols = screen.cols
    ui.colors = {}
    return ui


class FrameRepaintTest(unittest.TestCase):
    def test_frame_forces_a_full_repaint(self):
        screen = FakeScreen()
        ui = make_ui(screen)
        ui._frame("Disk setup", "choose a disk", "Enter select")
        self.assertTrue(screen.clearok_calls)
        self.assertTrue(all(screen.clearok_calls))
        self.assertIn("Disk setup", screen.row_text(0))
        self.assertIn("Enter select", screen.row_text(screen.rows - 1))

    def test_menu_redraws_after_an_idle_timeout(self):
        screen = FakeScreen(keys=[-1, curses.KEY_ENTER])
        ui = make_ui(screen)
        result = ui.menu("Title", "subtitle", [Row("One")])
        self.assertEqual(result, 0)
        self.assertGreaterEqual(screen.refreshes, 2)
        self.assertGreaterEqual(len(screen.clearok_calls), 2)
        # A timeout must be restored to blocking mode after every wait.
        self.assertEqual(
            screen.timeout_calls[:2], [REDRAW_INTERVAL_MS, -1]
        )

    def test_message_redraws_after_an_idle_timeout(self):
        screen = FakeScreen(keys=[-1, ord("x")])
        ui = make_ui(screen)
        key = ui.message("Failure", ["something happened"])
        self.assertEqual(key, ord("x"))
        self.assertGreaterEqual(screen.refreshes, 2)
        self.assertGreaterEqual(len(screen.clearok_calls), 2)

    def test_progress_full_redraws_on_start_and_step_change(self):
        screen = FakeScreen()
        ui = make_ui(screen)
        progress = ProgressView(ui, "Installing Tenko Linux", 9)
        self.assertTrue(screen.clearok_calls)
        initial = len(screen.clearok_calls)
        progress.set_step(2, 9, "Creating filesystems")
        self.assertGreater(len(screen.clearok_calls), initial)
        self.assertIn(
            "Creating filesystems", screen.row_text(2)
        )


if __name__ == "__main__":
    unittest.main()
