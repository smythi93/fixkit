import os

def remove_empty_lines_and_validate(folder_path, target_line_count=1783):
    # Alle Dateien im Ordner durchgehen
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Nur Dateien verarbeiten, keine Unterordner
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Entferne leere Zeilen
            non_empty_lines = [line for line in lines if line.strip()]

            # Überprüfen, ob die gewünschte Zeilenanzahl erreicht wird
            if len(non_empty_lines) != target_line_count:
                print(f"Warnung: Datei {filename} hat nach dem Entfernen leerer Zeilen {len(non_empty_lines)} Zeilen (erwartet: {target_line_count}).")
            
            # Datei mit den bereinigten Zeilen überschreiben
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(non_empty_lines)

    print("Leere Zeilen wurden aus allen Dateien entfernt.")

# Skript ausführen
folder_path = "/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results_fitness/"  # Ordner mit den Dateien
remove_empty_lines_and_validate(folder_path)