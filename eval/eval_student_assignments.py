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

import itertools
import traceback
import shutil
import re
import os
import argparse
import time
import random
import numpy as np
import signal
import json
import fileinput
import tempfile
from contextlib import contextmanager

#Settings 
WORKERS = 1
MAX_GENERATION = 10
POPULATION_SIZE = 40
W_MUT = 0.06

#local
REF_BENCHMARK = Path(__file__).parent / "refactory_benchmark"
QUESTION_1 = REF_BENCHMARK / "question_1" #575
QUESTION_2 = REF_BENCHMARK / "question_2" #435
QUESTION_3 = REF_BENCHMARK / "question_3" #308
QUESTION_4 = REF_BENCHMARK / "question_4" #357
QUESTION_5 = REF_BENCHMARK / "question_5" #108

OUTPUT = Path(__file__).parent / "results"
REP = Path(__file__).parent / "rep"

QUESTIONS = [QUESTION_1, QUESTION_2, QUESTION_3, QUESTION_4, QUESTION_5]

#slurm gruenau
REF_BENCHMARK_SLURM = Path("/vol/tmp/werkkai/fixkit/eval/refactory_benchmark")
QUESTION_1_SLURM = REF_BENCHMARK_SLURM / "question_1" #575
QUESTION_2_SLURM = REF_BENCHMARK_SLURM / "question_2" #435
QUESTION_3_SLURM = REF_BENCHMARK_SLURM / "question_3" #308
QUESTION_4_SLURM = REF_BENCHMARK_SLURM / "question_4" #357
QUESTION_5_SLURM = REF_BENCHMARK_SLURM / "question_5" #108

COUNT_TOTAL_SUBJECTS = {
    1 : 575,
    2 : 435,
    3 : 308,
    4 : 357,
    5 : 108,
}

QUESTIONS_SLURM = [QUESTION_1_SLURM, QUESTION_2_SLURM, QUESTION_3_SLURM, QUESTION_4_SLURM, QUESTION_5_SLURM]

OUTPUT_SLURM = Path("/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results")
REP_SLURM = Path(__file__).parent / "rep"

SEEDS_1 = [7133,883,6465,7235,3735,5197,2570,3405,2155,9753]
SEEDS_2 = [8013,3798,5637,7770,6056,2419,6841,1343,6924,0]
SEEDS_3 = [5416,6002,6862,5442,2971,1157,2225,1940,9408,6346]

APPROACHES = {
    "GENPROG": (
        PyGenProg,
        {
            "population_size": POPULATION_SIZE,
            "max_generations": MAX_GENERATION,
            "w_mut": W_MUT,
            "workers": WORKERS,
        },
    ),
    "KALI": (
        PyKali,
        {
            "max_generations": 1,
            "w_mut": W_MUT,
            "workers": WORKERS,
        },
    ),
    "MUTREPAIR": (
        PyMutRepair,
        {
            "max_generations": 1,
            "w_mut": W_MUT,
            "workers": WORKERS,
        },
    ),
    "CARDUMEN": (
        PyCardumen,
        {
            "population_size": POPULATION_SIZE,
            "max_generations": MAX_GENERATION,
            "w_mut": W_MUT,
            "workers": WORKERS,
        },
    ),
    #"AE": (PyAE, {"k": 1}),
}

