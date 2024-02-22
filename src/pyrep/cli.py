import argparse
import os
import sys
from pathlib import Path
from typing import Sequence

from pyrep.repair import Mode


def parse_args(args: Sequence[str]):
    arguments = argparse.ArgumentParser(
        description="The access point to the pyrep framework"
    )

    arguments.add_argument(
        "-m",
        "--repair",
        help="the repair repair/technique (Default: pyGenProg)",
        default="pyGenProg",
    )
    arguments.add_argument(
        "-s", "--source", help="the path to the project under repair"
    )
    arguments.add_argument(
        "-f",
        "--failing",
        help="the failing test cases, separated by path separators (unix: ':', windows: ';'). "
        "Needs to be specified together with --passing, if not the unit tests will be used",
    )
    arguments.add_argument(
        "-p",
        "--passing",
        help="the failing test cases, separated by path separators (unix: ':', windows: ';'). "
        "Needs to be specified together with --failing, if not the unit tests will be used",
    )
    arguments.add_argument(
        "-t",
        "--test",
        default=Path("tests"),
        help="the relative path to the directory/file containing the unit tests (Default: /tests). Can also be test "
        "cases, separated by path separators (unix: ':', windows: ';'). If --failing and --passing are specified, "
        "this will be ignored",
    )
    arguments.add_argument(
        "-o",
        "--out",
        default=Path("tmp"),
        help="the output directory to store the results and intermediate files (Default: tmp)",
    )
    arguments.add_argument(
        "--gen",
        help="the maximal number of generation a program variant is evolved",
        type=int,
        default=None,
    )
    arguments.add_argument(
        "--pop",
        help="the number of population that will be evolved during one generation",
        type=int,
        default=None,
    )
    arguments.add_argument(
        "--time",
        help="the timeout (in minutes) for executing the whole experiment",
        type=float,
        default=None,
    )

    return arguments.parse_args(args)


def main(*args: str, stdout=sys.stdout, stderr=sys.stderr):
    if "-O" in sys.argv:
        sys.argv.remove("-O")
        os.execl(sys.executable, sys.executable, "-O", *sys.argv)

    if stdout is not None:
        sys.stdout = stdout
    if stderr is not None:
        sys.stderr = stderr

    args = parse_args(args)
    repair = Mode[args.mode.upper()].value(**vars(args))
    time = args.time
