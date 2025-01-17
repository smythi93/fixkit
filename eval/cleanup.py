import os

def process_line(line):
    # Entfernen der gewünschten Textteile und Umformatieren der Zeile
    line = line.replace("Found: ", "").replace("Fitness: ", "").replace("Duration: ", "").replace(" s", "").replace(" ", "").replace("Generations:", "").replace("Seed:", "")
    return line

def process_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Nur Dateien verarbeiten, keine Ordner
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Verarbeitete Zeilen speichern
            processed_lines = [process_line(line) for line in lines]
            
            # Änderungen in der Datei speichern
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(processed_lines)

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
                # Verarbeitete Zeilen speichern
                processed_lines = [process_line(line) for line in lines]
                
                # Änderungen in der Datei speichern
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.writelines(processed_lines)

# Pfad zum Ordner angeben
#folder_path = "/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results"
#process_files_in_folder(folder_path)
file = "/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results_reruns/PyMutRepair_rerun_repairs.txt"
process_file(file)
