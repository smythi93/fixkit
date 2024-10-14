from typing import Tuple, Type, Dict, Any, List
from pathlib import Path
from fixkit.repair.repair import GeneticRepair
from fixkit.repair.pyae import PyAE
from fixkit.repair.pycardumen import PyCardumen
from fixkit.repair.pygenprog import PyGenProg
from fixkit.repair.pykali import PyKali
from fixkit.repair.pymutrepair import PyMutRepair
from fixkit.localization.coverage import CoverageLocalization
from fixkit.genetic.minimize import DefaultMutationMinimizer

import shutil
import re
import os
import argparse
import time
import random
import numpy as np
import signal
from contextlib import contextmanager

REF_BENCHMARK = Path(__file__).parent / "refactory_benchmark"
QUESTION_1 = REF_BENCHMARK / "question_1" #575
QUESTION_2 = REF_BENCHMARK / "question_2" #435
QUESTION_3 = REF_BENCHMARK / "question_3" #308
QUESTION_4 = REF_BENCHMARK / "question_4" #357
QUESTION_5 = REF_BENCHMARK / "question_5" #108

OUTPUT = Path(__file__).parent / "results"
REP = Path(__file__).parent / "rep"

QUESTIONS = [QUESTION_1, QUESTION_2, QUESTION_3, QUESTION_4, QUESTION_5]
SEEDS = [7133,883,6465,7235,3735,5197,2570,3405,2155,9753,8013,3798,5637,
         7770,6056,2419,6841,1343,6924,9419,5416,6002,6862,5442,2971,1157,
         2225,1940,9408,6346]

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
            "max_generations": 1,
            "w_mut": 0.06,
            "workers": 32,
        },
    ),
    "MUTREPAIR": (
        PyMutRepair,
        {
            "max_generations": 1,
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
    "AE": (PyAE, {"k": 1}),
}

def parse_args(args) -> Tuple[Type[GeneticRepair], Dict[str, Any]]:
        parser = argparse.ArgumentParser(description="Evaluate the repair approaches.")
        parser.add_argument(
            "-a",
            help="The repair approach to evaluate.",
            required=True,
            dest="approach",
        )

        parser.add_argument(
            "-q",
            help="The question to evaluate",
            required=True,
            dest="question",
        )
        
        args = parser.parse_args(args)
        return (APPROACHES[args.approach.upper()],QUESTIONS[int(args.question)])

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

class EvalRunner:
    def __init__(self, approach, input_path, output_path, seed) -> None:
        self.approach = approach
        self.input_path = input_path
        self.output_path = output_path
        self.seed = seed
        self.set_seed()
        self.output_file = os.path.join(self.output_path, f"{approach.__name__}_{self.seed}_{self.get_question()}.txt")
        self.checkpoint = self.get_checkpoint()

    def get_checkpoint(self) -> int:
        if os.path.exists(self.output_file):
            with open(self.output_file) as file:
                lines = file.readlines()
                lines.reverse()
                number_pattern = re.compile(r'\d\d\d')
                #Sucht die letzte Line mit Zahl -> falls letzte Line Fehlermeldung ist
                for line in lines:
                    match = number_pattern.search(line)
                    if match:
                        return int(match.group())
        else:
            return 0

    def get_subject_numbers(self) -> List[str]:
        files = os.listdir(self.input_path)
        number_pattern = re.compile(r'\d\d\d')
        files = [s for s in files if number_pattern.match(s)]
        files.sort()
        
        return files

    def get_test_files(self) -> List[str]:
        files = os.listdir(self.subject_path)
        test_pattern = re.compile(r'test_.*\.py')
        test_files = [s for s in files if test_pattern.match(s)]

        return test_files

    def get_candidate_name(self) -> str:
        files = os.listdir(self.subject_path)
        candidate_pattern = re.compile('wrong_._...')
        #it should not fail but what if it does not find a match we get indexerror
        #try catch and then continue with next subject

        #the string with .py
        candidate_name = [s for s in files if candidate_pattern.match(s)][0]
        #the string without .py
        candidate_name = candidate_pattern.search(candidate_name).group()

        return candidate_name

    def get_excludes(self) -> List[str]:
        #einfach alles dem path außer den candidate!
        files = os.listdir(self.subject_path)
        candidate_pattern = re.compile('wrong_._...')

        #it should not fail but what if it does not find a match we get indexerror
        #try catch and then continue with next subject

        excludes = [s for s in files if not candidate_pattern.match(s)]

        return excludes
    
    def get_question(self) -> str:
        question_pattern = re.compile('question_.')
        match = question_pattern.search(str(self.input_path))
        question = match.group()

        return question

    def set_seed(self) -> None:
        random.seed(self.seed)
        np.random.seed(self.seed)
    
    def evaluate(self, parameters: Dict) -> None:
        subject_numbers = self.get_subject_numbers()
        for number in subject_numbers:
            if int(number) <= self.checkpoint:
                continue
            self.subject_path = self.input_path / number
            test_files = self.get_test_files()
            candidate_name = self.get_candidate_name()
            excludes = self.get_excludes()
            
            start = time.time()
            try:
                with time_limit(1800):
                    localization = CoverageLocalization(
                        src=self.subject_path,
                        timeout=60,
                        cov=candidate_name,
                        tests=test_files,
                        metric="Ochiai",
                        out=REP
                    )
                
                    repair = self.approach.from_source(
                        src=self.subject_path,
                        excludes=excludes,
                        localization=localization,
                        out=REP,
                        minimizer=DefaultMutationMinimizer(),
                        **parameters
                    )
                
                    patches = repair.repair()
            except Exception as ep:
                with open(self.output_file, "a") as f:
                    f.write(f"{repair.__class__.__name__},{number},{ep.__class__.__name__}\n")
            else:
                duration = time.time() - start
                found = False
                #Wieso macht das meine "patches" kaputt
                #engine = Tests4PyEngine(AbsoluteFitness(set(), set()), workers=32, out="rep")
                #engine.evaluate(patches)
                max_fitness = 0.0
                for patch in patches:
                    if patch.fitness > max_fitness:
                        max_fitness = patch.fitness
                    if almost_equal(patch.fitness, 1):
                        found = True
                        break        

                
                with open(self.output_file, "a") as f:
                    f.write(f"{repair.__class__.__name__},{number}, Found: {found}, Fitness: {max_fitness}, Duration: {duration} s\n")
                
            shutil.rmtree(REP, ignore_errors=True)
            
    def evaluate_debug(self, parameters: Dict, subject_number):
        self.subject_path = self.input_path / subject_number
        test_files = self.get_test_files()
        candidate_name = self.get_candidate_name()
        excludes = self.get_excludes()

        start = time.time()
        try:
            with time_limit(1800):
                localization = CoverageLocalization(
                    src=self.subject_path,
                    timeout=60,
                    cov=candidate_name,
                    tests=test_files,
                    metric="Ochiai",
                    out=REP
                )
            
                repair = self.approach.from_source(
                    src=self.subject_path,
                    excludes=excludes,
                    localization=localization,
                    out=REP,
                    minimizer=DefaultMutationMinimizer(),
                    **parameters
                )
            
                patches = repair.repair()
        except Exception as ep:
            with open(self.output_file, "a") as f:
                f.write(f"{repair.__class__.__name__},{subject_number},{ep.__class__.__name__}\n")
        else:
            duration = time.time() - start
            found = False
            #Wieso macht das meine "patches" kaputt
            #engine = Tests4PyEngine(AbsoluteFitness(set(), set()), workers=32, out="rep")
            #engine.evaluate(patches)
            max_fitness = 0.0
            for patch in patches:
                if patch.fitness > max_fitness:
                    max_fitness = patch.fitness
                if almost_equal(patch.fitness, 1):
                    found = True
                    break        

            
            with open(self.output_file, "a") as f:
                f.write(f"{repair.__class__.__name__},{subject_number}, Found: {found}, Fitness: {max_fitness}, Duration: {duration} s\n")
            
        shutil.rmtree(REP, ignore_errors=True)

def run(approach, parameters, question):
    for seed in SEEDS:     
        runner = EvalRunner(approach=approach, input_path=question, output_path=OUTPUT, seed=seed)
        runner.evaluate(parameters)

def debug(approach, parameters, question, subject_number, seed):
    runner = EvalRunner(approach=approach, input_path=question, output_path=OUTPUT, seed=seed)
    runner.evaluate_debug(parameters, subject_number)

#needs to be called with -a and -q (0-4)
def main(args):
    approach, question = parse_args(args)
    approach, parameters = approach
    #approach, parameters = APPROACHES["GENPROG"]
    #question = QUESTION_1
    run(approach, parameters, question)

    #subject_number = "434"
    #debug(approach, parameters, question, subject_number, 0)

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])