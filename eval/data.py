from pathlib import Path
from typing import List, Dict
import re
import matplotlib
import matplotlib.pyplot as plt
import os
import json

QUESTION_1 = Path(__file__).parent / "results" / "question_1"
QUESTION_2 = Path(__file__).parent / "results" / "question_2"
QUESTION_3 = Path(__file__).parent / "results" / "question_3"
QUESTION_4 = Path(__file__).parent / "results" / "question_4"
QUESTION_5 = Path(__file__).parent / "results" / "question_5"
RESULTS = Path(__file__).parent / "results"
APPROACHES = ["PyCardumen", "PyKali", "PyGenProg", "PyMutRepair"]


inputs = [QUESTION_1]

class SubjectData:
    def __init__(self, file):
        self.seed: int = self.get_seed(file)
        self.question: int = self.get_question(file)
        self.approach: str = self.get_appraoch(file)
        self.data = self.get_data(file)
        #for debugging
        #print(self.approach, self.question, self.seed)
        self.subjects = [float(entry[1]) for entry in self.data if len(entry) == 5]
        self.fitness = [float(entry[3]) for entry in self.data if len(entry) >= 5]
        self.durations = [float(entry[4])  for entry in self.data if len(entry) >= 5]
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

    def get_data(self, file: Path) -> List[str]:
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

def create_data(result_path: str) -> List[SubjectData]:
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

#gives back the total repairs found for a question for a single approach
def found_repairs_question_approach(data: List[SubjectData], question: int, approach: str) -> Dict[int, int]:
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
    plt.savefig(os.path.join(Path(__file__).parent , f"found_repairs_question_{question}.jpg"))


#dont touch
def unique_fixes():
    for input in inputs:
        files = os.listdir(input)
        #File = Approach
        counts = {}
        for file in files:
            path_to_file = input / file
            data = get_data(path_to_file)
            subject = [int(entry[1]) for entry in data if len(entry) == 5]
            found_repair = [entry[2].strip() for entry in data if len(entry) == 5]
            repairs = []
            for id, entry in enumerate(found_repair):
                if entry == "True":
                    repairs.append(subject[id])
            counts[file] = repairs
        approaches = list(counts.keys())
        repairs = counts.values()
        for id, repair in enumerate(repairs):
            different_lists = []
            unique_repair = []
            not_unique_repair = []
            for id2, repair2 in enumerate(repairs):
                if id != id2:
                    different_lists.extend(repair2)
            for element in repair:
                if element in different_lists:
                    not_unique_repair.append(element)
                else:
                    unique_repair.append(element)
            approach = approaches[id]
            with open(QUESTION_1 / "unique_repairs.txt", "a") as f:
                f.write(f"{approach}\n")
                f.write(f"unique: {unique_repair}\n")
                f.write(f"not unique: {not_unique_repair}\n")

def plot_unique_fixes():
    for input in inputs:
        files = os.listdir(input)
        #File = Approach
        counts = {}
        for file in files:
            path_to_file = input / file
            data = get_data(path_to_file)
            subject = [int(entry[1]) for entry in data if len(entry) == 5]
            found_repair = [entry[2].strip() for entry in data if len(entry) == 5]
            repairs = []
            for id, entry in enumerate(found_repair):
                if entry == "True":
                    repairs.append(subject[id])
            counts[file] = repairs
        approaches = list(counts.keys())
        repairs = counts.values()
        plt.scatter(approaches, [repair for repair in repairs])
        plt.xlabel('subjects')
        plt.ylabel('approaches')
        plt.title('Fixes for Approach')

        # Add a legend
        plt.scatter([], [], c='green', label='Repair Found')
        plt.scatter([], [], c='red', label='Repair Not Found')
        plt.legend()

        plt.show()
        
def main(args):
    data = create_data(RESULTS)
    subject = data[1]
    #print(subject.question, subject.approach, subject.seed)
    
    #repairs = found_repairs_question(data, 1)
    #print(repairs)
    #plot_repairs_found(repairs, 1)
    corrupted_data = find_corrupted_data(RESULTS)
    with open("eval/corrupted_data.json", "w") as f:
        json.dump(corrupted_data, f)








if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
