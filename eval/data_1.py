import os
import pandas as pd

def load_csv_files(folder_path):
    """
    Lädt alle CSV-Dateien aus einem Ordner und kombiniert sie in einem einzigen DataFrame.
    """
    dataframes = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path, header=0, 
                             names=['approach_name', 'seed', 'question', 
                                    'subject_number', 'found', 'fitness', 'duration'])
            dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

def analyze_reparaturen(df, approach_name, seed):
    """
    Analysiert die Anzahl der gefundenen Reparaturen für ein spezifisches Verfahren und Seed.
    """
    filtered_df = df[(df['approach_name'] == approach_name) & (df['seed'] == seed)]
    found_repairs = filtered_df[filtered_df['found'] == True].shape[0]
    print(f"Anzahl der Reparaturen für {approach_name} mit Seed {seed}: {found_repairs}")
    return found_repairs

def analyze_average_duration(df, approach_name):
    """
    Analysiert die durchschnittliche Fitness für ein spezifisches Verfahren und Frage.
    """
    filtered_df = df[(df['approach_name'] == approach_name)]
    # Sortieren nach 'duration' und Entfernen der schnellsten Zeiten
    #filtered_df = filtered_df.sort_values(by='duration', ascending=True).iloc[590:]
    average_duration = filtered_df['duration'].mean()
    print(f"Durchschnittliche Runtime für {approach_name}: {average_duration:.4f}")
    return average_duration

def analyze_average_duration_fix(df, approach_name):
    """
    Analysiert die durchschnittliche Fitness für ein spezifisches Verfahren und Frage.
    """
    filtered_df = df[(df['approach_name'] == approach_name) & (df['found'] == True) ]
    # Sortieren nach 'duration' und Entfernen der schnellsten Zeiten
    #filtered_df = filtered_df.sort_values(by='duration', ascending=True).iloc[590:]
    average_duration = filtered_df['duration'].mean()
    print(f"Durchschnittliche Runtime für {approach_name}: {average_duration:.4f}")
    return average_duration


def analyze_duration_by_seed(df, approach_name):
    """
    Analysiert die durchschnittliche Dauer für jedes Seed eines Ansatzes.
    """
    filtered_df = df[df['approach_name'] == approach_name]
    duration_by_seed = filtered_df.groupby('seed')['duration'].mean()
    print(f"Durchschnittliche Dauer pro Seed für {approach_name}:\n{duration_by_seed}")
    return duration_by_seed

def analyze_reps_kai():
    SEEDS = [8013,3798,5637,7770,6056,2419,6841,1343,6924,0]
    SEEDS.sort()
    APPROACHES = ["PyGenProg", "PyCardumen", "PyKali", "PyMutRepair"]
    # Analysen
    for seed in SEEDS:
        res = f"{seed}: "
        for approach in APPROACHES:
            reps = analyze_reparaturen(df, approach_name=approach, seed=seed)
            res += str(reps)
            res += " "
        print(res)

# Hauptskript
folder_path = "/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results/"  # Ordner mit den CSV-Dateien
df = load_csv_files(folder_path)

# Konvertiere 'found' zu Strings und bereinige Werte (strip für Leerzeichen)
df['found'] = df['found'].astype(str).str.strip().str.lower()

# Behalte nur Zeilen mit 'true' oder 'false'
df = df[df['found'].isin(['true', 'false'])]

# Konvertiere 'found' von String ('true', 'false') zu bool (True, False)
df['found'] = df['found'].map({'true': True, 'false': False})

#average fitness
analyze_average_duration(df, "PyCardumen")
analyze_average_duration_fix(df, "PyCardumen")


#analyze_average_fitness(df, approach_name="PyCardumen", question=1)
#analyze_duration_by_seed(df, approach_name="PyCardumen")
