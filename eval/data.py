from pathlib import Path
from typing import List, Dict, Set, Tuple
from itertools import chain, combinations
import re
import matplotlib.pyplot as plt
import os
import numpy
import subprocess

QUESTION_1 = Path(__file__).parent / "results" / "question_1"
QUESTION_2 = Path(__file__).parent / "results" / "question_2"
QUESTION_3 = Path(__file__).parent / "results" / "question_3"
QUESTION_4 = Path(__file__).parent / "results" / "question_4"
QUESTION_5 = Path(__file__).parent / "results" / "question_5"
RESULTS = Path(__file__).parent / "results"


APPROACHES = ["PyCardumen", "PyKali", "PyGenProg", "PyMutRepair"]
OUTPUT = Path(__file__).parent
SEEDS_1 = [7133,883,6465,7235,3735,5197,2570,3405,2155,9753]

COUNT_TOTAL_SUBJECTS = {
    1 : 575,
    2 : 435,
    3 : 308,
    4 : 357,
    5 : 108,
}

class SubjectData:
    def __init__(self, file):
        self.seed: int = self.get_seed(file)
        self.question: int = self.get_question(file)
        self.approach: str = self.get_appraoch(file)
        self.data = self.get_data(file)

        self.subjects = [int(entry[1]) for entry in self.data if len(entry) == 5]
        self.fitness = [float(entry[3]) for entry in self.data if len(entry) >= 5]
        self.durations = [float(entry[4]) for entry in self.data if len(entry) >= 5]
        self.found_repairs = [entry[2].strip() for entry in self.data if len(entry) >= 5]
    
    def get_seed(self, file: Path) -> str|None:
        match: re.Match = re.search(r'(\d+)(?=\.txt)', file)

        if match:
            return match.group(1)
        return None
    
    def get_question(self, file: Path) -> str|None:
        match: re.Match = re.search(r'_(\d+)_\d+\.txt$', file)

        if match:
            return int(match.group(1))
        else:
            return None

    def get_appraoch(self, file: Path) -> str|None:
        match: re.Match = re.search(r'/results/([^_]+)_', file)
    
        if match:
            return match.group(1)
        else:
            return None

    def get_data(self, file: Path) -> List[List[str]]:
        with open(file) as f:
            lines = f.readlines()
            complete_data = []
            for line in lines:
                cleaned_line = (line.replace("Found: ", "")
                            .replace("Fitness: ", "")
                            .replace("Duration: ", "")
                            .replace(" s", "")
                            .strip())
                data = cleaned_line.split(",")
                complete_data.append(data)
            return complete_data

def create_subject_data(result_path: str) -> List[SubjectData]:
    data = []
    files = [os.path.join(result_path, f) for f in os.listdir(result_path)]
    
    for file in files:
        subject = SubjectData(file)
        data.append(subject)

    return data

def find_corrupted_data(result_path: str) -> List[str]:
    all_subjects: List[SubjectData] = []
    files = [os.path.join(result_path, f) for f in os.listdir(result_path)]
    
    for file in files:
        subject = SubjectData(file)
        all_subjects.append(subject)
    
    corrupted_data = []
    for subject in all_subjects:
        filtered_data = [entry for entry in subject.data if len(entry) == 3]
        for entry in filtered_data:
            entry.append(subject.question)
            entry.append(subject.seed)
            corrupted_data.append(entry)
    
    #[ApproachName, SubjectNumber, Exception, Question, Seed]
    return corrupted_data

def find_uncomplete_data(result_path: str) -> List[str]:
    all_subjects: List[SubjectData] = []
    files = [os.path.join(result_path, f) for f in os.listdir(result_path)]
    
    for file in files:
        subject = SubjectData(file)
        all_subjects.append(subject)
    
    uncomplete_data = []
    for subject in all_subjects:
        if subject.question == 1 and len(subject.data) == 575:
            continue
        elif subject.question == 2 and len(subject.data) == 435:
            continue
        elif subject.question == 3 and len(subject.data) == 308:
            continue
        elif subject.question == 4 and len(subject.data) == 357:
            continue
        elif subject.question == 5 and len(subject.data) == 108:
            continue
        else:
            subject_info = [subject.approach, subject.question, subject.seed]
            uncomplete_data.append(subject_info)

    #[ApproachName, Question, Seed]
    return uncomplete_data

