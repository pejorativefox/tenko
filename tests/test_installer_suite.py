"""Run the installer suite from the documented top-level test command.

The installer tests live next to the package they test
(``package_specs/tenko-installer/tests``).  This module teaches
``unittest discover -s tests`` to include them, so one command covers both
suites without moving the tests away from the installer.
"""

import pathlib
import unittest

INSTALLER_TESTS = (
    pathlib.Path(__file__).resolve().parent.parent
    / "package_specs"
    / "tenko-installer"
    / "tests"
)


def load_tests(loader, standard_tests, pattern):
    """Add the installer suite to the tests discovered under ``tests/``."""
    standard_tests.addTests(
        loader.discover(
            str(INSTALLER_TESTS),
            pattern="test_*.py",
            top_level_dir=str(INSTALLER_TESTS),
        )
    )
    return standard_tests
