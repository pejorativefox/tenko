#!/usr/bin/env python3
"""Audit Tenko's freedesktop.org compliance.

The audit is network-free and has three data sources:

* ``package_specs/`` -- spec files and static file lists (always available),
* ``--rpm-dir`` -- built RPMs, which are unpacked selectively so the real
  desktop entries, AppStream metadata, menus, MIME XML and icon themes can be
  validated (the default is the newest ``build/repo-publish/<release>``),
* ``--root`` -- an already extracted root tree, for example a mounted install
  or an unpacked image.

Every matrix row in ``docs/freedesktop.md`` is reported exactly once.  A row
marked ``implemented`` turns any finding into a failing result; ``partial`` and
``gap`` rows report the same findings as ``OPEN`` because an issue owns them.
That keeps the harness usable while the programme is in progress without
weakening the end state.

Usage:
    tenko audit
    tenko audit --rpm-dir build/repo-publish/6
    tenko audit --root build/rootfs-xfce
    tenko audit --only desktop-entry,icons
    tenko audit --json
"""
from __future__ import annotations

import argparse
import configparser
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# The specification index.  docs/freedesktop.md must carry a row for each of
# these keys; the key is the first cell of the matrix row, lowercased and with
# spaces or underscores replaced by '-'.  Keep this list in sync with the
# tracker (Gitea #32).
# ---------------------------------------------------------------------------
SPEC_INDEX = (
    "appstream",
    "autostart",
    "basedir",
    "clipboard",
    "clipboard-extensions",
    "dbus",
    "desktop-entry",
    "fhs",
    "global-shortcuts",
    "help-system",
    "icon-naming",
    "icon-theme",
    "idle-inhibit",
    "intent-apps",
    "menu",
    "mime-apps",
    "mpris",
    "notification",
    "polkit",
    "recent-files",
    "secret-service",
    "shortcuts",
    "shared-mime-info",
    "sound-naming",
    "sound-theme",
    "startup-notification",
    "status-notifier-item",
    "systemtray",
    "terminal-intent",
    "thumbnail",
    "trash",
    "wm",
    "xembed",
    "xsettings",
    "XDG user dirs",
    "xdg-desktop-portal",
)

DISPOSITIONS = ("implemented", "partial", "gap", "N/A")

# Upstream/vendor metadata defects that do not block the distro's own
# compliance.  Keys are (basename, text that must appear on the error line).
UPSTREAM_APPSTREAM_ERRORS = {
    (
        "google-chrome.appdata.xml",
        "type-property-required",
    ): "#42 Chrome vendor bundle metadata",
}

# Cache updates must be file triggers.  Each entry is (spec, command, path).
REQUIRED_TRIGGERS = (
    ("desktop-entry", "update-desktop-database", "/usr/share/applications"),
    ("shared-mime-info", "update-mime-database", "/usr/share/mime"),
    ("icon-theme", "gtk-update-icon-cache", "/usr/share/icons"),
)

# FHS 3.0 directories missing from the current tenko-basefs package.
FHS_REQUIRED_DIRS = (
    "/media",
    "/var/local",
    "/usr/local/etc",
    "/usr/local/games",
    "/usr/local/include",
    "/usr/local/man",
    "/usr/local/share",
    "/usr/local/src",
)

# Default associations a desktop install should provide (MIME Apps 1.0.1).
MIME_DEFAULT_REQUIRED = (
    "text/plain",
    "image/png",
    "inode/directory",
    "x-scheme-handler/http",
)

DESKTOP_PROFILE_PREFIXES = (
    "xfce-desktop",
    "tenko-workstation",
)

# Directories whose .desktop files are really Desktop Entry files.  XFCE's
# helper and panel-plugin descriptors, GTK module files and Xsession entries
# have private formats and are deliberately out of scope.
DESKTOP_ENTRY_DIRS = (
    "/usr/share/applications",
    "/usr/local/share/applications",
    "/etc/xdg/autostart",
)
AUTOSTART_DIRS = (
    "/etc/xdg/autostart",
    "/usr/local/share/autostart",
)

# Files that must be unpacked from RPMs for the content checks.
EXTRACT_PATTERNS = (
    "/usr/share/applications/*.desktop",
    "/usr/local/share/applications/*.desktop",
    "/etc/xdg/autostart/*.desktop",
    "/usr/local/share/autostart/*.desktop",
    "/usr/share/metainfo/*.xml",
    "/usr/share/metainfo/*.xml.gz",
    "/usr/share/appdata/*.xml",
    "/usr/share/icons/*/index.theme",
    "/etc/xdg/menus/*.menu",
    "/etc/xdg/mimeapps.list",
    "/usr/share/applications/mimeapps.list",
    "/usr/share/applications/defaults.list",
    "/usr/share/mime/packages/*.xml",
    "/usr/share/dbus-1/*.conf",
    "/usr/share/dbus-1/*.d/*.conf",
    "/usr/share/dbus-1/services/*.service",
    "/usr/share/dbus-1/system-services/*.service",
    "/usr/share/polkit-1/actions/*.policy",
    "/usr/share/xdg-desktop-portal/portals/*.portal",
    "/usr/bin/xdg-open",
)

TRIGGER_RE = re.compile(r"^%(trans)?filetrigger(in|postun|un)\b")
MACROS = {
    "%{_datadir}": "/usr/share",
    "%{_sysconfdir}": "/etc",
    "%{_prefix}": "/usr",
    "%{_bindir}": "/usr/bin",
    "%{_sbindir}": "/usr/sbin",
    "%{_libdir}": "/usr/lib64",
    "%{_libexecdir}": "/usr/libexec",
    "%{_localstatedir}": "/var",
    "%{_docdir}": "/usr/share/doc",
    "%{_mandir}": "/usr/share/man",
    "%{_infodir}": "/usr/share/info",
    "%{_includedir}": "/usr/include",
    "%{_unitdir}": "/usr/lib/systemd/system",
    "%{_userunitdir}": "/usr/lib/systemd/user",
}
VALIDATOR_TOOLS = ("desktop-file-validate", "appstreamcli", "rpm", "rpm2cpio", "cpio")