#gives back the total repairs found for a question for a single approach
def found_repairs_question_approach(data: List[SubjectData], question: int, approach: str) -> Dict[int, int]:
    """
    returns: Dict[int,int]
    First int seed of run
    second int total repairs of the approach in the run with the seed
    """
    total_repairs = {}

    for subject in data:
        if subject.question != question or subject.approach != approach:
            continue

        for entry in subject.found_repairs:
            if entry == "True":
                try:
                    count = total_repairs[subject.seed]
                except KeyError:
                    count = 0
                count+=1
                total_repairs[subject.seed] = count
    
    return total_repairs

#gives back the repairs found for a question for every approach
def found_repairs_question(data: List[SubjectData], question: int) -> Dict[str, Dict[int, int]]:
    """
    returns: Dict[str, Dict[int,int]]
    str: the approach
    first int: the seed of a run with the approach
    second int: total repairs of the run with the seed
    """
    repairs = {}
    for approach in APPROACHES:
        repairs[approach] = found_repairs_question_approach(data, question, approach)

    return repairs

def plot_repairs_found(repairs, question):
    # Extract the repair values for each approach for the box plot
    repair_data = [list(approach.values()) for approach in repairs.values()]
    labels = list(repairs.keys())

    # Create the box plot
    plt.figure(figsize=(10, 6))
    plt.boxplot(repair_data, labels=labels, patch_artist=True)

    # Add titles and labels
    plt.title("Distribution of Repairs Found by Different Approaches")
    plt.xlabel("Approach")
    plt.ylabel("Repairs Found")

    # Show the plot
    plt.savefig(os.path.join(Path(__file__).parent , f"found_repairs_question_{question}.pdf"))

class Repair:
    """
    the identification of a single repair 
    of the refactory benchmark
    """
    def __init__(self, approach: str, question: int, seed: int, id: int, time: float):
        self.approach: str = approach
        self.question: int = question
        self.seed: int = seed
        self.id: int = id
        self.time: float = time

    def __eq__(self, other):
        return (isinstance(other, Repair) 
                and self.approach == other.approach 
                and self.question == other.question 
                and self.seed == other.seed 
                and self.id == other.id 
                and self.time == other.time)

    def __hash__(self):
        return hash((self.approach, self.question, self.seed, self.id, self.time))
    
class ApproachRepairData:
    """
    a collection of repairs for a approach 
    of all the questions of the refactory benchmark
    """
    def __init__(self, approach: str, repairs: List[Repair]):
        self.approach_name = approach
        self.repairs = repairs

def create_repair_data(data: List[SubjectData]) -> List[ApproachRepairData]:
    repair_data = []
    #find all repairs from one approach
    for approach in APPROACHES:
        repairs = []
        for subject in data:
            if subject.approach == approach:
                for id, entry in enumerate(subject.found_repairs):
                    if entry == "True":
                        #das ist ein bisschen hässlich aber ist jetzt so
                        bug_id = subject.subjects[id]
                        time = subject.durations[id]
                        #HIER PROBLEM DAS ES MANCHMAL GLEICHE REPAIRS GIBT MIT UNTERSCHIEDLICHEN SEEDS
                        repair = Repair(subject.approach, subject.question, subject.seed, bug_id, time)
                        repairs.append(repair)
        repair_data.append(ApproachRepairData(approach, repairs))
    
    assert(len(repair_data) == len(APPROACHES))

    return repair_data

