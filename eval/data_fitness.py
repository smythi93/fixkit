import os
import pandas as pd

def load_csv_files(folder_path):
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

def find_already_working(df: pd.DataFrame):
    filtered_df = df[(df['count_of_gen'] == 0) & (df["seed"] == 1343)]
    
    return filtered_df

def remove_rows_based_on_dataframe(df, remove_df):
    # Extrahiere die Paare aus dem DataFrame `remove_df`
    pairs_to_remove = set(zip(remove_df['question'], remove_df['subject_number']))

    # Filtere den DataFrame
    filtered_df = df[~df.apply(lambda row: (row['question'], row['subject_number']) in pairs_to_remove, axis=1)]

    return filtered_df

folder_path = "/vol/fob-vol5/nebenf22/werkkai/dev/fixkit/eval/results_fitness"

df = load_csv_files(folder_path)

to_remove = find_already_working(df)

filtered_df = remove_rows_based_on_dataframe(df, to_remove)

#ab hier kann ich mit dem filtered_df arbeiten das hat die 59 bzw 590 subjects entfernt

