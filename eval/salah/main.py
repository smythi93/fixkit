import os
import re
import traceback
import csv

from pathlib import Path
from typing import List

from fixkit.repair.pygenprog import PyGenProg
from fixkit.localization.coverage import CoverageLocalization
from fixkit.genetic.minimize import DefaultMutationMinimizer


#Settings 
WORKERS = 1
MAX_GENERATION = 10
POPULATION_SIZE = 40
W_MUT = 0.06

REP = Path(__file__).parent / "rep"

def almost_equal(value, target, delta=0.0001):
    return abs(value - target) < delta

def get_test_files(tests_dir: Path) -> List[str]:
        files = os.listdir(tests_dir)
        test_pattern = re.compile(r'test_.*\.py')
        test_files = [s for s in files if test_pattern.match(s)]

        return test_files

if __name__ == "__main__":

    parameters = {
            "population_size": POPULATION_SIZE,
            "max_generations": MAX_GENERATION,
            "w_mut": W_MUT,
            "workers": WORKERS,
        }

    subject_dir = Path(__file__).parent / "subject"
    #tests_dir = Path("eval/salah/tests")
    results_dir = Path(__file__).parent / "results"
    
    candidate_name = "middle"
    test_files = get_test_files(subject_dir)
    print(subject_dir)
    print(results_dir)
    print(test_files)

    try:
        localization = CoverageLocalization(
                            src=subject_dir,
                            timeout=60,
                            cov=candidate_name,
                            tests=test_files,
                            metric="Ochiai",
                            out=REP
                        )
        repair = PyGenProg.from_source(
                            src=subject_dir,
                            excludes=["test_middle.py"],
                            localization=localization,
                            out=REP,
                            minimizer=DefaultMutationMinimizer(),
                            **parameters
                        )
        
        patches = repair.repair()

    except Exception as ep:
        with open(os.path.join(results_dir, "exception.txt"), "a") as f:
            traceback.TracebackException.from_exception(ep).print(file=f)
    
    else:
        max_fitness = 0.0
        found = False
        for patch in patches:
            if patch.fitness > max_fitness:
                max_fitness = patch.fitness
            if almost_equal(patch.fitness, 1):
                found = True
                break
        if not os.path.exists(os.path.join(results_dir, f"{repair.__class__.__name__}.csv")):
            with open(os.path.join(results_dir, f"{repair.__class__.__name__}.csv"), "a") as f:
                csvwriter = csv.writer(f, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
                csvwriter.writerow(["approach_name", "subject_name", "repair_found"])

        with open(os.path.join(results_dir, f"{repair.__class__.__name__}.csv"), "a") as f:
            csvwriter = csv.writer(f, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow([repair.__class__.__name__,candidate_name,found])
        