def count_total_repairs(repair_data: List[ApproachRepairData], question: int = 0, filter: bool = False) -> Dict[str, Dict[int,int]]:
    """
    returns: Dict[str, Dict[int,int]]
    str: approach name
    first int: seed
    second int: total repairs of this seed
    """
    
    #filter data if only interested in specific question
    data = dict()
    for approach in repair_data:
        if filter:
            data[approach.approach_name] = set([repair for repair in approach.repairs if repair.question == question])
        else:
            data[approach.approach_name] = set([repair for repair in approach.repairs])

    #calculate total repairs for every approach for every seed/run
    results = dict()
    for approach in data:
        approach_repairs = dict()
        for repair in data[approach]:
            repair: Repair
            try: 
                count = approach_repairs[repair.seed]
            except KeyError:
                count = 0
            count+=1
            approach_repairs[repair.seed] = count
        results[approach] = approach_repairs
    
    #assert every seed exists as key
    for approach in results:
        assert(len(SEEDS_1) == len(results[approach].values()))

    #calculate total repairs of all approaches together for a seed/run
    all_total_repairs = dict()
    for approach in results:
        approach_repairs = results[approach]
        for seed in approach_repairs:
            try:
                count = all_total_repairs[seed]
            except KeyError:
                count=0
            count+=approach_repairs[seed]
            all_total_repairs[seed] = count
    results["all"] = all_total_repairs

    return results


def find_unique_repairs(repair_data: List[ApproachRepairData], question: int = 0, filter: bool = False) -> Dict[str, Set[Tuple[int, int]]]:
    #find repairs of approach
    data = dict()
    for approach in repair_data:
        if filter:
            data[approach.approach_name] = set([repair for repair in approach.repairs if repair.question == question])
        else:
            data[approach.approach_name] = set([repair for repair in approach.repairs])

    #collect all the repairs from the other approaches
    other_repairs = dict()
    for approach in data.keys():
        other_repairs_approach = set()
        for other in data.keys():
            if approach != other:
                other_repairs_approach = set.union(other_repairs_approach, data[other])
        other_repairs[approach] = other_repairs_approach

    # Find uniques  
    uniques = dict()
    for approach in data:
        uniques_approach = {repair for repair in data[approach] if (repair.question, repair.id) not in {(other.question, other.id) for other in other_repairs[approach]}}
        
        # delete multiple repairs from different seeds and only keep one
        tmp = dict()
        for repair in uniques_approach:
            key = (repair.id, repair.question)
            if key not in tmp:
                tmp[key] = repair
        uniques_approach = set(tmp.values())

        uniques_approach = tuple(sorted(uniques_approach, key=lambda t: (t.question, t.id)))
        uniques[approach] = uniques_approach
    
    with open(os.path.join(OUTPUT, "unique_repairs"), "a") as f:
        if filter:
            for k,v in uniques.items():
                f.write(f"Approach: {k}\n")
                f.write(f"{len(v)} Unique Repairs found for approach {k} and question_{question}\n")
                for repair in v:
                    f.write(f"{(repair.question, repair.id) }")
                f.write(f"\n\n")
        else:
            for k,v in uniques.items():
                f.write(f"Approach: {k}\n")
                f.write(f"{len(v)} Unique Repairs found for {k}\n")
                for repair in v:
                    f.write(f"{(repair.question, repair.id) }")
                f.write(f"\n\n")
    
    return uniques

#common repairs with total common repairs (non exklusive) by approach
def common_repairs_by_approach_combination(data):
    powerset = chain.from_iterable(combinations(APPROACHES, r) for r in range(1,len(APPROACHES)+1))
    results = {}
    for combination in powerset:
        repairs = []
        for approach in combination:
            for other in data:
                if approach == other.approach:
                    repairs.append(set(other.repairs))
        #repairs enthält alle repairs der approaches durhc intersection nur noch die gemeinsamen repairs dabei
        results[combination] = set.intersection(*repairs)

    for k,v in results.items():
        print(k,len(v))

