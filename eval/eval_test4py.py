import random
import time
import signal
import traceback
import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Any

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

TMP = Path(__file__).parent / "tmp"
SFLKIT_EVENTS = Path(__file__).parent / "sflkit_events"
OUTPUT = Path(__file__).parent / "results"
REP = Path(__file__).parent / "rep"
SEEDS_1 = [7133,883,6465,7235,3735,5197,2570,3405,2155,9753]

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
    "CARDUMEN": (
        PyCardumen,
        {
            "population_size": 40,
            "max_generations": 10,
            "w_mut": 0.06,
            "workers": 32,
        },
    ),
}

SUBJECTS = {
    #"MIDDLE": {
    #    1: t4p.middle_1,
    #    2: t4p.middle_2,
    #},
    "MARKUP": {
        1: t4p.markup_1,
        2: t4p.markup_2,
    },
    "EXPRESSION": {
        1: t4p.expression_1,
    },
    #"CALCULATOR": {
    #    1: t4p.calculator_1,
    #},
}


def almost_equal(value, target, delta=0.0001):
    return abs(value - target) < delta


class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

class EvalRunner():
    def __init__(self, subject: Project, approach: GeneticRepair, seed: int, output_path: Path):
        self.subject = subject
        self.approach = approach
        self.seed = seed
        self.set_seed(self.seed)
        self.output_path = output_path
        self.output_file = os.path.join(self.output_path, f"{approach.__name__}_{self.subject.get_identifier()}.txt")
    
    def set_seed(self, seed):
        random.seed(seed)
        np.random.seed(seed)

    def evaluate(self, parameters: Dict[str, Any]):
        #work_dir=Path(Path(__file__).parent, "tmp").absolute()
        report = t4p.checkout(project=self.subject)
        if report.raised:
            raise report.raised
        
        try:
            with time_limit(1800):
                start = time.time()
                approach = self.approach.from_source(
                    src=Path("tmp", self.subject.get_identifier()),
                    excludes=DEFAULT_EXCLUDES,
                    localization=Tests4PyLocalization(
                        src=Path("tmp", self.subject.get_identifier()),
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
        except Exception as ep:
            err_file = os.path.join(self.output_path, f"{self.approach.__class__.__name__}_err.txt")
            with open(err_file, "a") as f:
                f.write(f"{self.approach.__class__.__name__},{self.subject.get_identifier()},{self.seed},{ep.__class__.__name__}\n")
                traceback.TracebackException.from_exception(ep).print(file=f)
        
        else:
            found = False
            engine = Tests4PyEngine(AbsoluteFitness(set(), set()), workers=32, out="rep")
            engine.evaluate(patches)
            for patch in patches:
                if almost_equal(patch.fitness, 1):
                    found = True
                    break
            
            with open(self.output_file, "a") as f:
                        f.write(f"{approach.__class__.__name__}, Found: {found}, Fitness: Not measured, Duration: {duration} s, Seed: {self.seed}\n")
        
        shutil.rmtree(REP, ignore_errors=True)
        shutil.rmtree(TMP, ignore_errors=True)
        shutil.rmtree(SFLKIT_EVENTS, ignore_errors=True)

def test():
    approach = APPROACHES["GENPROG"]
    subject = SUBJECTS["EXPRESSION"][1]
    approach, parameters = approach
    runner = EvalRunner(subject=subject,approach=approach,seed=SEEDS_1[0],output_path=OUTPUT)
    runner.evaluate(parameters)

def complete_eval_run():
    for dict in SUBJECTS.values():
        for subject in dict.values():
            for approach in APPROACHES:
                approach, parameters = APPROACHES[approach]
                for seed in SEEDS_1:
                    runner = EvalRunner(subject=subject,approach=approach,seed=seed,output_path=OUTPUT)
                    runner.evaluate(parameters)


def main(args):
    test()
    #complete_eval_run()
    print(Path(Path(__file__).parent, "tmp").absolute())



if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
