from typing import Tuple, Type, Dict, Any

from fixkit.repair.repair import GeneticRepair
from fixkit.repair.pyae import PyAE
from fixkit.repair.pycardumen import PyCardumen
from fixkit.repair.pygenprog import PyGenProg
from fixkit.repair.pykali import PyKali
from fixkit.repair.pymutrepair import PyMutRepair

import argparse

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

def evaluate(approach: GeneticRepair, subject):



def almost_equal(value, target, delta=0.0001):
    return abs(value - target) < delta

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
    print(args)
    




if __name__ == "__main__":
    import sys

    main(sys.argv[1:])