#common repairs for venn diagrammm also exklusive schnittmengen
def common_repairs_venn(repair_data: List[ApproachRepairData], question: int = 0, filter: bool = False) -> Dict[str, Set[Tuple[int, int]]]:
    """
    returns: Dict[str, Set[Tuple[int,int]]] 
    the string is a the name of the approach 
    the tuples are the corresponding repairs 
    first int id
    second int question of id
    """
    
    data = {}
    #convert data to a dict of set of tuples, every tuple represents a repair
    for approach in repair_data:
        if filter:
            data[approach.approach_name] = set([(repair.question, repair.id) for repair in approach.repairs if repair.question == question])
        else:
            data[approach.approach_name] = set([(repair.question, repair.id) for repair in approach.repairs])

    powerset = chain.from_iterable(combinations(APPROACHES, r) for r in range(1, len(APPROACHES)+1))
    results = {}
    for combination in powerset:
        intersect = set.intersection(*(data[approach] for approach in combination))
        #größere schnittmengen abziehen
        larger_combinations = chain.from_iterable(combinations(APPROACHES, r) for r in range(len(combination), len(APPROACHES)+1))
        for larger_comb in larger_combinations:
            if set(combination).issubset(set(larger_comb)) and set(combination) != set(larger_comb):
                intersect_bigger_comb = set.intersection(*(data[approach] for approach in larger_comb))
                intersect -= intersect_bigger_comb

        results[combination] = tuple(sorted(intersect, key=lambda t: (t[0], t[1])))
    
    #no duplicates in der gesamten menge
    assert(sum([len(r) for r in results.values()]) == len(set.union(*(set(r) for r in results.values()))))
    assert(set([(rep.question, rep.id) for approach in repair_data for rep in approach.repairs]) == set.union(*(set(r) for r in results.values())))

    for k,v in results.items():
        print(k,len(v))

    with open(os.path.join(OUTPUT, "common_repairs"), "a") as f:
        for k,v in results.items():
            f.write(f"Approaches Combination {k}\n")
            f.write(f"Common Repairs found {len(v)}\n")
            f.write(f"{v}\n\n")

    return results

def calculate_time_to_fix_on_common_repairs(data: List[ApproachRepairData]) -> Dict[str, Tuple[float, float]]:
    """
    ich nehme nur die zeit für repairs die wirklich alle gefunden haben
    
    returns: Dict[str, Tuple[float, float]]
    str: approach name
    first float: mean for a fix on common repairs of a approach
    second float: std abweichung for a fix on common repairs of a approach
    """
    #erstmal average refining later
    common_repairs = common_repairs_venn(data)

    #tuples of repairs transforming to Repair Objects with the fastest time
    #erstmal ohne fastest time
    common_repairs_all_approaches = common_repairs[('PyCardumen', 'PyKali', 'PyGenProg', 'PyMutRepair')]
    
    approach_tmp = dict()
    for approach in APPROACHES:
        tmp = set()
        for common_repair in common_repairs_all_approaches:
            question, id = common_repair
            for repair_data in data:
                if repair_data.approach_name == approach:
                    for repair in repair_data.repairs:
                        if repair.approach == approach and repair.question == question and repair.id == id:
                            tmp.add(repair)
                            break
        approach_tmp[approach] = tmp
    
    results = {}
    for approach in approach_tmp:
        repairs = approach_tmp[approach]
        times = [repair.time for repair in repairs]
        time_mean = numpy.mean(times)
        time_std = numpy.std(times)
        results[approach] = (time_mean, time_std)
    
    return results

import io
import pytest

