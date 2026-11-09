"""Update the running live installer from the package repository.

The installer is network-only and the live medium carries no RPMs, so a
freshly published tenko-installer can be picked up without rebuilding the
ISO: once the network works, check the same repository the target install
will use and, with the user's consent, upgrade the copy in the live root
(dmsquash-live keeps a writable tmpfs overlay) and restart the installer.

The restart is requested by returning :data:`RESTART` to the curses entry
point, which re-executes the (now updated) launcher after curses has
restored the terminal.
"""

from __future__ import annotations

import os
import re

from log import Logger
from runner import CommandRunner
from ui import CursesUI, Row

STEP = "self-update"
RELEASEVER = "6"
DEFAULT_CACHE_DIR = "/run/tenko/dnf-live"

# %{evr} is "version-release" or "epoch:version-release".  Filtering the
# output keeps a dnf warning on the combined stdout/stderr stream from being
# mistaken for the candidate version.
_EVR_RE = re.compile(r"^(?:\d+:)?[^-]+-[^-]+$")

# Exit status used by the interactive flow to ask the caller to exec the
# updated installer.
RESTART = 75


def repo_source(repo: str) -> str:
    """Return the repository in the form dnf expects for --repofrompath."""

    return repo if "://" in repo else "file://" + repo


def dnf_base(repo: str, cache_dir: str = DEFAULT_CACHE_DIR) -> list[str]:
    """Common dnf arguments for operating on the live root.

    The live repo file may be a different (older) release than the one the
    user selected for the target install, so use the install repository
    explicitly and keep metadata out of the live overlay.
    """

    return [
        "dnf",
        "--nogpgcheck",
        "--releasever=" + RELEASEVER,
        "--disablerepo=*",
        "--repofrompath=tenko-live," + repo_source(repo),
        "--setopt=install_weak_deps=False",
        "--setopt=cachedir=" + os.path.join(cache_dir, "cache"),
        "--setopt=persistdir=" + os.path.join(cache_dir, "persist"),
    ]


def installed_evr(runner: CommandRunner) -> str:
    """Return the EVR of the running tenko-installer, or "" if unknown."""

    result = runner.run(
        ("rpm", "-q", "--qf", "%{EVR}", "tenko-installer"),
        step=STEP,
        description="read the running installer version",
        read_only=True,
        allow_failure=True,
    )
    return result.output.strip() if result.rc == 0 else ""


def available_update(
    runner: CommandRunner,
    repo: str,
    cache_dir: str = DEFAULT_CACHE_DIR,
) -> str | None:
    """Return the candidate EVR when the repository has a newer installer.

    ``dnf repoquery --upgrades`` compares against the RPM database of the
    live root, so it handles epoch and release ordering without parsing
    versions here.  A repository or DNS failure is not fatal: the caller
    keeps the current installer and continues.
    """

    result = runner.run(
        dnf_base(repo, cache_dir)
        + [
            "-q",
            "--refresh",
            "repoquery",
            "--upgrades",
            "--latest-limit=1",
            "--qf",
            "%{evr}",
            "tenko-installer",
        ],
        step=STEP,
        description="check the repository for a newer installer",
        read_only=True,
        allow_failure=True,
    )
    if result.rc != 0:
        return None
    lines = [
        line.strip()
        for line in result.output.splitlines()
        if _EVR_RE.match(line.strip())
    ]
    return lines[-1] if lines else None


def offer_update(
    ui: CursesUI,
    runner: CommandRunner,
    logger: Logger,
    repo: str,
    *,
    cache_dir: str = DEFAULT_CACHE_DIR,
) -> bool:
    """Check for an installer update and optionally apply it.

    Returns True when the caller must restart the installer.  Any update
    failure is reported in the UI and leaves the current installer usable.
    """

    progress = ui.progress("Checking for installer updates", 1)
    try:
        progress.set_step(1, 1, "Reading the package repository")
        candidate = available_update(runner, repo, cache_dir)
        current = installed_evr(runner) if candidate is not None else ""
    except Exception as exc:  # the check must never block the install
        logger.error("self-update", status="check-failed", error=str(exc))
        candidate = None
        current = ""
    finally:
        progress.finish()
    if candidate is None:
        logger.info("self-update", status="current")
        return False
    logger.info(
        "self-update",
        status="available",
        current=current or None,
        candidate=candidate,
    )
    rows = [
        Row(
            "Update to {} and restart the installer".format(candidate),
            note="downloads from the network",
        ),
        Row(
            "Continue with the current installer"
            + (" ({})".format(current) if current else ""),
        ),
    ]
    choice = ui.menu(
        "Installer update available",
        "The repository has a newer tenko-installer.  Updating replaces the "
        "running copy in the live system (RAM only); the installation has "
        "not started yet.",
        rows,
        footer="Up/Down select   Enter continue",
        allow_rescan=False,
    )
    if choice != 0:
        logger.info("self-update", status="declined", candidate=candidate)
        return False

    progress = ui.progress("Updating the installer", 1)
    progress.set_step(1, 1, "Installing tenko-installer " + candidate)
    logger.console = progress.line
    failure = ""
    try:
        result = runner.run_streaming(
            dnf_base(repo, cache_dir) + ["-y", "upgrade", "tenko-installer"],
            progress.line,
            step=STEP,
            description="update the running installer",
        )
        if not result.ok:
            failure = "dnf exited with status {}".format(result.rc)
    except Exception as exc:  # a failed update must not end the installer
        failure = str(exc)
    finally:
        logger.console = None
        progress.finish()

    if failure:
        logger.error("self-update", status="failed", error=failure)
        ui.message(
            "Installer update failed",
            [
                "The update did not complete; the current installer will",
                "continue.",
                "",
                failure.splitlines()[0],
            ],
            footer="Press any key to continue",
        )
        return False

    logger.info("self-update", status="updated", candidate=candidate)
    ui.message(
        "Installer updated",
        [
            "tenko-installer {} was installed on the live system.".format(
                candidate
            ),
            "",
            "Press any key to restart the installer and start again.",
        ],
        footer="Press any key to restart",
    )
    return True
