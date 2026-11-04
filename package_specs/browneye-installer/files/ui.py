"""Small ncurses UI toolkit for the installer.

The toolkit is intentionally limited: menus, text, forms, a typed
confirmation, and a progress/log pane.  It uses only the Python standard
library and works on a VGA console (``TERM=linux``), serial/vt100 and
xterm-like terminals.  The installer never depends on mouse input or colour.
"""

from __future__ import annotations

import curses
import textwrap
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Iterable, Sequence

MIN_ROWS = 24
MIN_COLS = 80

QUIT = -1
RESCAN = -2
BACK = -3


@dataclass
class Row:
    text: str
    enabled: bool = True
    note: str = ""
    marker: str = " "


@dataclass
class Field:
    label: str
    value: str = ""
    secret: bool = False
    hint: str = ""


class CursesUI:
    def __init__(self, stdscr) -> None:
        self.screen = stdscr
        self.rows = 24
        self.cols = 80
        self._measure()
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        self.screen.keypad(True)
        try:
            curses.use_default_colors()
        except curses.error:
            pass

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------
    def _measure(self) -> None:
        self.rows, self.cols = self.screen.getmaxyx()

    def _ensure_size(self) -> bool:
        while True:
            self._measure()
            if self.rows >= MIN_ROWS and self.cols >= MIN_COLS:
                return True
            self.screen.erase()
            msg = "Terminal is too small: {}x{}; need at least {}x{}".format(
                self.cols, self.rows, MIN_COLS, MIN_ROWS
            )
            self._safe_add(self.rows // 2, max(0, (self.cols - len(msg)) // 2), msg)
            self.screen.refresh()
            key = self.screen.getch()
            if key in (ord("q"), 27):
                return False

    def _safe_add(self, y: int, x: int, text: str, attr: int = 0) -> None:
        if y < 0 or y >= self.rows or x >= self.cols:
            return
        # The VGA console and some serial terminals run with LANG=C; keep the
        # screen ASCII so curses never raises a UnicodeEncodeError.
        text = str(text).encode("ascii", "replace").decode("ascii")
        try:
            self.screen.addnstr(y, max(0, x), text, max(0, self.cols - x - 1), attr)
        except curses.error:
            pass

    def _center(self, text: str) -> int:
        return max(0, (self.cols - len(text)) // 2)

    def _frame(self, title: str, subtitle: str = "", footer: str = "") -> None:
        self.screen.erase()
        self._safe_add(0, 0, " " * (self.cols - 1), curses.A_REVERSE)
        self._safe_add(0, 2, title[: self.cols - 4], curses.A_REVERSE | curses.A_BOLD)
        if subtitle:
            self._safe_add(1, 2, subtitle[: self.cols - 4], curses.A_BOLD)
        if footer:
            self._safe_add(
                self.rows - 1, 0, " " * (self.cols - 1), curses.A_REVERSE
            )
            self._safe_add(
                self.rows - 1, 2, footer[: self.cols - 4], curses.A_REVERSE
            )

    def _wait(self) -> int:
        return self.screen.getch()

    # ------------------------------------------------------------------
    # Menus and messages
    # ------------------------------------------------------------------
    def menu(
        self,
        title: str,
        subtitle: str,
        rows: Sequence[Row],
        *,
        footer: str = "Up/Down move   Enter select   r rescan   q quit",
        allow_rescan: bool = True,
        allow_back: bool = False,
    ) -> int:
        index = next((i for i, row in enumerate(rows) if row.enabled), 0)
        offset = 0
        while True:
            if not self._ensure_size():
                return QUIT
            self._frame(title, subtitle, footer)
            body_top = 3
            body_height = max(1, self.rows - body_top - 2)
            if index < offset:
                offset = index
            if index >= offset + body_height:
                offset = index - body_height + 1
            for line_no, row_index in enumerate(
                range(offset, min(len(rows), offset + body_height))
            ):
                row = rows[row_index]
                y = body_top + line_no
                marker = ">" if row_index == index else " "
                text = "{} {} {}".format(marker, row.marker, row.text)
                if row.note:
                    text += "  " + row.note
                attr = curses.A_BOLD if row_index == index else 0
                if not row.enabled:
                    attr |= curses.A_DIM
                self._safe_add(y, 2, text[: self.cols - 4], attr)
            if not rows:
                self._safe_add(body_top, 2, "(nothing found)")
            self.screen.refresh()
            key = self._wait()
            if key in (ord("q"), 27) and not allow_back:
                return QUIT
            if key in (ord("q"), 27) and allow_back:
                return BACK
            if key in (curses.KEY_UP, ord("k")):
                for candidate in range(index - 1, -1, -1):
                    if rows[candidate].enabled:
                        index = candidate
                        break
            elif key in (curses.KEY_DOWN, ord("j")):
                for candidate in range(index + 1, len(rows)):
                    if rows[candidate].enabled:
                        index = candidate
                        break
            elif key == curses.KEY_PPAGE:
                index = max(0, index - body_height)
            elif key == curses.KEY_NPAGE:
                index = min(max(0, len(rows) - 1), index + body_height)
            elif key == curses.KEY_HOME:
                index = 0
            elif key == curses.KEY_END:
                index = max(0, len(rows) - 1)
            elif key in (curses.KEY_ENTER, 10, 13):
                if rows and rows[index].enabled:
                    return index
            elif key == ord("r") and allow_rescan:
                return RESCAN
            elif key == curses.KEY_RESIZE:
                continue

    def message(
        self,
        title: str,
        lines: Sequence[str],
        *,
        footer: str = "Press any key to continue",
        subtitle: str = "",
    ) -> int:
        self._ensure_size()
        self._frame(title, subtitle, footer)
        y = 3
        for line in lines:
            for wrapped in textwrap.wrap(str(line), max(20, self.cols - 6)) or [""]:
                if y >= self.rows - 2:
                    break
                self._safe_add(y, 3, wrapped)
                y += 1
        self.screen.refresh()
        key = self._wait()
        while key == curses.KEY_RESIZE:
            self._ensure_size()
            self._frame(title, subtitle, footer)
            y = 3
            for line in lines:
                for wrapped in textwrap.wrap(str(line), max(20, self.cols - 6)) or [""]:
                    if y >= self.rows - 2:
                        break
                    self._safe_add(y, 3, wrapped)
                    y += 1
            self.screen.refresh()
            key = self._wait()
        return key

    # ------------------------------------------------------------------
    # Forms
    # ------------------------------------------------------------------
    def form(
        self,
        title: str,
        fields: Sequence[Field],
        *,
        subtitle: str = "",
        footer: str = "Tab/Up/Down next   Enter done   Esc back",
        extra_lines: Sequence[str] = (),
        mask_password: bool = True,
    ) -> list[str] | None:
        work = [Field(f.label, f.value, f.secret, f.hint) for f in fields]
        try:
            curses.curs_set(1)
        except curses.error:
            pass
        try:
            return self._form_loop(
                title,
                work,
                subtitle=subtitle,
                footer=footer,
                extra_lines=extra_lines,
                mask_password=mask_password,
            )
        finally:
            try:
                curses.curs_set(0)
            except curses.error:
                pass

    def _form_loop(
        self,
        title: str,
        fields: list[Field],
        *,
        subtitle: str,
        footer: str,
        extra_lines: Sequence[str],
        mask_password: bool,
    ) -> list[str] | None:
        index = 0
        while True:
            if not self._ensure_size():
                return None
            self._frame(title, subtitle, footer)
            y = 3
            for line in extra_lines:
                for wrapped in textwrap.wrap(str(line), max(20, self.cols - 6)) or [""]:
                    self._safe_add(y, 3, wrapped)
                    y += 1
            y += 1
            positions: list[tuple[int, int]] = []
            for field_index, item in enumerate(fields):
                label = item.label + ":"
                self._safe_add(y, 3, label[: max(10, self.cols // 3)], curses.A_BOLD)
                value = item.value
                shown = "*" * len(value) if (item.secret and mask_password) else value
                field_x = 3 + max(12, self.cols // 3)
                width = max(10, self.cols - field_x - 3)
                display = shown[-width:]
                attr = curses.A_REVERSE if field_index == index else 0
                self._safe_add(y, field_x, " " * width, attr)
                self._safe_add(y, field_x, display[:width], attr)
                if item.hint and field_index == index:
                    self._safe_add(
                        y + 1,
                        field_x,
                        item.hint[: self.cols - field_x - 2],
                        curses.A_DIM,
                    )
                positions.append((y, field_x + min(len(display), width)))
                y += 2
            self.screen.refresh()
            if fields:
                cy, cx = positions[index]
                try:
                    self.screen.move(cy, min(cx, self.cols - 2))
                except curses.error:
                    pass
            key = self._wait()
            if key == 27:
                return None
            if key in (curses.KEY_UP, curses.KEY_BTAB):
                index = (index - 1) % max(1, len(fields))
            elif key in (curses.KEY_DOWN, 9):
                index = (index + 1) % max(1, len(fields))
            elif key in (curses.KEY_ENTER, 10, 13):
                if index == len(fields) - 1:
                    return [item.value for item in fields]
                index += 1
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                if fields:
                    fields[index].value = fields[index].value[:-1]
            elif key == 21:  # Ctrl-U
                if fields:
                    fields[index].value = ""
            elif key == curses.KEY_RESIZE:
                continue
            elif 32 <= key <= 126 and fields:
                if len(fields[index].value) < 256:
                    fields[index].value += chr(key)

    def confirm_typed(
        self,
        title: str,
        lines: Sequence[str],
        prompts: Sequence[str],
        *,
        footer: str = "Tab next   Enter confirm   Esc back",
    ) -> list[str] | None:
        fields = [Field(label) for label in prompts]
        return self.form(
            title,
            fields,
            subtitle="Type the values exactly; there is no undo after formatting.",
            footer=footer,
            extra_lines=lines,
        )

    # ------------------------------------------------------------------
    # Progress
    # ------------------------------------------------------------------
    def progress(self, title: str, total: int) -> "ProgressView":
        return ProgressView(self, title, total)


class ProgressView:
    def __init__(self, ui: CursesUI, title: str, total: int) -> None:
        self.ui = ui
        self.title = title
        self.total = max(1, total)
        self.index = 0
        self.step_name = "Starting"
        self.lines: deque[str] = deque(maxlen=2000)
        self._last_draw = 0.0
        self._pending = 0
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        self.draw()

    def set_step(self, index: int, total: int, name: str) -> None:
        self.index = index
        self.total = max(1, total)
        self.step_name = name
        self.draw()

    def line(self, text: str) -> None:
        if not text:
            return
        self.lines.append(str(text).replace("\t", "    "))
        self._pending += 1
        now = time.monotonic()
        if self._pending >= 8 or now - self._last_draw > 0.15:
            self.draw()

    def draw(self) -> None:
        if not self.ui._ensure_size():
            return
        ui = self.ui
        ui._frame(self.title, "", "Please wait; do not power off or remove the media")
        step_text = "[{}/{}] {}".format(self.index, self.total, self.step_name)
        ui._safe_add(2, 2, step_text[: ui.cols - 4], curses.A_BOLD)
        bar_width = max(10, ui.cols - 8)
        filled = int(bar_width * (self.index / self.total)) if self.total else 0
        bar = "#" * filled + "-" * (bar_width - filled)
        ui._safe_add(3, 3, "[" + bar + "]", curses.A_DIM)
        available = max(1, ui.rows - 7)
        visible = list(self.lines)[-available:]
        y = 5
        for line in visible:
            ui._safe_add(y, 2, line[-max(1, ui.cols - 4) :])
            y += 1
        ui.screen.refresh()
        self._last_draw = time.monotonic()
        self._pending = 0

    def pump(self) -> int:
        """Return a key if one is waiting, without blocking."""

        try:
            self.ui.screen.nodelay(True)
            key = self.ui.screen.getch()
        finally:
            try:
                self.ui.screen.nodelay(False)
            except curses.error:
                pass
        if key == curses.KEY_RESIZE:
            self.draw()
        return key

    def finish(self) -> None:
        self.draw()
