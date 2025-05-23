import os

import pandas as pd
import scipy.stats as stats
import numpy as np
import scikit_posthocs as sp
from scipy.stats import mannwhitneyu

from pathlib import Path
from typing import List, Dict

import seaborn as sns
import matplotlib.pyplot as plt

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

def test_runtime_ttf_eines_approaches(runtime, time_to_fix):
    u_stat, p_value = mannwhitneyu(runtime, time_to_fix, alternative='two-sided')
    print(f"Mann-Whitney-U p-Wert: {p_value}, u-stat: {u_stat}")



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

def print_top_10_lowest_durations(df, column, group_by_col):
    # Sortiere pro 'approach_name' und gebe die 10 niedrigsten Werte aus
    for approach, group in df.groupby(group_by_col):
        top_10 = group.nsmallest(10, column)  # 10 kleinste Werte
        print(f"Top 10 geringste Laufzeiten für Ansatz: {approach}")
        print(top_10[['approach_name', 'question', 'subject_number', "seed", column]])
        print("-" * 50)

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
def test_shapiro(durations: List, name) -> float:
    sw_stat, sw_p = stats.shapiro(durations)
    if sw_p > 0.05:
        print(f"Die Daten von {name} sind normalverteilt. stats={sw_stat} + p={sw_p}")
    else:
        print(f"Die Daten von {name} sind NICHT normalverteilt. stats={sw_stat} + p={sw_p}")

    return sw_p

#test normalverteilung
def test_ks(durations: List, name) -> float:
    mean, std = np.mean(durations), np.std(durations, ddof=1)
    ks_stat, ks_p = stats.kstest(durations, "norm", args=(mean, std))
    if ks_p > 0.05:
        print(f"Die Daten von {name} sind normalverteilt. stats={ks_stat} + p={ks_p}")
    else:
        print(f"Die Daten von {name} sind NICHT normalverteilt. stats={ks_stat} + p={ks_p}")

    return ks_p

# Kruskal-Wallis-Test Signifikanz Test bei keiner Normalverteilung
def kruskal_wallis_test(df: Dict) -> float:
    h_stat, p_value = stats.kruskal(df['PyGenProg'], df['PyCardumen'], df['PyKali'], df['PyMutRepair'])
    print(f"Kruskal-Wallis-Statistik: {h_stat}, p-Wert: {p_value}")
    if p_value < 0.05:
        print("Die Mittelwerte der Gruppen sind signifikant unterschiedlich (H0 ablehnen).")
    else:
        print("Die Mittelwerte der Gruppen sind nicht signifikant unterschiedlich (H0 beibehalten).")
    
    return p_value

def posthoc_dunn_test(gen_dur: List, car_dur: List, kali_dur: List, mutrepair_dur: List):
    data = gen_dur + car_dur + kali_dur + mutrepair_dur
    groups = ['PyGenProg']*len(gen_dur) + ['PyCardumen']*len(car_dur) + ['PyKali']*len(kali_dur) + ['PyMutRepair']*len(mutrepair_dur)
    df = pd.DataFrame({'values': data, 'groups': groups})

    posthoc_dunn = sp.posthoc_dunn(df, val_col='values', group_col='groups', p_adjust='bonferroni')
    print(posthoc_dunn)

def test_significance(filtered_df: pd.DataFrame, only_time_to_fix = False):
    if only_time_to_fix:
        filtered_df = filtered_df[(filtered_df['found'] == True)]
        print("Testing Time To Fix")
    else:
        print("Testing Runtime")

    grouped = filtered_df.groupby('approach_name')['duration'].apply(list)

    #TODO: move only exhaustive logic to subroutines

    genprog_dur = grouped["PyGenProg"]
    cardumen_dur = grouped["PyCardumen"]
    kali_dur = grouped["PyKali"]
    mutrepair_dur = grouped["PyMutRepair"]

    #Test Normalverteilung
    print("Test KS: ")
    test_ks(genprog_dur, "PyGenProg")
    test_ks(cardumen_dur, "PyCardumen")
    test_ks(kali_dur, "PyKali")
    test_ks(mutrepair_dur, "PyMutRepair")
    print()

    print("Test Shapiro:")
    test_shapiro(genprog_dur, "PyGenProg")
    test_shapiro(cardumen_dur, "PyCardumen")
    test_shapiro(kali_dur, "PyKali")
    test_shapiro(mutrepair_dur, "PyMutRepair")
    print()

    #Test Signifikanter Unterschied bei keiner Normalverteilung
    kruskal_wallis_test(grouped)

    #Posthoc_Dunn Test welche der Gruppen sich unterscheiden
    posthoc_dunn_test(genprog_dur, cardumen_dur, kali_dur, mutrepair_dur)
    print()


def plot_that_shit(df, file_name, approach_order):
    # Manuell festgelegte Reihenfolge der Approaches
    #approach_order = ['PyGenProg', "PyCardumen", 'PyKali', 'PyMutRepair']

    # Anzahl der Einträge pro Approach berechnen (feste Reihenfolge beibehalten)
    approach_counts = df.groupby('approach_name').size().reindex(approach_order)

    # Boxplot erstellen mit definierter Reihenfolge
    plt.figure(figsize=(8, 6))

    colors = {
    "PyKali": (240/255, 135/255, 5/255),
    "PyGenProg": (115/255, 108/255, 168/255),
    "PyCardumen": (22/255, 153/255, 211/255),
    "PyMutRepair": (232/255, 86/255, 66/255)
}
    
    sns.boxplot(x="approach_name", y="duration", data=df, order=approach_order, palette=colors, fill=False)

    # Anzahl der Datenpunkte unter den Labels hinzufügen (feste Reihenfolge)
    xticklabels = [f"{approach}\n(n={approach_counts[approach]})" for approach in approach_order]
    plt.xticks(ticks=range(len(approach_order)), labels=xticklabels)

    # Diagramm anpassen
    plt.xlabel("Approach")
    plt.ylabel("Duration in seconds")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig(file_name, format="pdf")

