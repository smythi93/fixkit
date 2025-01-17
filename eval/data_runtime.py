import os

import pandas as pd
import scipy.stats as stats
import numpy as np
import scikit_posthocs as sp

from pathlib import Path

def load_result_fitness_csv_files(folder_path):
    dataframes = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path, header=0, 
                             names=['approach_name', 'seed', 'question', 
                                    'subject_number', 'found',
                                    'fit_gen_1', 'fit_gen_2','fit_gen_3',
                                    'fit_gen_4','fit_gen_5','fit_gen_6',
                                    'fit_gen_7','fit_gen_8','fit_gen_9',
                                    'fit_gen_10', 'count_of_gen', 'duration'])
            dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

def load_result_csv_files(folder_path):
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

def find_already_working(df: pd.DataFrame):
    filtered_df = df[(df['count_of_gen'] == 0) & (df["seed"] == 1343)]
    
    return filtered_df

def remove_rows_based_on_dataframe(df, remove_df):
    # Extrahiere die Paare aus dem DataFrame `remove_df`
    pairs_to_remove = set(zip(remove_df['question'], remove_df['subject_number']))

    # Filtere den DataFrame
    filtered_df = df[~df.apply(lambda row: (row['question'], row['subject_number']) in pairs_to_remove, axis=1)]

    return filtered_df

def calculate_mean_median(df, name):
    filtered_df = df[(df['approach_name'] == name)]
    average_duration = filtered_df['duration'].mean()
    median_duration = filtered_df['duration'].median()
    print(f"Mittelwert von {name}: {average_duration:.1f}")
    print(f"Median von {name}: {median_duration:.1f}")
    
    
def calculate_mean_median_on_fixes(df, name):
    filtered_df = df[(df['approach_name'] == name) & df['found'] == True]
    average_duration = filtered_df['duration'].mean()
    median_duration = filtered_df['duration'].median()
    print(f"Mittelwert von {name} nur Fixes: {average_duration:.1f}")
    print(f"Median von {name} nur Fixes: {median_duration:.1f}")

def mean_and_shit(df: pd.DataFrame, name):
    print(approach)
    filtered_df = df[(df["approach_name"] == name)]
    stats = filtered_df['duration'].describe()

    print(stats)
    print("Variance: ")
    print(filtered_df['duration'].var())
    print("Median: ")
    print(filtered_df["duration"].median())
    
#test normalverteilung
def test_shapiro(df: pd.DataFrame, name) -> float:
    sw_stat, sw_p = stats.shapiro(df[name])
    if sw_p > 0.05:
        print(f"Die Daten von {name} sind normalverteilt. stats={sw_stat} + p={sw_p}")
    else:
        print(f"Die Daten von {name} sind NICHT normalverteilt. stats={sw_stat} + p={sw_p}")

    return sw_p

#test normalverteilung
def test_ks(df:pd.DataFrame, name) -> float:
    mean, std = df[name].mean(), df[name].std(ddof=1)
    ks_stat, ks_p = stats.kstest(df[name], "norm", args=(mean, std))
    if ks_p > 0.05:
        print(f"Die Daten von {name} sind normalverteilt. stats={ks_stat} + p={ks_p}")
    else:
        print(f"Die Daten von {name} sind NICHT normalverteilt. stats={ks_stat} + p={ks_p}")

    return ks_p

df_result_fitness = load_result_fitness_csv_files("/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results_fitness")
df_results = load_result_csv_files("/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results")
to_remove = find_already_working(df_result_fitness)

filtered_df = remove_rows_based_on_dataframe(df_results, to_remove)

filtered_df = filtered_df[filtered_df['found'].isin(['True', 'False', True, False])]
filtered_df['found'] = filtered_df['found'].map(lambda x: True if x in ['True', True] else False)

#ab hier kann ich mit dem filtered_df arbeiten das hat die 590 subjects * 4 entfernt
#außerdem wurden alle fehlermeldungen entfernt
#AB HIER SCHÖNE CLEANE DATEN

duration_df = filtered_df.pivot_table(
        columns='approach_name',  # Neue Spalten basierend auf 'approach_name'
        values='duration',        # Werte basierend auf 'duration'
        aggfunc='mean'            # Falls Duplikate existieren, nimm den Mittelwert
    )

print(duration_df)
#AB HIER DATEN WIE BEI REPAIR NUR STATT REPAIRS DURATIONS
APPROACHES = ["PyGenProg", "PyCardumen", "PyKali", "PyMutRepair"]

#for approach in APPROACHES:
#    calculate_mean_median(filtered_df, approach)
#    calculate_mean_median_on_fixes(filtered_df, approach)

#for approach in APPROACHES:
#    mean_and_shit(filtered_df, approach)