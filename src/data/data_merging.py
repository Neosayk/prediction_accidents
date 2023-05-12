import glob
import os
import csv
import pandas as pd


def upload_to_supabase(csv_file_path, chunk_size, supabase, table_name):
    print("Lecture du fichier CSV et préparation pour l'envoi à Supabase...")
    data_iterator = pd.read_csv(csv_file_path, chunksize=chunk_size, na_filter=False)
    row_count = 0
    for chunk in data_iterator:
        chunk_data = chunk.to_dict(orient='records')
        response = supabase.table(table_name).insert(chunk_data).execute()
        if response:
            print(f"{len(chunk_data)} lignes insérées avec succès dans la table '{table_name}'")
            row_count += len(chunk_data)
    print(f"{row_count} lignes insérées au total dans la table '{table_name}'")


def csv_to_dataframe(pattern: str, sample_size: int = 1024, encoding: str = 'latin1', low_memory: bool = False):
    print("Recherche du fichier CSV le plus récent correspondant au motif donné...")
    matching_files = glob.glob(pattern)
    if not matching_files:
        print("Aucun fichier correspondant trouvé.")
        return None
    most_recent_file = max(matching_files, key=os.path.getmtime)
    
    print(f"Le fichier CSV le plus récent trouvé est : {most_recent_file}")
    print("Détection du délimiteur du fichier CSV...")
    try:
        with open(most_recent_file, 'r', encoding=encoding) as csvfile:
            sample = csvfile.read(sample_size)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
    except Exception as e:
        print(f"Une erreur est survenue lors de la détection du délimiteur : {e}")
        return None

    print(f"Le délimiteur du fichier CSV est : {delimiter}")
    print("Lecture du fichier CSV...")
    try:
        df = pd.read_csv(most_recent_file, sep=delimiter, encoding=encoding, low_memory=low_memory)
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du fichier CSV : {e}")
        return None

    print("Le fichier CSV a été lu avec succès.")
    return df


def merge_dataframes(df_list, merge_keys, merge_how='left'):
    print("Fusion des dataframes...")
    if not df_list:
        print("La liste des dataframes est vide.")
        return None
    if len(df_list) == 1:
        print("Une seule dataframe a été fournie. Aucune fusion nécessaire.")
        return df_list[0]

    merged_data = df_list[0]
    for i in range(1, len(df_list)):
        print(f"Fusion de la dataframe {i+1}...")
        merged_data = pd.merge(merged_data, df_list[i], how=merge_how, on=merge_keys[i-1])

    print("Les dataframes ont été fusionnées avec succès.")
    return merged_data