import glob
import csv
import os
import pandas as pd

def find_most_recent_csv_file(pattern: str):
    print(f"Recherche du fichier CSV correspondant au motif '{pattern}'...")
    matching_files = glob.glob(pattern)
    if not matching_files:
        return None
    most_recent_file = max(matching_files, key=os.path.getmtime)
    return most_recent_file

def find_csv_delimiter(file_path: str, sample_size: int = 1024, encoding: str = 'latin1'):
    print(f"Détection du délimiteur pour le fichier '{file_path}'...")
    try:
        with open(file_path, 'r', encoding=encoding) as csvfile:
            sample = csvfile.read(sample_size)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
    except Exception as e:
        print(f"Erreur lors de la détection du délimiteur : {e}")
        return None
    print(f"Délimiteur détecté: '{delimiter}'")
    return delimiter

def read_csv_with_delimiter(file_path: str, delimiter: str, encoding: str = 'latin1', low_memory: bool = False):
    print(f"Lecture du fichier CSV '{file_path}' avec le délimiteur '{delimiter}'...")
    try:
        return pd.read_csv(file_path, sep=delimiter, encoding=encoding, low_memory=low_memory)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier CSV : {e}")
        return None

def merge_dataframes(df_list, merge_keys, merge_how='left'):
    if not df_list:
        print("Aucun DataFrame à fusionner.")
        return None
    if len(df_list) == 1:
        print("Un seul DataFrame présent, pas besoin de fusion.")
        return df_list[0]

    print("Fusion des DataFrames...")
    merged_data = df_list[0]
    for i in range(1, len(df_list)):
        print(f"Fusion des DataFrames {i} et {i+1} sur la clé {merge_keys[i-1]}...")
        merged_data = pd.merge(merged_data, df_list[i], how=merge_how, on=merge_keys[i-1])
    print("Fusion terminée.")
    return merged_data