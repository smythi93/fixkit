from pathlib import Path
from typing import List
import matplotlib
import matplotlib.pyplot as plt
import os
QUESTION_1 = Path(__file__).parent / "results" / "question_1"
QUESTION_2 = Path(__file__).parent / "results" / "question_2"
QUESTION_3 = Path(__file__).parent / "results" / "question_3"
QUESTION_4 = Path(__file__).parent / "results" / "question_4"
QUESTION_5 = Path(__file__).parent / "results" / "question_5"

inputs = [QUESTION_1]

def get_data(path_to_file: Path)-> List[List[str]]:
        with open(path_to_file) as f:
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

def first_scatter():
    file = "PyGenProg_question_1.txt"
    #data of 1 approach
    data = get_data(QUESTION_1 / file)
    print(data[0])
    print(data[0][3])
    # Extract fitness and duration
    #matplotlib.use("TkAgg")
    subject = [float(entry[1]) for entry in data if len(entry) == 5]
    fitness = [float(entry[3]) for entry in data if len(entry) >= 5]
    duration = [float(entry[4])  for entry in data if len(entry) >= 5]
    found_repair = [entry[2].strip() for entry in data if len(entry) >= 5]
    print(found_repair)

    # Create a scatter plot
    plt.scatter(subject, fitness, c=['green' if found == "True" else 'red' for found in found_repair])
    plt.xlabel('subjects')
    plt.ylabel('Fitness')
    plt.title('Fitness vs Subjects')

    # Add a legend
    plt.scatter([], [], c='green', label='Repair Found')
    plt.scatter([], [], c='red', label='Repair Not Found')
    plt.legend()

    plt.show()

def reps_question():
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
                    repairs.append(id)
            counts[file] = repairs
        approaches = counts.keys()
        repairs = counts.values()
        plt.bar(approaches, [len(count) for count in repairs],)
        plt.xlabel("Approaches")
        plt.ylabel("Repairs Found")
        plt.show()

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
    files = os.listdir(QUESTION_1)

    #reps_question()
    unique_fixes()
    plot_unique_fixes()





if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