def run_all_tests(test_dir):
    # Capture pytest output
    output = io.StringIO()
    sys.stdout = output
    #sys.stderr = output

    # Run pytest
    result = subprocess.run(
            ["pytest", test_dir, "--capture=no"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    

    # Restore stdout and stderr
    sys.stdout = sys.__stdout__
    #sys.stderr = sys.__stderr__

    # Print captured output
    #print(output.getvalue())

    # Return the exit code
    return result.returncode

def find_already_working_subjects(data: List[ApproachRepairData]) -> Set[Tuple[int, int]]:
    #ich vermute das einige subjects schon funktionieren bevor sie repariert werden
    common_repairs = common_repairs_venn(data)
    common_repairs_all_approaches = common_repairs[('PyCardumen', 'PyKali', 'PyGenProg', 'PyMutRepair')]
    already_working = set()
    for repair in common_repairs_all_approaches:
        question, id = repair
        path = Path(__file__).parent
        id = str(id).zfill(3)
        path = os.path.join(path, f"refactory_benchmark" ,f"question_{question}", f"{id}")
        exit_code = run_all_tests(path)
        if exit_code == 0:
            already_working.add(repair)
    return already_working



def plot_common_fixes_times(data: List[ApproachRepairData], question: int = 0, filter: bool = False):
    #TODO: filter für questions momentan einfach alle

    #erstmal average refining later
    common_repairs = common_repairs_venn(data)

    #tuples of repairs transforming to Repair Objects with the fastest time
    #erstmal ohne fastest time
    common_repairs_all_approaches = common_repairs[('PyCardumen', 'PyKali', 'PyGenProg', 'PyMutRepair')]

    #TODO: hier nochmal alle reinnehmen egal welcher seed es gefunden hat dann natürlich unterschiedlich viele werte für jeden approach aber egal
    #TODO: später dann noch auch alle repairs mit reinnehmen welche auch nicht von allen gefunden wurde aber min. immer 2 also aller außer die uniques
    
    #collecting repairs 
    approach_tmp = dict()
    for approach in APPROACHES:
        tmp = set()
        for common_repair in common_repairs_all_approaches:
            question, id = common_repair
            for repair_data in data:
                if repair_data.approach_name == approach:
                    for repair in repair_data.repairs:
                        if repair.approach == approach and repair.question == question and repair.id == id:
                            tmp.add(repair)
                            break
        approach_tmp[approach] = tmp
    
    #collecting times
    #TODO: besseren namen für data
    data = dict()
    for approach in approach_tmp:
        approach_times = set()
        for repair in approach_tmp[approach]:
            repair: Repair
            approach_times.add(repair.time)
        data[approach] = approach_times
    
    # Daten für den Boxplot vorbereiten
    approaches = list(data.keys())
    measurements = [list(times) for times in data.values()]

    # Boxplot erstellen
    plt.figure(figsize=(8, 6))
    plt.boxplot(measurements, tick_labels=approaches, patch_artist=True, boxprops=dict(facecolor="lightblue"))

    # Diagramm verschönern
    plt.title("Comparing times for common fixes", fontsize=14)
    plt.ylabel("Time in seconds", fontsize=12)
    plt.xlabel("Approaches", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Diagramm anzeigen
    plt.tight_layout()
    if filter:
        plt.savefig(os.path.join(Path(__file__).parent , f"time_common_fixes_question_{question}.pdf"))
    else:
        plt.savefig(os.path.join(Path(__file__).parent , f"time_common_fixes.pdf"))

def filter_out_already_working_subjects(data: List[ApproachRepairData]) -> List[ApproachRepairData]:
    already_working = find_already_working_subjects(data)
    for approach in data:
        approach.repairs = [
            repair for repair in approach.repairs
            if not any(
                repair.question == question and repair.id == id
                for question, id in already_working
            )
        ]
    #assert??? das sie nciht mehr drinnen sind
    return data

#TODO: repair data sollte ein dict sein mit key approach
def main(args):
    #Subject Data
    subject_data = create_subject_data(RESULTS)
    repair_data = create_repair_data(subject_data)
    print("Before filtering: ")
    plot_common_fixes_times(repair_data)
    filtered_repair_data = filter_out_already_working_subjects(repair_data)
    print("After filtering: ")
    plot_common_fixes_times(filtered_repair_data)
    #uniques = find_unique_repairs(repair_data)
    #common_repairs = common_repairs_venn(repair_data)
    #times = calculate_time_to_fix_on_common_repairs(repair_data)
    #total_repairs = count_total_repairs(repair_data)



    #corrupted_data = find_corrupted_data(RESULTS)
    #with open("eval/corrupted_data.json", "w") as f:
        #json.dump(corrupted_data, f)

    #with open("eval/corrupted_data.json") as f:
            #data = json.load(f)
            #data = [entry for entry in data if entry[2] != "TimeoutException" and entry[2] != "TimeoutExpired"]
            #am anfang 295
            #print(len(data))

    #uncomplete_data = find_uncomplete_data(RESULTS)
    #with open("eval/uncomplete_data.json", "w") as f:
        #json.dump(uncomplete_data, f)



if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
