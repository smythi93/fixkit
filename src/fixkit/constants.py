"""
This module contains the constants used in the fixkit package.
"""

import os
from pathlib import Path

DEFAULT_WORK_DIR = Path(os.getcwd(), "rep")
SFLKIT_EVENTS_PATH = Path("sflkit_events")


def XML_OUTPUT(name: str) -> Path:
    return Path(DEFAULT_WORK_DIR, f"{name}.xml")


DEFAULT_EXCLUDES = [
    "test/*",
    "tests/*",
    "test.py",
    "tests.py",
    "setup.py",
    "env",
    "build",
    "bin",
    "docs",
    "examples",
    "hacking",
    ".git",
    ".github",
    "extras",
    "profiling",
    "plugin",
    "gallery",
    "blib2to3",
    "docker",
    "contrib",
    "changelogs",
    "licenses",
    "packaging",
    "setupext.py",
    "*tests4py*",
]

__all__ = ["DEFAULT_EXCLUDES", "DEFAULT_WORK_DIR", "SFLKIT_EVENTS_PATH"]