@dataclass
class Finding:
    spec: str
    check: str
    message: str
    severity: str = "error"


@dataclass
class Row:
    spec: str
    display: str
    version: str
    disposition: str
    evidence: str
    findings: list[Finding] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def issues(self) -> list[str]:
        return sorted(set(re.findall(r"#\d+", self.evidence)))

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity != "error"]


def normalize_spec(name: str) -> str:
    return re.sub(r"[-_\s]+", "-", name.strip().strip("`").strip().lower())


def normalize_macro(value: str) -> str:
    value = value.strip().strip(",")
    for macro, path in MACROS.items():
        value = value.replace(macro, path)
    return value.rstrip("/") or "/"


def parse_desktop_file(path: Path) -> configparser.ConfigParser | None:
    parser = configparser.ConfigParser(
        interpolation=None, strict=False, delimiters=("=",), comment_prefixes=("#",)
    )
    parser.optionxform = str
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            parser.read_file(handle)
    except (configparser.Error, UnicodeError):
        return None
    if not parser.has_section("Desktop Entry"):
        return None
    return parser


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


class Auditor:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.root = Path(args.root).resolve() if args.root else None
        self.spec_root = Path(args.spec_root).resolve()
        self.doc_path = Path(args.doc).resolve()
        self.only = {normalize_spec(x) for x in args.only.split(",") if x.strip()} if args.only else None
        self.rows: dict[str, Row] = {}
        self.doc_findings: list[Finding] = []
        self.spec_text: dict[str, str] = {}
        self.paths: set[str] = set()
        self.static_paths: set[str] = set()
        self.contents: Path | None = None
        self._tempdirs: list[Path] = []
        self.rpms: list[Path] = []
        self.rpm_files: dict[Path, list[str]] = {}
        self.dbus_service_names: set[str] = set()
        self.theme_inherits: dict[str, list[str]] = {}
        self.theme_icons: dict[str, set[str]] = {}
        self.pixmap_icons: set[str] = set()
        self.warning_log: list[str] = []
        self._tool_cache: dict[str, bool] = {}

    # -- setup -----------------------------------------------------------
    def load_matrix(self) -> None:
        if not self.doc_path.is_file():
            self.doc_findings.append(
                Finding("docs", "matrix", f"missing {self.doc_path}", "error")
            )
            return
        by_key = {normalize_spec(name): name for name in SPEC_INDEX}
        seen: set[str] = set()
        for lineno, line in enumerate(self.doc_path.read_text(encoding="utf-8").splitlines(), 1):
            text = line.strip()
            if not text.startswith("|"):
                continue
            cells = [cell.strip() for cell in text.strip("|").split("|")]
            if len(cells) != 4:
                continue
            label = cells[0].strip("`").strip()
            if not label or label.lower() == "spec" or set(label) <= set("-: "):
                continue
            key = normalize_spec(label)
            if key not in by_key:
                # Ignore the explanatory tables; they have three columns.
                self.doc_findings.append(
                    Finding(
                        "docs",
                        "matrix",
                        f"{self.doc_path.name}:{lineno}: unknown spec row {label!r}",
                        "error",
                    )
                )
                continue
            if key in seen:
                self.doc_findings.append(
                    Finding("docs", "matrix", f"duplicate spec row {label!r}", "error")
                )
                continue
            seen.add(key)
            disposition = cells[2].strip()
            if disposition.lower() == "n/a":
                disposition = "N/A"
            elif disposition.lower() in DISPOSITIONS:
                disposition = disposition.lower()
            row = Row(key, label, cells[1], disposition, cells[3])
            self.rows[key] = row
            if disposition not in DISPOSITIONS:
                self.doc_findings.append(
                    Finding("docs", "matrix", f"{label}: invalid disposition {disposition!r}", "error")
                )
            if disposition in ("partial", "gap") and not row.issues:
                self.doc_findings.append(
                    Finding(
                        "docs",
                        "matrix",
                        f"{label}: {disposition} row has no linked issue",
                        "error",
                    )
                )
            if disposition == "N/A" and not row.evidence:
                self.doc_findings.append(
                    Finding("docs", "matrix", f"{label}: N/A row has no rationale", "error")
                )
        for key, display in by_key.items():
            if key not in seen:
                self.doc_findings.append(
                    Finding("docs", "matrix", f"missing spec row {display!r}", "error")
                )

    def load_specs(self) -> None:
        for spec in sorted(self.spec_root.glob("*/*.spec")):
            self.spec_text[spec.parent.name] = spec.read_text(encoding="utf-8", errors="replace")

    def load_filelists(self) -> None:
        for filelist in sorted(self.spec_root.glob("*/files/*.filelist")):
            for line in filelist.read_text(encoding="utf-8", errors="replace").splitlines():
                path = line.strip()
                if not path or path.startswith("#"):
                    continue
                path = re.sub(r"^%(doc|config|attr|verify|dir|defattr|license)\b[^ ]*\s*", "", path)
                path = re.sub(r"^%attr\([^)]*\)\s*", "", path)
                path = normalize_macro(path)
                if path.startswith("/"):
                    self.static_paths.add(path)

    def load_inline_filelists(self) -> None:
        """Collect paths from specs that use an inline %files section."""
        path_directive = re.compile(
            r"^%(doc|config|attr|verify|dir|defattr|license)\b[^ ]*\s*"
        )
        section_start = re.compile(r"^%files\b")
        other_section = re.compile(r"^%[a-zA-Z]")
        for text in self.spec_text.values():
            in_files = False
            for raw in text.splitlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if section_start.match(line):
                    in_files = True
                    continue
                if not in_files:
                    continue
                if path_directive.match(line):
                    entry = path_directive.sub("", line)
                    entry = normalize_macro(entry)
                    if entry.startswith("/"):
                        self.static_paths.add(entry)
                    continue
                if other_section.match(line):
                    in_files = False
                    continue
                entry = normalize_macro(line)
                if entry.startswith("/"):
                    self.static_paths.add(entry)

    def load_root(self) -> None:
        if not self.root:
            return
        if not self.root.is_dir():
            self.doc_findings.append(
                Finding("docs", "root", f"--root {self.root} is not a directory", "error")
            )
            return
        self.contents = self.root
        self.paths = set()
        for base, dirs, files in os.walk(self.root):
            rel = os.path.relpath(base, self.root)
            rel = "" if rel == "." else "/" + rel.replace(os.sep, "/")
            self.paths.add(rel or "/")
            for name in files:
                self.paths.add((rel + "/" + name) if rel else "/" + name)

    def load_rpms(self) -> None:
        if self.root is not None:
            # --root is a complete filesystem tree; do not mix in RPM contents.
            return
        if not shutil.which("rpm") or not shutil.which("rpm2cpio") or not shutil.which("cpio"):
            self.doc_findings.append(
                Finding(
                    "docs",
                    "rpms",
                    "rpm, rpm2cpio and cpio are required to audit built RPMs",
                    "error",
                )
            )
            return
        dirs = self.args.rpm_dir
        if not dirs:
            publish = self.args.repo_root / "build" / "repo-publish"
            if publish.is_dir():
                candidates = [
                    item
                    for item in sorted(publish.iterdir())
                    if item.is_dir() and any(item.glob("*.rpm"))
                ]
                if candidates:
                    dirs = [str(candidates[-1])]
        by_name: dict[str, Path] = {}
        for directory in dirs:
            path = Path(directory)
            if not path.is_dir():
                self.doc_findings.append(
                    Finding("docs", "rpms", f"--rpm-dir {directory} is not a directory", "error")
                )
                continue
            for rpm in sorted(path.glob("*.rpm")):
                by_name[rpm.name] = rpm
        self.rpms = sorted(by_name.values())
        if not self.rpms:
            self.paths = set(self.static_paths)
            return
        self.paths = set()
        for rpm in self.rpms:
            result = subprocess.run(
                ["rpm", "-qpl", str(rpm)], capture_output=True, text=True
            )
            if result.returncode != 0:
                self.doc_findings.append(
                    Finding("docs", "rpms", f"{rpm.name}: {result.stderr.strip()}", "error")
                )
                continue
            files = [line for line in result.stdout.splitlines() if line.startswith("/")]
            self.rpm_files[rpm] = files
            self.paths.update(files)
        self.extract_contents()

    def extract_contents(self) -> None:
        if not self.rpms:
            return
        selected = []
        for rpm, files in self.rpm_files.items():
            if any(
                fnmatch.fnmatch(path, pattern)
                for path in files
                for pattern in EXTRACT_PATTERNS
            ):
                selected.append(rpm)
        if not selected:
            return
        tmp = Path(tempfile.mkdtemp(prefix="tenko-fdo-audit-"))
        self._tempdirs.append(tmp)
        patterns = ["./" + pattern.lstrip("/") for pattern in EXTRACT_PATTERNS]
        for rpm in selected:
            producer = subprocess.Popen(
                ["rpm2cpio", str(rpm)],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            subprocess.run(
                ["cpio", "-idm", "--quiet", *patterns],
                stdin=producer.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=tmp,
                check=False,
            )
            if producer.stdout:
                producer.stdout.close()
            producer.wait()
        self.contents = tmp
        self.load_dbus_services()
        self.load_icon_themes()

    def load_dbus_services(self) -> None:
        if not self.contents:
            return
        for path in self.contents.glob("usr/share/dbus-1/services/*.service"):
            text = path.read_text(encoding="utf-8", errors="replace")
            match = re.search(r"^Name\s*=\s*(\S+)", text, re.MULTILINE)
            if match:
                self.dbus_service_names.add(match.group(1))

    def load_icon_themes(self) -> None:
        if not self.contents:
            return
        for path in self.contents.glob("usr/share/icons/*/index.theme"):
            theme = path.parent.name
            parser = configparser.ConfigParser(strict=False, interpolation=None)
            try:
                parser.read(path)
                raw = parser.get("Icon Theme", "Inherits", fallback="")
            except configparser.Error:
                raw = ""
            self.theme_inherits[theme] = [
                item.strip() for item in raw.split(",") if item.strip()
            ]
        for icon in self.paths:
            if not icon.startswith("/usr/share/icons/"):
                continue
            parts = icon.split("/")
            if len(parts) < 6:
                continue
            theme = parts[3]
            name = parts[-1]
            stem, dot, ext = name.rpartition(".")
            if not dot or ext.lower() not in ("png", "svg", "xpm"):
                continue
            self.theme_icons.setdefault(theme, set()).add(stem)
            self.theme_icons.setdefault(theme, set()).add(name)
        for icon in self.paths:
            if icon.startswith("/usr/share/pixmaps/"):
                name = icon.rsplit("/", 1)[-1]
                stem, dot, ext = name.rpartition(".")
                if dot and ext.lower() in ("png", "svg", "xpm"):
                    self.pixmap_icons.add(stem)
                    self.pixmap_icons.add(name)

    # -- helpers ---------------------------------------------------------
    def cleanup(self) -> None:
        for path in self._tempdirs:
            shutil.rmtree(path, ignore_errors=True)

    def selected(self, *specs: str) -> bool:
        if self.only is None:
            return True
        return any(normalize_spec(spec) in self.only for spec in specs)

    def add(self, spec: str, check: str, message: str, severity: str = "error") -> None:
        key = normalize_spec(spec)
        if key not in self.rows or not self.selected(key):
            return
        self.rows[key].findings.append(Finding(key, check, message, severity))

    def note(self, spec: str, message: str) -> None:
        key = normalize_spec(spec)
        if key in self.rows and self.selected(key):
            self.rows[key].notes.append(message)

    def has_path(self, path: str) -> bool:
        path = path.rstrip("/")
        return any(p == path or p.startswith(path + "/") for p in self.paths)

    def files_under(self, prefix: str, suffix: str = "") -> list[str]:
        prefix = prefix.rstrip("/") + "/"
        return sorted(
            p for p in self.paths if p.startswith(prefix) and p.endswith(suffix)
        )

    def content_file(self, path: str) -> Path | None:
        if not self.contents:
            return None
        candidate = self.contents / path.lstrip("/")
        return candidate if candidate.is_file() else None

    def tool(self, name: str) -> bool:
        if name not in self._tool_cache:
            self._tool_cache[name] = shutil.which(name) is not None
        return self._tool_cache[name]

    def require_tools(self, *names: str) -> bool:
        missing = [name for name in names if not self.tool(name)]
        if missing:
            self.doc_findings.append(
                Finding(
                    "docs",
                    "tools",
                    "missing required tool(s): " + ", ".join(missing),
                    "error",
                )
            )
            return False
        return True

    def desktop_files(self, directories=DESKTOP_ENTRY_DIRS) -> list[Path]:
        if not self.contents:
            return []
        found: list[Path] = []
        for directory in directories:
            base = self.contents / directory.lstrip("/")
            if base.is_dir():
                found.extend(sorted(base.glob("*.desktop")))
        return found

    def installed_desktop_ids(self) -> set[str]:
        ids = set()
        for directory in ("/usr/share/applications", "/usr/local/share/applications"):
            for path in self.files_under(directory, ".desktop"):
                ids.add(path.rsplit("/", 1)[-1])
        return ids

    def resolve_exec(self, value: str) -> bool:
        value = value.strip().strip('"')
        if not value:
            return True
        if value.startswith("/"):
            return self.has_path(value)
        name = value.split()[0]
        for directory in ("/usr/bin", "/usr/sbin", "/bin", "/sbin", "/usr/local/bin"):
            if self.has_path(f"{directory}/{name}"):
                return True
        return False

    def requires_of(self, names: set[str]) -> set[str]:
        found: set[str] = set()
        for name, text in self.spec_text.items():
            if name not in names:
                continue
            for line in text.splitlines():
                if not line.lower().startswith("requires:"):
                    continue
                for token in line.split(":", 1)[1].split():
                    token = token.split(">=", 1)[0].split("=", 1)[0].split("<", 1)[0]
                    token = token.split("(", 1)[0].strip(",")
                    if token:
                        found.add(token)
        return found

    def desktop_profile_requires(self) -> set[str]:
        return self.requires_of(
            {
                name
                for name in self.spec_text
                if any(name.startswith(prefix) for prefix in DESKTOP_PROFILE_PREFIXES)
            }
        )

    # -- checks ----------------------------------------------------------
    def check_desktop_entry(self) -> None:
        if not self.selected("desktop-entry"):
            return
        if not self.contents:
            self.note("desktop-entry", "desktop-file-validate skipped: no RPMs or --root")
            return
        if not self.require_tools("desktop-file-validate"):
            return
        files = self.desktop_files(
            ("/usr/share/applications", "/usr/local/share/applications")
        )
        errors = warnings = 0
        for path in files:
            result = subprocess.run(
                ["desktop-file-validate", str(path)],
                capture_output=True,
                text=True,
            )
            output = (result.stdout + result.stderr).replace(str(self.contents) + "/", "")
            for line in output.splitlines():
                if ": error:" in line:
                    errors += 1
                    self.add("desktop-entry", "desktop-file-validate", line)
                elif ": warning:" in line or ": hint:" in line:
                    warnings += 1
                    self.warning_log.append(line)
        if not files:
            self.add(
                "desktop-entry",
                "desktop-file-validate",
                "no application desktop entries found",
            )
        else:
            self.note(
                "desktop-entry",
                f"desktop-file-validate: {len(files)} entries, {errors} errors, "
                f"{warnings} warnings/hints (allowed)",
            )

    def check_autostart(self) -> None:
        if not self.selected("autostart"):
            return
        if not self.contents:
            self.note("autostart", "autostart validation skipped: no RPMs or --root")
            return
        if not self.require_tools("desktop-file-validate"):
            return
        files = self.desktop_files(AUTOSTART_DIRS)
        if not files:
            self.add("autostart", "autostart", "no /etc/xdg/autostart entries found")
            return
        errors = warnings = 0
        for path in files:
            result = subprocess.run(
                ["desktop-file-validate", str(path)],
                capture_output=True,
                text=True,
            )
            output = (result.stdout + result.stderr).replace(str(self.contents) + "/", "")
            for line in output.splitlines():
                if ": error:" in line:
                    errors += 1
                    self.add("autostart", "desktop-file-validate", line)
                elif ": warning:" in line or ": hint:" in line:
                    warnings += 1
                    self.warning_log.append(line)
            parser = parse_desktop_file(path)
            if not parser:
                continue
            try_exec = parser.get("Desktop Entry", "TryExec", fallback="")
            if try_exec and not self.resolve_exec(try_exec):
                self.add(
                    "autostart",
                    "TryExec",
                    f"{path.name}: TryExec {try_exec!r} does not resolve",
                )
            if not parser.has_option("Desktop Entry", "Type"):
                self.add("autostart", "Type", f"{path.name}: missing Type")
        self.note(
            "autostart",
            f"{len(files)} entries, {errors} errors, {warnings} warnings/hints (allowed)",
        )

    def check_appstream(self) -> None:
        if not self.selected("appstream"):
            return
        if not self.contents:
            self.note("appstream", "AppStream validation skipped: no RPMs or --root")
            return
        if not self.require_tools("appstreamcli"):
            return
        files = self.files_under("/usr/share/metainfo", ".xml") + self.files_under(
            "/usr/share/appdata", ".xml"
        )
        files = [f for f in files if self.content_file(f)]
        if not files:
            self.add("appstream", "appstreamcli", "no AppStream metainfo files found")
            return
        errors = warnings = 0
        for path in files:
            local = self.content_file(path)
            if not local:
                continue
            result = subprocess.run(
                ["appstreamcli", "validate", "--no-net", str(local)],
                capture_output=True,
                text=True,
            )
            for line in (result.stdout + result.stderr).splitlines():
                match = re.match(r"^([EWI]):\s*(.*)$", line.strip())
                if not match:
                    continue
                kind, message = match.groups()
                if kind == "W":
                    warnings += 1
                    self.warning_log.append(f"{Path(path).name}: {message}")
                elif kind == "I":
                    continue
                else:
                    basename = Path(path).name
                    allowed = any(
                        basename == name and needle in message
                        for (name, needle) in UPSTREAM_APPSTREAM_ERRORS
                    )
                    if allowed:
                        warnings += 1
                        self.warning_log.append(
                            f"{basename}: allowed upstream error: {message}"
                        )
                    else:
                        errors += 1
                        self.add("appstream", "appstreamcli", f"{basename}: {message}")
        # Count GUI entries without AppStream launchable metadata.  This is
        # #42 work, not a validation error, so report it as a note.
        launchables = set()
        for path in files:
            local = self.content_file(path)
            if not local:
                continue
            try:
                root = ET.parse(local).getroot()
            except ET.ParseError:
                continue
            for element in root.iter():
                if local_name(element.tag) == "launchable" and element.text:
                    launchables.add(element.text.strip())
        missing = []
        for path in self.desktop_files(("/usr/share/applications",)):
            parser = parse_desktop_file(path)
            if not parser:
                continue
            if parser.get("Desktop Entry", "NoDisplay", fallback="false").lower() == "true":
                continue
            desktop_id = path.name
            if desktop_id not in launchables:
                missing.append(desktop_id)
        if missing:
            self.note(
                "appstream",
                f"{len(missing)} application entries have no AppStream launchable "
                f"(#42): {', '.join(sorted(missing)[:5])}"
                + (" ..." if len(missing) > 5 else ""),
            )
        self.note(
            "appstream",
            f"appstreamcli: {len(files)} files, {errors} errors, {warnings} warnings "
            "(allowed)",
        )

    def check_icons(self) -> None:
        if not self.selected("icon-theme", "icon-naming"):
            return
        if not self.contents:
            self.note("icon-theme", "icon checks skipped: no RPMs or --root")
            self.note("icon-naming", "icon checks skipped: no RPMs or --root")
            return
        installed = set(self.theme_inherits)
        if not installed:
            self.add("icon-theme", "index.theme", "no installed icon themes found")
        for theme, inherits in sorted(self.theme_inherits.items()):
            for parent in inherits:
                if parent not in installed:
                    self.add(
                        "icon-theme",
                        "Inherits",
                        f"{theme}/index.theme inherits missing theme {parent!r}",
                    )
        all_stems = set(self.pixmap_icons)
        for stems in self.theme_icons.values():
            all_stems.update(stems)
        checked = 0
        for path in self.desktop_files(DESKTOP_ENTRY_DIRS):
            parser = parse_desktop_file(path)
            if not parser:
                continue
            icon = parser.get("Desktop Entry", "Icon", fallback="").strip()
            if not icon:
                continue
            checked += 1
            if icon.startswith("/"):
                if not self.has_path(icon):
                    self.add(
                        "icon-naming",
                        "Icon",
                        f"{path.name}: absolute icon {icon!r} is not installed",
                    )
                continue
            name = icon.rsplit("/", 1)[-1]
            stem, dot, _ = name.rpartition(".")
            candidates = {name}
            if dot:
                candidates.add(stem)
            if not candidates & all_stems:
                self.add(
                    "icon-naming",
                    "Icon",
                    f"{path.name}: Icon={icon!r} does not resolve in hicolor, "
                    "an installed theme, or /usr/share/pixmaps",
                )
        self.note("icon-naming", f"checked {checked} Icon= values in desktop entries")
        self.note("icon-theme", f"themes: {', '.join(sorted(installed)) or 'none'}")

    def check_shared_mime(self) -> None:
        if not self.selected("shared-mime-info"):
            return
        if not self.has_path("/usr/share/mime"):
            self.add("shared-mime-info", "layout", "/usr/share/mime is not shipped")
        if not self.contents:
            self.note("shared-mime-info", "MIME XML validation skipped: no RPMs or --root")
            return
        files = self.files_under("/usr/share/mime/packages", ".xml")
        if not files:
            self.add(
                "shared-mime-info", "layout", "/usr/share/mime/packages has no XML files"
            )
        for path in files:
            local = self.content_file(path)
            if not local:
                continue
            try:
                root = ET.parse(local).getroot()
            except ET.ParseError as error:
                self.add("shared-mime-info", "xml", f"{Path(path).name}: {error}")
                continue
            if local_name(root.tag) != "mime-info":
                self.add(
                    "shared-mime-info",
                    "xml",
                    f"{Path(path).name}: root element is not <mime-info>",
                )
        self.note("shared-mime-info", f"validated {len(files)} MIME package files")

    def check_mime_apps(self) -> None:
        if not self.selected("mime-apps"):
            return
        candidates = (
            "/etc/xdg/mimeapps.list",
            "/usr/share/applications/mimeapps.list",
            "/usr/share/applications/defaults.list",
        )
        found = next((path for path in candidates if self.has_path(path)), None)
        if not found:
            self.add("mime-apps", "layout", "no default mimeapps.list is shipped")
            return
        local = self.content_file(found)
        if not local:
            if self.contents:
                self.add("mime-apps", "parse", f"{found} could not be read")
            return
        parser = configparser.ConfigParser(strict=False, interpolation=None)
        try:
            parser.read(local)
        except configparser.Error as error:
            self.add("mime-apps", "parse", f"{found}: {error}")
            return
        if not parser.has_section("Default Applications"):
            self.add("mime-apps", "parse", f"{found}: no [Default Applications] section")
            return
        installed = self.installed_desktop_ids()
        defaults = parser["Default Applications"]
        for mime in MIME_DEFAULT_REQUIRED:
            if not defaults.get(mime):
                self.add("mime-apps", "defaults", f"no default association for {mime}")
        if not any(key.startswith("audio/") for key in defaults):
            self.add("mime-apps", "defaults", "no default audio association")
        if not any(key.startswith("video/") for key in defaults):
            self.add("mime-apps", "defaults", "no default video association")
        for mime, value in defaults.items():
            for desktop_id in (item.strip() for item in value.split(";")):
                if desktop_id and desktop_id not in installed:
                    self.add(
                        "mime-apps",
                        "defaults",
                        f"{mime}: {desktop_id} is not installed",
                    )
        self.note("mime-apps", f"defaults read from {found}")

    def check_menu(self) -> None:
        if not self.selected("menu"):
            return
        if not self.contents:
            self.note("menu", "menu validation skipped: no RPMs or --root")
            return
        files = self.files_under("/etc/xdg/menus", ".menu")
        if not files:
            self.add("menu", "layout", "no .menu file is shipped")
            return
        for path in files:
            local = self.content_file(path)
            if not local:
                continue
            try:
                root = ET.parse(local).getroot()
            except ET.ParseError as error:
                self.add("menu", "xml", f"{Path(path).name}: {error}")
                continue
            if local_name(root.tag) != "Menu":
                self.add(
                    "menu", "xml", f"{Path(path).name}: root element is not <Menu>"
                )
                continue
            for element in root.iter():
                if local_name(element.tag) != "Directory" or not element.text:
                    continue
                name = element.text.strip()
                if not any(
                    self.has_path(f"{base}/{name}")
                    for base in (
                        "/usr/share/desktop-directories",
                        "/etc/xdg/desktop-directories",
                        "/usr/local/share/desktop-directories",
                    )
                ):
                    self.add(
                        "menu",
                        "Directory",
                        f"{Path(path).name}: missing directory file {name!r}",
                    )
        self.note("menu", f"validated {len(files)} menu files")

    def check_help(self) -> None:
        if not self.selected("help-system"):
            return
        if not self.has_path("/usr/share/help"):
            self.add("help-system", "layout", "/usr/share/help is not shipped")
        elif not any(
            path.startswith("/usr/share/help/") and path.endswith("index.html")
            for path in self.paths
        ):
            self.add(
                "help-system",
                "layout",
                "no /usr/share/help/<id>/index.html page is shipped",
            )
        if not self.has_path("/usr/bin/tenko-help"):
            self.add(
                "help-system",
                "handler",
                "no help: URI handler is shipped (tenko-help)",
            )
        local = self.content_file("/etc/xdg/mimeapps.list")
        if local:
            parser = configparser.ConfigParser(strict=False, interpolation=None)
            try:
                parser.read(local)
            except configparser.Error:
                parser = None
            if parser is None or not parser.has_section("Default Applications"):
                self.add("help-system", "handler", "mimeapps.list cannot be parsed")
            else:
                value = parser["Default Applications"].get(
                    "x-scheme-handler/help", ""
                )
                if not value:
                    self.add(
                        "help-system",
                        "handler",
                        "x-scheme-handler/help has no default handler",
                    )
                else:
                    self.note("help-system", f"help: handler is {value}")
        elif self.contents:
            self.add(
                "help-system",
                "handler",
                "/etc/xdg/mimeapps.list is not shipped",
            )

    def check_triggers(self) -> None:
        wanted = {
            spec
            for spec, _command, _path in REQUIRED_TRIGGERS
            if self.selected(spec)
        }
        if not wanted:
            return
        triggers = []
        for package, text in self.spec_text.items():
            lines = text.splitlines()
            index = 0
            while index < len(lines):
                line = lines[index].strip()
                if not TRIGGER_RE.match(line):
                    index += 1
                    continue
                body = []
                cursor = index + 1
                while cursor < len(lines):
                    candidate = lines[cursor]
                    if not candidate.strip() or candidate.lstrip().startswith("%"):
                        break
                    body.append(candidate)
                    cursor += 1
                paths = []
                if "--" in line:
                    paths = [
                        normalize_macro(item)
                        for item in line.split("--")[-1].split()
                    ]
                triggers.append((package, line, paths, "\n".join(body)))
                index = cursor
        for spec, command, path in REQUIRED_TRIGGERS:
            if spec not in wanted:
                continue
            match = next(
                (
                    trigger
                    for trigger in triggers
                    if command in trigger[3]
                    and any(
                        item == path or item.startswith(path + "/")
                        for item in trigger[2]
                    )
                ),
                None,
            )
            if match:
                self.note(
                    spec,
                    f"{command} file trigger in {match[0]} for {path}",
                )
            else:
                self.add(
                    spec,
                    "trigger",
                    f"missing {command} file trigger for {path}",
                )

    def check_paths(self) -> None:
        required = (
            ("desktop-entry", "/usr/share/applications"),
            ("shared-mime-info", "/usr/share/mime/packages"),
            ("icon-theme", "/usr/share/icons"),
            ("appstream", "/usr/share/metainfo"),
            ("autostart", "/etc/xdg/autostart"),
            ("dbus", "/usr/share/dbus-1/services"),
            ("dbus", "/usr/share/dbus-1/system-services"),
            ("polkit", "/usr/share/polkit-1/actions"),
            ("sound-theme", "/usr/share/sounds/freedesktop"),
            ("xdg-desktop-portal", "/usr/share/xdg-desktop-portal/portals"),
        )
        for spec, path in required:
            if self.selected(spec) and not self.has_path(path):
                self.add(spec, "layout", f"{path} is not shipped")

    def check_basedir(self) -> None:
        if self.selected("basedir"):
            sysconfig = self.spec_text.get("tenko-sysconfig", "")
            basefs = self.spec_text.get("tenko-basefs", "")
            combined = sysconfig + "\n" + basefs
            if ".local/bin" not in combined:
                self.add(
                    "basedir",
                    "PATH",
                    "~/.local/bin is not added to PATH by tenko-sysconfig",
                )
        if self.selected("fhs"):
            basefs = self.spec_text.get("tenko-basefs", "")
            for path in FHS_REQUIRED_DIRS:
                if path not in basefs and not self.has_path(path):
                    self.add("fhs", "layout", f"{path} is not created")
        if self.selected("XDG user dirs"):
            if "xdg-user-dirs" not in self.spec_text:
                self.add("XDG user dirs", "package", "xdg-user-dirs is not packaged")
            elif not self.has_path("/usr/bin/xdg-user-dirs-update"):
                self.add(
                    "XDG user dirs",
                    "package",
                    "xdg-user-dirs-update is not shipped",
                )

    def check_dbus(self) -> None:
        if not self.selected("dbus"):
            return
        if not self.has_path("/usr/bin/dbus-daemon"):
            self.add("dbus", "package", "dbus-daemon is not shipped")
        if not self.contents:
            self.note("dbus", "D-Bus policy validation skipped: no RPMs or --root")
            return
        files = (
            self.files_under("/usr/share/dbus-1", ".conf")
            + self.files_under("/etc/dbus-1", ".conf")
        )
        for path in files:
            local = self.content_file(path)
            if not local:
                continue
            try:
                ET.parse(local)
            except ET.ParseError as error:
                self.add("dbus", "policy", f"{path}: {error}")
        self.note("dbus", f"validated {len(files)} D-Bus configuration files")

    def check_components(self) -> None:
        panel_plugins = self.files_under("/usr/share/xfce4/panel/plugins", ".desktop")
        panel_plugin_names = {path.rsplit("/", 1)[-1] for path in panel_plugins}
        path_names = {path.rsplit("/", 1)[-1] for path in self.paths}
        profile = self.desktop_profile_requires()

        if self.selected("appstream"):
            if "appstream" not in profile:
                self.add(
                    "appstream",
                    "profile",
                    "appstream is not required by the desktop profile",
                )
            if not self.has_path("/usr/bin/appstreamcli"):
                self.add("appstream", "package", "appstreamcli is not shipped")
        if self.selected("notification"):
            service = (
                "org.freedesktop.Notifications" in self.dbus_service_names
                or any(
                    path.endswith(".service") and "Notifications" in path
                    for path in self.paths
                )
            )
            if not service:
                self.add(
                    "notification",
                    "dbus",
                    "no D-Bus service provides org.freedesktop.Notifications",
                )
            if not ({"dunst", "xfce4-notifyd", "notification-daemon"} & profile):
                self.add(
                    "notification",
                    "profile",
                    "no notification daemon is required by the desktop profile",
                )
        if self.selected("secret-service"):
            service = (
                "org.freedesktop.secrets" in self.dbus_service_names
                or any("secrets.service" in path for path in self.paths)
            )
            if not service:
                self.add(
                    "secret-service",
                    "dbus",
                    "no D-Bus service provides org.freedesktop.secrets",
                )
            if not ({"gnome-keyring", "keepassxc", "kwallet"} & profile):
                self.add(
                    "secret-service",
                    "profile",
                    "no Secret Service provider is required by the desktop profile",
                )
        if self.selected("polkit"):
            agent = bool(
                path_names & {"xfce-polkit", "polkit-gnome-authentication-agent-1"}
            ) or any("polkit-authentication-agent" in path for path in self.paths)
            if not agent:
                self.add("polkit", "agent", "no polkit authentication agent is shipped")
            if not ({"xfce-polkit", "polkit-gnome"} & profile):
                self.add(
                    "polkit",
                    "profile",
                    "no polkit authentication agent is required by the desktop profile",
                )
            if self.contents:
                for path in self.files_under("/usr/share/polkit-1/actions", ".policy"):
                    local = self.content_file(path)
                    if not local:
                        continue
                    try:
                        ET.parse(local)
                    except ET.ParseError as error:
                        self.add("polkit", "policy", f"{Path(path).name}: {error}")
        if self.selected("recent-files"):
            if "gvfsd-recent" not in path_names:
                self.add("recent-files", "package", "gvfsd-recent is not shipped")
        if self.selected("trash"):
            if "gvfsd-trash" not in path_names:
                self.add("trash", "package", "gvfsd-trash is not shipped")
        if self.selected("thumbnail"):
            if "tumblerd" not in path_names and not self.has_path("/usr/share/thumbnailers"):
                self.add("thumbnail", "package", "no thumbnail service is shipped")
        if self.selected("sound-theme"):
            if not self.has_path("/usr/share/sounds/freedesktop/index.theme"):
                self.add(
                    "sound-theme",
                    "package",
                    "sound-theme-freedesktop is not installed",
                )
            if "sound-theme-freedesktop" not in profile:
                self.add(
                    "sound-theme",
                    "profile",
                    "sound-theme-freedesktop is not required by the desktop profile",
                )
        if self.selected("sound-naming"):
            sounds = self.files_under("/usr/share/sounds/freedesktop/stereo")
            if not sounds:
                self.add(
                    "sound-naming",
                    "package",
                    "no freedesktop sound-naming event sounds are installed",
                )
        if self.selected("xdg-desktop-portal"):
            if (
                "org.freedesktop.portal.Desktop" not in self.dbus_service_names
                and "xdg-desktop-portal" not in path_names
            ):
                self.add(
                    "xdg-desktop-portal", "package", "xdg-desktop-portal is not shipped"
                )
            portals = self.files_under(
                "/usr/share/xdg-desktop-portal/portals", ".portal"
            )
            if not portals:
                self.add(
                    "xdg-desktop-portal",
                    "backend",
                    "no portal backend .portal file is installed",
                )
            if "xdg-desktop-portal" not in profile:
                self.add(
                    "xdg-desktop-portal",
                    "profile",
                    "xdg-desktop-portal is not required by the desktop profile",
                )
        if self.selected("startup-notification"):
            if not any("libstartup-notification" in path for path in self.paths):
                self.add(
                    "startup-notification",
                    "package",
                    "libstartup-notification is not shipped",
                )
        if self.selected("systemtray", "xembed"):
            if "systray.desktop" not in panel_plugin_names and not any(
                "libsystray.so" in path for path in self.paths
            ):
                for spec in ("systemtray", "xembed"):
                    if self.selected(spec):
                        self.add(spec, "package", "xfce4-panel systray plugin is not shipped")
        if self.selected("wm"):
            if not self.has_path("/usr/bin/xfwm4"):
                self.add("wm", "package", "xfwm4 is not shipped")
        if self.selected("xsettings"):
            if not self.has_path("/usr/bin/xfsettingsd"):
                self.add("xsettings", "package", "xfsettingsd is not shipped")

    def check_mime_apps_profile(self) -> None:
        if self.selected("mime-apps"):
            profile = self.desktop_profile_requires()
            if "xdg-utils" not in profile:
                self.add(
                    "mime-apps",
                    "profile",
                    "xdg-utils is not required by the desktop profile",
                )
        if self.selected("desktop-entry"):
            profile = self.desktop_profile_requires()
            if "desktop-file-utils" not in profile:
                self.add(
                    "desktop-entry",
                    "profile",
                    "desktop-file-utils is not required by the desktop profile",
                )

    # -- report ----------------------------------------------------------
    def run(self) -> int:
        self.load_matrix()
        self.load_specs()
        self.load_filelists()
        self.load_inline_filelists()
        self.paths = set(self.static_paths)
        self.load_root()
        if self.root is not None:
            self.load_dbus_services()
            self.load_icon_themes()
        if not self.args.no_rpm:
            self.load_rpms()
        try:
            checks = (
                self.check_paths,
                self.check_desktop_entry,
                self.check_autostart,
                self.check_appstream,
                self.check_icons,
                self.check_shared_mime,
                self.check_mime_apps,
                self.check_mime_apps_profile,
                self.check_menu,
                self.check_help,
                self.check_triggers,
                self.check_basedir,
                self.check_dbus,
                self.check_components,
            )
            for check in checks:
                check()
            return self.report()
        finally:
            self.cleanup()

    def report(self) -> int:
        selected_rows = [
            self.rows[normalize_spec(key)]
            for key in SPEC_INDEX
            if normalize_spec(key) in self.rows and self.selected(key)
        ]
        failures = 0
        counters = {"PASS": 0, "OPEN": 0, "FAIL": 0, "N/A": 0}
        json_rows = []
        print("Tenko freedesktop compliance audit")
        print("=" * 78)
        for row in self.rows.values():
            unique = []
            seen = set()
            for finding in row.findings:
                key = (finding.check, finding.message)
                if key in seen:
                    continue
                seen.add(key)
                unique.append(finding)
            row.findings = unique
        if self.only is None or "docs" in self.only:
            doc_status = "PASS" if not self.doc_findings else "FAIL"
            print(
                f"{doc_status:<5} {'docs':<22} {'-':<11} "
                f"{len(self.rows)}/{len(SPEC_INDEX)} matrix rows"
            )
            for finding in self.doc_findings:
                print(f"      {finding.check}: {finding.message}")
                failures += 1
            print("-" * 78)
        for row in selected_rows:
            errors = row.errors
            warnings = row.warnings
            if row.disposition == "N/A":
                status = "FAIL" if errors else "N/A"
            elif errors:
                status = "FAIL" if row.disposition == "implemented" else "OPEN"
            else:
                status = "PASS" if row.disposition == "implemented" else "OPEN"
            counters[status] += 1
            if status == "FAIL":
                failures += 1
            issue = ""
            if status == "OPEN" and row.issues:
                issue = " -> " + ", ".join(row.issues)
            summary = row.evidence
            if errors:
                summary = f"{len(errors)} finding(s)" + issue
            elif row.disposition in ("partial", "gap"):
                summary = "no automated finding; verification pending" + issue
            print(
                f"{status:<5} {row.display:<22} {row.disposition:<11} "
                f"{summary}"
            )
            for finding in errors:
                print(f"      {finding.check}: {finding.message}")
            if self.args.verbose:
                for finding in warnings:
                    print(f"      warning: {finding.check}: {finding.message}")
                for note in row.notes:
                    print(f"      note: {note}")
            json_rows.append(
                {
                    "spec": row.spec,
                    "version": row.version,
                    "disposition": row.disposition,
                    "status": status,
                    "evidence": row.evidence,
                    "findings": [
                        {
                            "check": item.check,
                            "message": item.message,
                            "severity": item.severity,
                        }
                        for item in row.findings
                    ],
                    "notes": row.notes,
                }
            )
        print("-" * 78)
        print(
            "rows: {PASS} pass, {OPEN} open, {FAIL} fail, {N/A} N/A".format(**counters)
        )
        if self.warning_log:
            print(f"allowed warnings: {len(self.warning_log)}")
            if self.args.verbose:
                for line in self.warning_log:
                    print(f"  warning: {line}")
            else:
                print("  (run with --verbose for the list)")
        if self.args.json:
            print(
                json.dumps(
                    {
                        "rows": json_rows,
                        "doc_findings": [
                            {"check": f.check, "message": f.message}
                            for f in self.doc_findings
                        ],
                        "failures": failures,
                    },
                    indent=2,
                )
            )
        return 1 if failures else 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--rpm-dir",
        action="append",
        default=[],
        help="directory of built RPMs (repeatable); default: newest build/repo-publish/*",
    )
    parser.add_argument(
        "--root",
        help="already extracted root tree to audit instead of unpacking RPMs",
    )
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[2],
        type=Path,
        help="repository checkout root (default: parent of this script)",
    )
    parser.add_argument(
        "--spec-root",
        type=Path,
        help="package_specs directory (default: REPO_ROOT/package_specs)",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        help="matrix document (default: REPO_ROOT/docs/freedesktop.md)",
    )
    parser.add_argument(
        "--only",
        help="comma-separated spec keys to check (for debugging and tests)",
    )
    parser.add_argument(
        "--no-rpm",
        action="store_true",
        help="skip RPM scanning (static filelist/spec checks only)",
    )
    parser.add_argument("--verbose", action="store_true", help="show notes and allowed warnings")
    parser.add_argument("--json", action="store_true", help="also print a JSON report")
    args = parser.parse_args(argv)
    if args.spec_root is None:
        args.spec_root = args.repo_root / "package_specs"
    if args.doc is None:
        args.doc = args.repo_root / "docs" / "freedesktop.md"
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    auditor = Auditor(args)
    return auditor.run()


if __name__ == "__main__":
    sys.exit(main())
