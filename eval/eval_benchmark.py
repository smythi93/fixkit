from typing import Tuple, Type, Dict, Any
from pathlib import Path
from fixkit.repair.repair import GeneticRepair
from fixkit.repair.pyae import PyAE
from fixkit.repair.pycardumen import PyCardumen
from fixkit.repair.pygenprog import PyGenProg
from fixkit.repair.pykali import PyKali
from fixkit.repair.pymutrepair import PyMutRepair
from fixkit.localization.coverage import CoverageLocalization
from fixkit.fitness.engine import Tests4PyEngine
from fixkit.fitness.metric import AbsoluteFitness

import shutil
import re
import os
import re
import argparse
import time
import random
import numpy as np
import ast

REF_BENCHMARK = Path(__file__).parent / "refactory_benchmark"
QUESTION_1 = REF_BENCHMARK / "question_1" #575
QUESTION_2 = REF_BENCHMARK / "question_2" #435
QUESTION_3 = REF_BENCHMARK / "question_3" #308
QUESTION_4 = REF_BENCHMARK / "question_4" #357
QUESTION_5 = REF_BENCHMARK / "question_5" #108
REP = Path(__file__).parent / "rep"

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
    "AE": (PyAE, {"k": 1}),
}

def almost_equal(value, target, delta=0.0001):
    return abs(value - target) < delta

def parse_args(args) -> Tuple[Type[GeneticRepair], Dict[str, Any]]:
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
    return APPROACHES[args.approach.upper()]

def get_subject_numbers(question_path: Path):
    files = os.listdir(QUESTION_1)
    number_pattern = re.compile('\d\d\d')
    files = [s for s in files if number_pattern.match(s)]
    files.sort()
    
    return files

def get_test_files(subject_path: Path):
    files = os.listdir(subject_path)
    test_pattern = re.compile('test_.*\.py')
    test_files = [s for s in files if test_pattern.match(s)]

    return test_files

def get_candidate_name(subject_path: Path):
    files = os.listdir(subject_path)
    candidate_pattern = re.compile('wrong_._...')
    #it should not fail but what if it does not find a match we get indexerror
    #try catch and then continue with next subject

    #the string with .py
    candidate_name = [s for s in files if candidate_pattern.match(s)][0]
    #the string without .py
    candidate_name = candidate_pattern.search(candidate_name).group()

    return candidate_name

def get_excludes(subject_path: Path):
    #einfach alles dem path außer den candidate!
    files = os.listdir(subject_path)
    candidate_pattern = re.compile('wrong_._...')

    #it should not fail but what if it does not find a match we get indexerror
    #try catch and then continue with next subject

    excludes = [s for s in files if not candidate_pattern.match(s)]

    return excludes
    
def evaluate(appraoch: Type[GeneticRepair], question_path: Path, parameters: Dict):
    subject_numbers = get_subject_numbers(question_path)
    for number in subject_numbers:
        subject_path = question_path / number
        test_files = get_test_files(subject_path)
        candidate_name = get_candidate_name(subject_path)
        excludes = get_excludes(subject_path)

        #used for the txt write later on
        question_pattern = re.compile('question_.')
        match = question_pattern.search(str(question_path))
        question = match.group()

        
        start = time.time()

        localization = CoverageLocalization(
                src=subject_path,
                cov=candidate_name,
                tests=test_files,
                metric="Ochiai",
                out=REP
            )

        repair = appraoch.from_source(
                src=subject_path,
                excludes=excludes,
                localization=localization,
                out=REP,
                **parameters
            )
    #try:
        patches = repair.repair()            
    #except Exception as ep:
        #path = os.path.join(Path(__file__).parent, f"{repair.__class__.__name__}_{question}.txt")
        #with open(path, "a") as f:
            #f.write(f"{repair.__class__.__name__},{number},{ep.__class__.__name__}\n")
    #else:
        duration = time.time() - start
        found = False
        #Wieso macht das meine "patches" kaputt
        #engine = Tests4PyEngine(AbsoluteFitness(set(), set()), workers=32, out="rep")
        #engine.evaluate(patches)
        max_fitness = 0.0
        path = os.path.join(Path(__file__).parent, f"{repair.__class__.__name__}_{question}.txt")
        for patch in patches:
            if patch.fitness > max_fitness:
                max_fitness = patch.fitness
            if almost_equal(patch.fitness, 1):
                found = True
                break        

        
        with open(path, "a") as f:
            f.write(f"{repair.__class__.__name__},{number},Found: {found}, Fitness: {max_fitness}, Duration: {duration} s\n")
            
        shutil.rmtree(REP, ignore_errors=True)
            
        if(int(number) > 3):
            break

def main(args):
    random.seed(0)
    np.random.seed(0)
    
    approach, parameters = APPROACHES["CARDUMEN"]
    evaluate(approach, QUESTION_1, parameters)
    evaluate(approach, QUESTION_2, parameters)
    evaluate(approach, QUESTION_3, parameters)
    evaluate(approach, QUESTION_4, parameters)
    evaluate(approach, QUESTION_5, parameters)
 
    
if __name__ == "__main__":
    import sys
    main(sys.argv[1:])