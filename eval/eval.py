import argparse
import random
import time
from pathlib import Path
from typing import Type, Dict, Any, Tuple

import numpy as np
import tests4py.api as t4p
from tests4py.projects import Project

from fixkit.constants import DEFAULT_EXCLUDES
from fixkit.fitness.engine import Tests4PyEngine
from fixkit.fitness.metric import AbsoluteFitness
from fixkit.localization.t4p import Tests4PyLocalization
from fixkit.repair import GeneticRepair
from fixkit.repair.pygenprog import PyGenProg
from fixkit.repair.pykali import PyKali
from fixkit.repair.pymutrepair import PyMutRepair
from fixkit.repair.pycardumen import PyCardumen
from fixkit.repair.pyae import PyAE


random.seed(0)
np.random.seed(0)

APPROACHES = {
    "GENPROG": (
        PyGenProg,
        {
            "population_size": 40,
            "max_generations": 10,
            "w_mut": 0.06,
            "workers": 32,
        },
    ),
    "KALI": (
        PyKali,
        {
            "max_generations": 10,
            "w_mut": 0.06,
            "workers": 32,
        },
    ),
    "MUTREPAIR": (
        PyMutRepair,
        {
            "max_generations": 10,
            "w_mut": 0.06,
            "workers": 32,
        },
    ),
    "DEEPREPAIR": (None, {}),
    "CARDUMEN": (
        PyCardumen,
        {
            "population_size": 40,
            "max_generations": 10,
            "w_mut": 0.06,
            "workers": 32,
        },
    ),
    "AE": (PyAE, {"k": 1}),
    "SPR": (None, {}),
}

SUBJECTS = {
    "MIDDLE": {
        1: t4p.middle_1,
        2: t4p.middle_2,
    },
    "MARKUP": {
        1: t4p.markup_1,
        2: t4p.markup_2,
    },
    "EXPRESSION": {
        1: t4p.expression_1,
    },
    "CALCULATOR": {
        1: t4p.calculator_1,
    },
}


def almost_equal(value, target, delta=0.0001):
    return abs(value - target) < delta


def evaluate(
    approach: Type[GeneticRepair], subject: Project, parameters: Dict[str, Any]
):
    report = t4p.checkout(subject)
    if report.raised:
        raise report.raised
    start = time.time()
    approach = approach.from_source(
        src=Path("tmp", subject.get_identifier()),
        excludes=DEFAULT_EXCLUDES,
        localization=Tests4PyLocalization(
            src=Path("tmp", subject.get_identifier()),
            events=["line"],
            predicates=["line"],
            metric="Ochiai",
            out="rep",
        ),
        out="rep",
        is_t4p=True,
        **parameters,
    )
    patches = approach.repair()
    duration = time.time() - start
    found = False
    engine = Tests4PyEngine(AbsoluteFitness(set(), set()), workers=32, out="rep")
    engine.evaluate(patches)
    for patch in patches:
        if almost_equal(patch.fitness, 1):
            found = True
            break
    return found, duration


def parse_args(args) -> Tuple[Tuple[Type[GeneticRepair], Dict[str, Any]], Project]:
    parser = argparse.ArgumentParser(description="Evaluate the repair approaches.")
    parser.add_argument(
        "-a",
        help="The repair approach to evaluate.",
        required=True,
        dest="approach",
    )
    parser.add_argument(
        "-s",
        help="The subject to evaluate.",
        required=True,
        dest="subject",
    )
    parser.add_argument(
        "-i",
        help="The bug id to evaluate.",
        required=True,
        type=int,
        dest="bug_id",
    )
    args = parser.parse_args(args)
    return (
        APPROACHES[args.approach.upper()],
        SUBJECTS[args.subject.upper()][args.bug_id],
    )


def main(args):
    approach, subject = parse_args(args)
    approach, parameters = approach
    found, duration = evaluate(approach, subject, parameters)
    with open(f"{approach.__name__}_{subject.get_identifier()}.txt", "w") as f:
        f.write(f"{approach.__name__},{subject.get_identifier()},{found},{duration}\n")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