APPROACHES_FOR_CORRUPTED_DATA = {
    "PyGenProg": (
        PyGenProg,
        {
            "population_size": POPULATION_SIZE,
            "max_generations": MAX_GENERATION,
            "w_mut": W_MUT,
            "workers": WORKERS,
        },
    ),
    "PyKali": (
        PyKali,
        {
            "max_generations": 1,
            "w_mut": W_MUT,
            "workers": WORKERS,
        },
    ),
    "PyMutRepair": (
        PyMutRepair,
        {
            "max_generations": 1,
            "w_mut": W_MUT,
            "workers": WORKERS,
        },
    ),
    "PyCardumen": (
        PyCardumen,
        {
            "population_size": POPULATION_SIZE,
            "max_generations": MAX_GENERATION,
            "w_mut": W_MUT,
            "workers": WORKERS,
        },
    ),
    #"AE": (PyAE, {"k": 1}),
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
    def __init__(self, approach, input_path, output_path, seed, slurm=False) -> None:
        self.approach = approach
        self.input_path = input_path
        self.output_path = output_path
        self.seed = seed
        self.set_seed()
        self.output_file = os.path.join(self.output_path, f"{approach.__name__}_{self.get_question()}_{self.seed}.txt")
        #checkpoint where the evaluation stopped last time
        self.checkpoint = self.get_checkpoint(self.output_file)
        #Subjects are all the faulty programs for one question
        self.subject_numbers = self.get_subject_numbers(self.input_path)

    def set_seed(self) -> None:
        random.seed(self.seed)
        np.random.seed(self.seed)

    def get_checkpoint(self, output_file: Path) -> int:
        if os.path.exists(output_file):
            with open(output_file) as file:
                lines = file.readlines()
                lines.reverse()
                number_pattern = re.compile(r'\d\d\d')
                #Sucht die letzte Line mit Zahl -> falls letzte Line Fehlermeldung ist
                for line in lines:
                    match = number_pattern.search(line)
                    if match:
                        return int(match.group())
            return 0
        else:
            return 0

    def get_subject_numbers(self, input_path: Path) -> List[str]:
        files = os.listdir(input_path)
        number_pattern = re.compile(r'\d\d\d')
        files = [s for s in files if number_pattern.match(s)]
        files.sort()
        
        return files

    def get_test_files(self, subject_path: Path) -> List[str]:
        files = os.listdir(subject_path)
        test_pattern = re.compile(r'test_.*\.py')
        test_files = [s for s in files if test_pattern.match(s)]

        return test_files

    def get_candidate_name(self, subject_path: Path) -> str:
        files = os.listdir(subject_path)
        candidate_pattern = re.compile('wrong_._...')
        #it should not fail but what if it does not find a match we get indexerror
        #try catch and then continue with next subject

        #the string with .py
        candidate_name = [s for s in files if candidate_pattern.match(s)][0]
        #the string without .py
        candidate_name = candidate_pattern.search(candidate_name).group()

        return candidate_name

    def get_excludes(self, subject_path: Path) -> List[str]:
        #einfach alles dem path außer den candidate!
        files = os.listdir(subject_path)
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
    
    def evaluate(self, parameters: Dict) -> None:
        subject_numbers = self.get_subject_numbers(self.input_path)
        for number in subject_numbers:
            if int(number) <= self.checkpoint:
                continue
            subject_path = self.input_path / number
            test_files = self.get_test_files(subject_path)
            candidate_name = self.get_candidate_name(subject_path)
            excludes = self.get_excludes(subject_path)
            
            start = time.time()
            try:
                with time_limit(1800):
                    localization = CoverageLocalization(
                        src=subject_path,
                        timeout=60,
                        cov=candidate_name,
                        tests=test_files,
                        metric="Ochiai",
                        out=REP
                    )
                
                    repair = self.approach.from_source(
                        src=subject_path,
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

                err_file = os.path.join(self.output_path, f"{repair.__class__.__name__}_err.txt")
                with open(err_file, "a") as f:
                    f.write(f"{repair.__class__.__name__},{self.get_question()},{number},{self.seed},{ep.__class__.__name__}\n")
                    traceback.TracebackException.from_exception(ep).print(file=f)

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
        subject_path = self.input_path / subject_number
        test_files = self.get_test_files()
        candidate_name = self.get_candidate_name()
        excludes = self.get_excludes()

        start = time.time()
        try:
            with time_limit(1800):
                localization = CoverageLocalization(
                    src=subject_path,
                    timeout=60,
                    cov=candidate_name,
                    tests=test_files,
                    metric="Ochiai",
                    out=REP
                )
            
                repair = self.approach.from_source(
                    src=subject_path,
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
                
                err_file = os.path.join(self.output_path, f"{repair.__class__.__name__}_err.txt")
                with open(err_file, "a") as f:
                    f.write(f"{repair.__class__.__name__},{self.get_question()},{subject_number},{self.seed},{ep.__class__.__name__}\n")
                    traceback.TracebackException.from_exception(ep).print(file=f)

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
    
    def evaluate_debug_slurm(self, parameters: Dict, subject_number):
        subject_path = self.input_path / subject_number
        test_files = self.get_test_files(subject_path)
        candidate_name = self.get_candidate_name(subject_path)
        excludes = self.get_excludes(subject_path)

        start = time.time()
        try:
            with time_limit(1800):
                localization = CoverageLocalization(
                    src=subject_path,
                    timeout=60,
                    cov=candidate_name,
                    tests=test_files,
                    metric="Ochiai",
                    out=REP
                )
            
                repair = self.approach.from_source(
                    src=subject_path,
                    excludes=excludes,
                    localization=localization,
                    out=REP,
                    minimizer=DefaultMutationMinimizer(),
                    **parameters
                )
            
                patches = repair.repair()
        except Exception as ep:
                tempfile_name = tempfile.NamedTemporaryFile(delete=False).name

                with open(self.output_file, "r") as original, open(tempfile_name, "w") as temp:
                    for idx, line in enumerate(original, start=1):
                        if idx == int(subject_number):
                            temp.write(f"{repair.__class__.__name__},{subject_number},{ep.__class__.__name__}\n")
                        else:
                            temp.write(line)

                # Temporäre Datei ersetzen die Originaldatei
                shutil.move(tempfile_name, self.output_file)
                
                err_file = os.path.join(self.output_path, f"{repair.__class__.__name__}_err.txt")
                with open(err_file, "a") as f:
                    f.write(f"{repair.__class__.__name__},{self.get_question()},{subject_number},{self.seed},{ep.__class__.__name__}\n")
                    traceback.TracebackException.from_exception(ep).print(file=f)

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

            tempfile_name = tempfile.NamedTemporaryFile(delete=False).name

            with open(self.output_file, "r") as original, open(tempfile_name, "w") as temp:
                lines = original.readlines()
                for idx, line in enumerate(lines, start=1):
                    if idx == int(subject_number):
                        temp.write(f"{repair.__class__.__name__},{subject_number}, Found: {found}, Fitness: {max_fitness}, Duration: {duration} s\n")
                    else:
                        temp.write(line)

            shutil.move(tempfile_name, self.output_file)
            #os.remove(self.output_file)
            #os.rename()
            
        shutil.rmtree(REP, ignore_errors=True)

def run_local(approach, parameters, question):
    for seed in SEEDS_1:
        runner = EvalRunner(approach=approach, input_path=question, output_path=OUTPUT_SLURM, seed=seed)
        runner.evaluate(parameters)

def run_slurm(approach, parameters, question, seed):   
    runner = EvalRunner(approach=approach, input_path=question, output_path=OUTPUT_SLURM, seed=seed)
    runner.evaluate(parameters)

def run_slurm_old(approach, parameters, question, seed):
    for seed in SEEDS_1:
        runner = EvalRunner(approach=approach, input_path=question, output_path=OUTPUT_SLURM, seed=seed)
        runner.evaluate(parameters)


def debug_local(approach, parameters, question, subject_number, seed):
    runner = EvalRunner(approach=approach, input_path=question, output_path=OUTPUT, seed=seed)
    runner.evaluate_debug(parameters, subject_number)

def debug_slurm(approach, parameters, question, subject_number, seed):
    runner = EvalRunner(approach=approach, input_path=question, output_path=OUTPUT_SLURM, seed=seed)
    runner.evaluate_debug_slurm(parameters, subject_number)

#needs to be called with -a and -q (0-4)
#if execution with slurm run via slurm.sh

#TODO:
# better debugging possibilities
# wenn keine coverage gemacht werden kann könnte man auch einfach sagen das alle locations gleiche weights bekommen !!!
# Bisher nur Problem bei Cardumen gewesen, aber mit Marius besprechen wäre elegante Lösung
# AE

def main(args):
    debugging = False
    local =  False
    slurm = False
    slurm_old = False
    fix_corrupted = True

    if(fix_corrupted):
        with open("corrupted_data.json") as f:
            data = json.load(f)
            data = [entry for entry in data if entry[2] != "TimeoutException" and entry[2] != "TimeoutExpired"]
            print(data)
            for entry in data:
                approach, parameters = APPROACHES_FOR_CORRUPTED_DATA[entry[0]]
                question = QUESTIONS_SLURM[int(entry[3])-1]
                subject_number = entry[1]
                seed = int(entry[4])
                print("start")
                debug_slurm(approach, parameters, question, subject_number, seed)
                print(f"finished: {approach, question, subject_number, seed}")

    
    if(slurm_old):
        input_id = int(args[0])
        approaches_names = ["GENPROG", "KALI", "MUTREPAIR", "CARDUMEN"]
        question = QUESTIONS_SLURM[input_id//4]
        approach, parameters = APPROACHES[approaches_names[input_id%5]]

    if (slurm):
        
        #input_id = int(args[0])
        #approaches_names = ["GENPROG", "KALI", "MUTREPAIR", "CARDUMEN"]
        #all_combinations = list(itertools.product(approaches_names, QUESTIONS_SLURM, SEEDS_2))
        #approach_name, question, seed = all_combinations[input_id]
        #approach, parameters = APPROACHES[approach_name]
        approach, parameters = APPROACHES["CARDUMEN"]
        question = QUESTION_5_SLURM
        seed = 8013
        #nochmal schauen am anfang wurde einer doppelt ausgeführt!!
        run_slurm(approach, parameters, question, seed)

    if (local):
        approach, question = parse_args(args)
        approach, parameters = approach
        approach, parameters = APPROACHES["GENPROG"]
        question = QUESTION_1
        run_local(approach, parameters, question)
    
    if (debugging and local):
        approach, parameters = APPROACHES["GENPROG"]
        subject_number = "434"
        seed = 0
        debug_local(approach, parameters, question, subject_number, seed)

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])