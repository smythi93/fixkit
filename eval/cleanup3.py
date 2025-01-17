import os
import re

def merge_files_by_pattern(folder_path, name_prefix, seed, output_suffix="_all_"):
    # Erstellen des Ausgabe-Dateinamens
    output_filename = f"{name_prefix}{output_suffix}{str(seed)}.csv"
    output_path = os.path.join(folder_path, output_filename)

    # Finden aller relevanten Dateien, die dem Muster entsprechen
    files = [f for f in os.listdir(folder_path) if re.match(rf"{re.escape(name_prefix)}_question_\d+_{re.escape(str(seed))}", f)]
    
    # Dateien nach der Nummer in "question_X" sortieren
    files.sort(key=lambda x: int(re.search(r'question_(\d+)', x).group(1)))

    with open(output_path, 'w', encoding='utf-8') as output_file:
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as input_file:
                    data = input_file.read()
                    output_file.write(data)  # Daten in die neue Datei schreiben
                    output_file.write("\n")  # Zeilenumbruch für die Trennung
                print(f"Inhalte aus {file} wurden zusammengeführt.")
            else:
                print(f"Datei {file} wurde nicht gefunden.")
    
    print(f"Alle Daten wurden in {output_filename} gespeichert.")

# Skript ausführen
folder_path = "/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results_fitness/"
name_prefix = "PyGenProg"  # Der allgemeine Prefix (z. B. "PyCardumen")
SEEDS = [8013,3798,5637,7770,6056,2419,6841,1343,6924,0]
for seed in SEEDS:
	merge_files_by_pattern(folder_path, name_prefix, seed)
