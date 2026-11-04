"""Structured logging for browneye-installer.

The installer writes machine-readable JSON Lines to
``/run/browneye/install.jsonl`` and a small human-readable mirror to
``/run/browneye/install.log``.  Both are copied to the new ESP and to the
installed system at the end of a run.

Secrets are never written to either file.  ``chpasswd`` input is logged as a
redacted placeholder by the command runner, and the account password is not
kept in this module at all.
"""

from __future__ import annotations

import getpass
import json
import os
import socket
import sys
import time
from datetime import datetime, timezone
from typing import Any, Callable

MIB = 1024 * 1024
GIB = 1024 * MIB

_SECRET_KEYS = {
    "password",
    "passwd",
    "secret",
    "token",
    "key",
    "admin_password",
    "root_password",
}

_REDACTED = "<redacted>"


def redact_value(key: str, value: Any) -> Any:
    """Return a safe representation for a field name/value pair."""

    if key.lower() in _SECRET_KEYS:
        return _REDACTED if value not in (None, "") else value
    if isinstance(value, dict):
        return {k: redact_value(k, v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact_value(key, item) for item in value]
    return value


def redact_argv(argv: list[str] | tuple[str, ...]) -> list[str]:
    """Redact common password command line forms.

    The installer never passes a password in argv (``chpasswd`` reads stdin),
    but this keeps accidental future uses from leaking into the log.
    """

    result: list[str] = []
    hide_next = False
    for item in argv:
        if hide_next:
            result.append(_REDACTED)
            hide_next = False
            continue
        if item in ("--password", "--passwd", "-p"):
            result.append(item)
            hide_next = True
            continue
        if item.startswith("--password=") or item.startswith("--passwd="):
            name, _, _value = item.partition("=")
            result.append(name + "=" + _REDACTED)
            continue
        result.append(item)
    return result


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class Logger:
    """JSONL + human log with an optional console mirror.

    ``console`` is called with a human-readable single line.  In curses mode
    the UI supplies a callback that appends to the progress log pane; in
    plain/non-interactive mode the default writes to stderr (and the caller
    may also mirror to a serial port).
    """

    def __init__(
        self,
        path: str = "/run/browneye/install.jsonl",
        *,
        human_path: str | None = None,
        console: Callable[[str], None] | None = None,
        quiet: bool = False,
    ) -> None:
        self.path = path
        self.human_path = human_path or os.path.join(
            os.path.dirname(path) or ".", "install.log"
        )
        self.console = console
        self.quiet = quiet
        self._json = None
        self._human = None
        self._fallback = False

        try:
            directory = os.path.dirname(path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            self._json = open(path, "a", encoding="utf-8", buffering=1)
            self._human = open(self.human_path, "a", encoding="utf-8", buffering=1)
        except OSError as exc:
            # A read-only or unwritable /run must not prevent the UI from
            # telling the user why the install failed.
            self._fallback = True
            self.path = ""
            self.human_path = ""
            self.record(
                "error",
                "log-open-failed",
                error=str(exc),
                requested_path=path,
            )

    @property
    def available(self) -> bool:
        return self._json is not None

    def close(self) -> None:
        for handle in (self._json, self._human):
            if handle is not None:
                try:
                    handle.flush()
                    handle.close()
                except OSError:
                    pass
        self._json = None
        self._human = None

    def flush(self) -> None:
        for handle in (self._json, self._human):
            if handle is not None:
                try:
                    handle.flush()
                    os.fsync(handle.fileno())
                except OSError:
                    pass

    def record(self, level: str, event: str, *, step: str | None = None, **fields: Any) -> dict:
        record: dict[str, Any] = {
            "ts": _now(),
            "level": level,
            "event": event,
            "pid": os.getpid(),
        }
        if step:
            record["step"] = step
        for key, value in fields.items():
            record[key] = redact_value(key, value)

        if self._json is not None:
            try:
                self._json.write(json.dumps(record, sort_keys=True, default=str) + "\n")
            except OSError:
                pass

        human = self._human_line(record)
        if self._human is not None:
            try:
                self._human.write(human + "\n")
            except OSError:
                pass
        if self.console is not None and not self.quiet:
            try:
                self.console(human)
            except Exception:  # a broken UI must not break logging
                pass
        return record

    def _human_line(self, record: dict[str, Any]) -> str:
        stamp = str(record.get("ts", ""))[11:19] or time.strftime("%H:%M:%S")
        level = str(record.get("level", "info")).upper()
        step = record.get("step")
        event = record.get("event", "")
        prefix = f"{stamp} {level:<7} "
        if step:
            prefix += f"[{step}] "
        parts = []
        for key in sorted(record):
            if key in ("ts", "level", "event", "step", "pid"):
                continue
            value = record[key]
            if isinstance(value, (dict, list)):
                value = json.dumps(value, sort_keys=True, default=str)
            parts.append(f"{key}={value}")
        line = prefix + str(event)
        if parts:
            line += " " + " ".join(parts)
        return line

    # Convenience wrappers -------------------------------------------------
    def debug(self, event: str, **fields: Any) -> dict:
        return self.record("debug", event, **fields)

    def info(self, event: str, **fields: Any) -> dict:
        return self.record("info", event, **fields)

    def warning(self, event: str, **fields: Any) -> dict:
        return self.record("warning", event, **fields)

    def error(self, event: str, **fields: Any) -> dict:
        return self.record("error", event, **fields)

    def step_start(self, step: str, index: int, total: int) -> dict:
        return self.record(
            "info", "step-start", step=step, index=index, total=total
        )

    def step_done(self, step: str, index: int, total: int) -> dict:
        return self.record(
            "info", "step-done", step=step, index=index, total=total
        )

    def command(
        self,
        argv: list[str] | tuple[str, ...],
        rc: int,
        duration_ms: int,
        *,
        step: str | None = None,
        output_tail: str | None = None,
        stdin_log: str | None = None,
    ) -> dict:
        fields: dict[str, Any] = {
            "argv": redact_argv(argv),
            "rc": rc,
            "dur_ms": duration_ms,
        }
        if stdin_log is not None:
            fields["stdin"] = stdin_log
        if output_tail:
            fields["tail"] = output_tail[-4000:]
        return self.record("info", "command", step=step, **fields)

    def plan(self, plan_record: dict[str, Any]) -> dict:
        return self.record("info", "plan", plan=plan_record)

    def probe(self, probe_record: dict[str, Any]) -> dict:
        return self.record("debug", "probe", probe=probe_record)

    def session_header(self, **extra: Any) -> dict:
        uname = os.uname()
        return self.record(
            "info",
            "session-start",
            host=socket.gethostname(),
            user=getpass.getuser(),
            kernel=uname.release,
            machine=uname.machine,
            argv=sys.argv,
            **extra,
        )


def null_logger(**_: Any) -> Logger:
    """A logger for unit tests: no file, no console."""

    logger = Logger.__new__(Logger)
    logger.path = ""
    logger.human_path = ""
    logger.console = None
    logger.quiet = True
    logger._json = None
    logger._human = None
    logger._fallback = True
    return logger
