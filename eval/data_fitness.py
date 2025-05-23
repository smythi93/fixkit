import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def new_load_csv_files(folder_path):
    dataframes = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path, header=0, 
                             names=["approach_name", "seed", "question", "subject_number", "found",
                                     "max_fit_gen_1", "max_fit_gen_2", "max_fit_gen_3", "max_fit_gen_4", 
                                     "max_fit_gen_5", "max_fit_gen_6", "max_fit_gen_7", "max_fit_gen_8", 
                                     "max_fit_gen_9", "max_fit_gen_10", "avrg_fit_gen_1", "avrg_fit_gen_2", 
                                     "avrg_fit_gen_3", "avrg_fit_gen_4", "avrg_fit_gen_5", "avrg_fit_gen_6", 
                                     "avrg_fit_gen_7", "avrg_fit_gen_8", "avrg_fit_gen_9", "avrg_fit_gen_10", 
                                     "count_of_gens", "duration" ])
            dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

def old_load_csv_files(folder_path):
    dataframes = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path, header=0, 
                             names=["approach_name", "seed", "question", "subject_number", "found",
                                     "fit_gen_1", "fit_gen_2", "fit_gen_3", "fit_gen_4", 
                                     "fit_gen_5", "fit_gen_6", "fit_gen_7", "fit_gen_8", 
                                     "fit_gen_9", "fit_gen_10",
                                     "count_of_gens", "duration" ])
            dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

def find_already_working(df: pd.DataFrame):
    filtered_df = df[(df['count_of_gens'] == 0)]
    
    return filtered_df

def remove_rows_based_on_dataframe(df, remove_df):
    # Extrahiere die Paare aus dem DataFrame `remove_df`
    pairs_to_remove = set(zip(remove_df['question'], remove_df['subject_number']))

    # Filtere den DataFrame
    filtered_df = df[~df.apply(lambda row: (row['question'], row['subject_number']) in pairs_to_remove, axis=1)]

    return filtered_df

def mean_and_shit(df: pd.DataFrame):
    mean_count_of_gen = df['count_of_gen'].mean()
    median_count_of_gen = df['count_of_gen'].median()
    print(f"Mean: {mean_count_of_gen}")
    print(f"Median: {median_count_of_gen}")

def generation_found_patches(combined_df):
    # Absolute Häufigkeiten berechnen
    value_counts = combined_df['count_of_gens'].value_counts().sort_index()
    colors = {
    "PyKali": (240/255, 135/255, 5/255),
    "PyGenProg": (115/255, 108/255, 168/255),
    "PyCardumen": (22/255, 153/255, 211/255),
    "PyMutRepair": (232/255, 86/255, 66/255)
}
    # Balkendiagramm erstellen
    plt.bar(value_counts.index, value_counts.values, color=colors["PyCardumen"], edgecolor=colors["PyCardumen"], alpha=0.8)

    # Titel und Achsenbeschriftungen
    plt.xlabel('Generation')
    plt.ylabel('Patches')

    # X-Achse exakt beschriften
    plt.xticks(value_counts.index)

    # Plot als PDF speichern
    plt.savefig('generation_found_patches.pdf', format='pdf', bbox_inches='tight')

    plt.tight_layout()

    # Plot schließen
    plt.close("all")

def line_plot_both_in_one(df, repair_df, filename):

    # Wähle nur die relevanten Spalten (fit_gen_1 bis fit_gen_10)
    fit_columns = [f'fit_gen_{i}' for i in range(1, 11)]

    # Erstelle das Diagramm
    plt.figure(figsize=(10, 6))
    for index, row in df.head(10).iterrows():
        print(row)
        plt.plot(fit_columns, row[fit_columns], label=f'NoPa {index}', alpha=0.6)

    for index, row in repair_df.head(10).iterrows():
        print(row)
        plt.plot(fit_columns, row[fit_columns], label=f'Patch {index}', alpha=0.6)
    

    plt.xlabel('Generations')
    plt.ylabel('Fitness')
    plt.title('The fitness of the most fit candidate across generations')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
    plt.grid(True)
    plt.savefig(filename, format="pdf")
    plt.close("all")

def line_plot_both_seperate(df, repair_df, filename):
    # Wähle nur die relevanten Spalten (fit_gen_1 bis fit_gen_10)
    fit_columns = [f'fit_gen_{i}' for i in range(1, 11)]

    # Erstelle ein Plot-Fenster mit 2 Subplots nebeneinander
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    # Plot für df
    counter = 1
    for index, row in df.head(10).iterrows():
        axes[0].plot(fit_columns, row[fit_columns], label=f'NoPa {counter}', alpha=0.6)
        counter += 1

    axes[0].set_xlabel('Generations')
    axes[0].set_ylabel('Fitness')
    axes[0].set_title('Fitness of candidates without successful patch')
    axes[0].legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
    axes[0].grid(True)

    # Setze benutzerdefinierte x-Ticks (gen_1 bis gen_10)
    axes[0].set_xticks(fit_columns)
    axes[0].set_xticklabels([f'{i}' for i in range(1, 11)])

    # Plot für repair_df
    counter = 1
    for index, row in repair_df.head(10).iterrows():
        axes[1].plot(fit_columns, row[fit_columns], label=f'Patch {counter}', alpha=0.6)
        counter += 1

    axes[1].set_xlabel('Generations')
    axes[1].set_ylabel('Fitness')
    axes[1].set_title('Fitness of candidates with successful patch')
    axes[1].legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
    axes[1].grid(True)

    # Setze benutzerdefinierte x-Ticks (gen_1 bis gen_10) für den zweiten Plot
    axes[1].set_xticks(fit_columns)
    axes[1].set_xticklabels([f'{i}' for i in range(1, 11)])

    # Optimierung der Layout-Anpassung, um Überlappung zu vermeiden
    plt.tight_layout()
    plt.savefig(filename, format="pdf")
    plt.close("all")

