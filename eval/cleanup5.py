import os
import csv
import re

def add_seed_to_csv(folder_path, name_prefix):
    # Gehe alle Dateien im Ordner durch
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Überprüfe, ob die Datei dem Schema "name_all_seed" entspricht (z. B. PyCardumen_all_123)
        if os.path.isfile(file_path) and re.match(rf"{re.escape(name_prefix)}_all_(\d+)\.csv", filename):
            # Seed aus dem Dateinamen extrahieren
            match = re.search(rf'{re.escape(name_prefix)}_all_(\d+)\.csv', filename)
            if match:
                seed = match.group(1)  # Der extrahierte Seed aus dem Dateinamen
                
                # Datei öffnen und Zeilen verarbeiten
                with open(file_path, mode='r', encoding='utf-8') as infile:
                    reader = csv.reader(infile)
                    rows = list(reader)

                # Zeilen bearbeiten und Seed an die zweite Stelle verschieben
                for i, row in enumerate(rows):
                    if len(row) >= 1:
                        # Füge den Seed an die zweite Stelle
                        row.insert(1, seed)
                
                # Datei mit den bearbeiteten Zeilen überschreiben
                with open(file_path, mode='w', encoding='utf-8', newline='') as outfile:
                    writer = csv.writer(outfile)
                    writer.writerows(rows)

                print(f"Seed {seed} wurde in Datei {filename} an die zweite Stelle eingefügt.")
            else:
                print(f"Kein gültiger Seed in Dateinamen {filename} gefunden.")
        else:
            print(f"Datei {filename} entspricht nicht dem Muster.")

# Skript ausführen
folder_path = "/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results_fitness/"  # Ordner mit den CSV-Dateien
name_prefix = "PyGenProg"  # Prefix der Dateien (z. B. "PyCardumen")
add_seed_to_csv(folder_path, name_prefix)
