"""
This module contains the constants used in the pyrep package.
"""

import os
from pathlib import Path

DEFAULT_WORK_DIR = Path(os.getcwd(), "rep")
SFLKIT_EVENTS_PATH = Path("sflkit_events")

DEFAULT_EXCLUDES = [
    "test",
    "tests",
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
]

__all__ = ["DEFAULT_EXCLUDES", "DEFAULT_WORK_DIR", "SFLKIT_EVENTS_PATH"]
