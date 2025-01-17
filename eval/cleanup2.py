import os
import re

def process_line(line, question_number):
    # Fügt die Frage-Nummer an der zweiten Stelle hinzu
    parts = line.strip().split(',')
    if len(parts) > 0:
        parts.insert(1, question_number)  # Frage-Nummer einfügen
    return ','.join(parts) + '\n'

def process_files_with_question_number():
    # Der feste Pfad, in dem die Dateien liegen
    folder_path = "/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results_fitness/"
    
    # Suche nach Dateien, die dem Muster entsprechen
    files = os.listdir(folder_path)
    
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        
        # Frage-Nummer aus dem Dateinamen extrahieren
        match = re.search(r'question_(\d+)', filename)
        if match:
            question_number = match.group(1)  # Die Nummer hinter "question_"
            
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                
                # Jede Zeile verarbeiten und die Frage-Nummer hinzufügen
                processed_lines = [process_line(line, question_number) for line in lines]
                
                # Änderungen in der Datei speichern
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.writelines(processed_lines)
                print(f"Datei {filename} wurde erfolgreich bearbeitet.")
            else:
                print(f"Datei {filename} wurde nicht gefunden!")
        else:
            print(f"Keine gültige Frage-Nummer in {filename} gefunden!")

# Skript ausführen
process_files_with_question_number()