def line_plot_all_subjects(df, filename1):
    # Wähle nur die relevanten Spalten (fit_gen_1 bis fit_gen_10)
    fit_columns = [f'fit_gen_{i}' for i in range(1, 11)]

    # Erstes Diagramm für df
    plt.figure(figsize=(10, 6))
    counter = 1
    for index, row in df.head(10).iterrows():
        plt.plot(fit_columns, row[fit_columns], label=f'NoPa {counter}', alpha=0.6, linewidth=3)
        counter += 1

    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title('Fitness of candidates without successful patch')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
    plt.grid(True)
    plt.xticks(fit_columns, [f'{i}' for i in range(1, 11)])
    plt.tight_layout()
    plt.savefig(filename1, format="pdf")
    plt.close()

def line_plot_repairs_only(repair_df, filename2):
    # Wähle nur die relevanten Spalten (fit_gen_1 bis fit_gen_10)
    fit_columns = [f'fit_gen_{i}' for i in range(1, 11)]

    # Zweites Diagramm für repair_df
    plt.figure(figsize=(10, 6))
    counter = 1
    for index, row in repair_df.head(10).iterrows():
        plt.plot(fit_columns, row[fit_columns], label=f'Patch {counter}', alpha=0.6, linewidth=3)
        counter += 1

    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title('Fitness of candidates with successful patch')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
    plt.grid(True)
    plt.xticks(fit_columns, [f'{i}' for i in range(1, 11)])
    plt.tight_layout()
    plt.savefig(filename2, format="pdf")
    plt.close()

def count_unique_max_fit_values(df):
    max_fit_columns = [f"fit_gen_{i}" for i in range(1, 11)]
    unique_counts = df[max_fit_columns].apply(lambda row: row.nunique(), axis=1)
    return unique_counts


def plot_unique_counts_bar_charts(df1, df2, filename):
    df1['unique_max_fit_count'] = count_unique_max_fit_values(df1)
    df2['unique_max_fit_count'] = count_unique_max_fit_values(df2)

    print(df1["unique_max_fit_count"].value_counts().sort_index())
    colors = {
    "PyKali": (240/255, 135/255, 5/255),
    "PyGenProg": (115/255, 108/255, 168/255),
    "PyCardumen": (22/255, 153/255, 211/255),
    "PyMutRepair": (232/255, 86/255, 66/255)
}
    # Erstelle eine Figur mit zwei Subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=False)

    # Erstes Diagramm
    df1['unique_max_fit_count'].value_counts().sort_index().plot(
        kind='bar', color=colors["PyCardumen"], edgecolor=colors["PyCardumen"], ax=axes[0]
    )
    axes[0].set_title('All Subjects')
    axes[0].set_xlabel('Number of different maximal fitness values')
    axes[0].set_ylabel('Quantity')
    axes[0].grid(axis='y', linestyle='--', alpha=0.7)
    axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=0)

    # Zweites Diagramm
    counts = df2['unique_max_fit_count'].value_counts().sort_index()

    # Schritt 2: Wenn 0 und 1 existieren, füge die Häufigkeit von 0 zu 1 hinzu
    #counts[2] += counts[1]

    # Schritt 3: Setze die Häufigkeit von 0 auf 0
    #counts[1] = 0

    # Plotten
    counts.plot(
        kind='bar', 
        color=colors["PyMutRepair"], 
        edgecolor=colors["PyMutRepair"], 
        ax=axes[1]
    )
    axes[1].set_title('Repairs only')
    axes[1].set_xlabel('Number of different maximal fitness values')
    axes[1].grid(axis='y', linestyle='--', alpha=0.7)
    axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=0)

    plt.xticks()
    plt.tight_layout()
    plt.savefig(filename, format="pdf")
    plt.close("all")


old_folder_path = "/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results_fitness"
new_folder_path = "/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results_fitness_2"

old_df = old_load_csv_files(old_folder_path)
new_df = new_load_csv_files(new_folder_path)
df = old_df

to_remove = find_already_working(df)

filtered_df = remove_rows_based_on_dataframe(df, to_remove)

filtered_df = filtered_df[filtered_df['found'].isin(['True', 'False', True, False])]
filtered_df['found'] = filtered_df['found'].map(lambda x: True if x in ['True', True] else False)

repairs_df = filtered_df[filtered_df["found"] == True]
#ab hier kann ich mit dem filtered_df arbeiten das hat die 59 bzw 590 subjects entfernt


filtered_df = filtered_df[filtered_df["seed"] == 0]
repairs_df = filtered_df[filtered_df["found"] == True]
#line_plot_both_in_one(filtered_df, repairs_df, "max_fitness_line_plot_both_in_one.pdf")
#line_plot_both_seperate(filtered_df, repairs_df, "max_fitness_line_plot_both_seperate.pdf")
line_plot_all_subjects(filtered_df, "line_plot_max_fitness_all_subjects.pdf")
line_plot_repairs_only(repairs_df, "line_plot_max_fitness_repairs_only.pdf")


#plot_unique_counts_bar_charts(filtered_df, repairs_df, "barchart_changes_in_fitness.pdf")
#generation_found_patches(repairs_df)
#mean_and_shit(filtered_df_fixes)

#line_pdf(filtered_df, "max", "max_fitness_line_plot.pdf")
#line_pdf(filtered_df, "max", "max_fitness_line_plot_fixes_only.pdf", True)
#line_pdf(filtered_df, "avrg", "avrg_fitness_line_plot.pdf")
#line_pdf(filtered_df, "avrg", "avrg_fitness_line_plot_fixes_only.pdf", True)