def remove_upper_outliers_per_approach(df, column, group_by_col, factor=3.0):
    def filter_outliers(group):
        Q1 = group[column].quantile(0.25)
        Q3 = group[column].quantile(0.75)
        IQR = Q3 - Q1

        upper_bound = Q3 + factor * IQR  # Nur obere Grenze berücksichtigen

        return group[group[column] <= upper_bound]

    df_filtered = df.groupby(group_by_col, group_keys=False).apply(filter_outliers)
    return df_filtered

def remove_all_outliers_per_approach(df, column, group_by_col, factor=3.0):
    def filter_outliers(group):
        Q1 = group[column].quantile(0.25)
        Q3 = group[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - factor * IQR
        upper_bound = Q3 + factor * IQR

        # Filterung erfolgt auf der aktuellen Gruppe, nicht auf dem gesamten DataFrame
        return group[(group[column] >= lower_bound) & (group[column] <= upper_bound)]

    # Anwenden der Funktion auf jede Gruppe und Zusammenfügen der Ergebnisse
    df_filtered = df.groupby(group_by_col, group_keys=False).apply(filter_outliers)
    return df_filtered.reset_index(drop=True)

df_result_fitness = load_result_fitness_csv_files("/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results_fitness")

df_results = load_result_csv_files("/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results")
to_remove = find_already_working(df_result_fitness)

filtered_df = remove_rows_based_on_dataframe(df_results, to_remove)

filtered_df = filtered_df[filtered_df['found'].isin(['True', 'False', True, False])]
filtered_df['found'] = filtered_df['found'].map(lambda x: True if x in ['True', True] else False)
repairs_df = filtered_df[(filtered_df['found'] == True)]
#ab hier kann ich mit dem filtered_df arbeiten das hat die 590 subjects * 4 entfernt
#außerdem wurden alle fehlermeldungen entfernt
#AB HIER SCHÖNE CLEANE DATEN

#removed_outliers_df = remove_all_outliers_per_approach(filtered_df, 'duration', 'approach_name', factor=1.0)
#removed_outliers_repairs_df = remove_all_outliers_per_approach(repairs_df, 'duration', 'approach_name', factor=1.0)


## PLOTTING THE RUNTIMES AND TIME TO FIX
approach_order_all = ['PyGenProg', "PyCardumen", 'PyKali', 'PyMutRepair']
approach_order_without_cardumen = ['PyGenProg', 'PyKali', 'PyMutRepair']
#plot_that_shit(removed_outliers_df, "runtime_removed_all_outliers.pdf", approach_order_all)
#plot_that_shit(removed_outliers_df, "runtime_removed_all_outliers_without_cardumen.pdf", approach_order_without_cardumen)
#plot_that_shit(removed_outliers_repairs_df, "time_to_fix_removed_all_outliers_without_cardumen.pdf", approach_order_without_cardumen)
#plot_that_shit(removed_outliers_repairs_df, "time_to_fix_removed_all_outliers.pdf", approach_order_all)
#plot_that_shit(filtered_df, "runtime_boxplot.pdf", approach_order_all)
#plot_that_shit(repairs_df, "time_to_fix.boxplot.pdf", approach_order_all)
## COMPARING RUNTIME UND TTF EINES APPROACHES
only_exhaustive_df = filtered_df[(filtered_df["approach_name"] == "PyKali") | (filtered_df["approach_name"] == "PyMutRepair")]
only_evolutionary_df = filtered_df[(filtered_df["approach_name"] == "PyGenProg") | (filtered_df["approach_name"] == "PyCardumen")]

grouped = filtered_df.groupby('approach_name')['duration'].apply(list)
grouped_repairs = repairs_df.groupby('approach_name')['duration'].apply(list)

genprog_dur_rep = grouped_repairs["PyGenProg"]
cardumen_dur_rep = grouped_repairs["PyCardumen"]
kali_dur_rep = grouped_repairs["PyKali"]
mutrepair_dur_rep = grouped_repairs["PyMutRepair"]

genprog_dur = grouped["PyGenProg"]
cardumen_dur = grouped["PyCardumen"]
kali_dur = grouped["PyKali"]
mutrepair_dur = grouped["PyMutRepair"]


#test_runtime_ttf_eines_approaches(genprog_dur, genprog_dur_rep)
#test_runtime_ttf_eines_approaches(cardumen_dur, cardumen_dur_rep)
#test_runtime_ttf_eines_approaches(kali_dur, kali_dur_rep)
#test_runtime_ttf_eines_approaches(mutrepair_dur, mutrepair_dur_rep)

## TESTING OB SIGNIGIKANTER UNTERSCHIED ZWISCHEN APPROACHES
#test_significance(filtered_df)
test_significance(filtered_df, True)

#APPROACHES = ["PyGenProg", "PyCardumen", "PyMutRepair", "PyKali"]
#for approach in APPROACHES:
#    calculate_mean_median(filtered_df, approach)
#    calculate_mean_median_on_fixes(filtered_df, approach)

#for approach in APPROACHES:
#    mean_and_shit(filtered_df, approach)