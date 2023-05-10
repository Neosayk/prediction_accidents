import os
import time
import glob
import csv
import tarfile
import pandas as pd
from github import Github

def create_destination_folder(source_folder, file_path):
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    destination_folder = os.path.join(file_path, timestamp)
    os.makedirs(destination_folder)
    print(f"Dossier de destination créé : {destination_folder}")
    return destination_folder

def get_artifacts(source_folder):
    file_extensions = ('*.csv', '*.html', '*.pkl')
    artifacts_files = []
    for extension in file_extensions:
        artifacts_files.extend(glob.glob(os.path.join(source_folder, extension)))
    print(f"Nombre de fichiers pris en charge à archiver : {len(artifacts_files)}")
    return artifacts_files

def archive_csv_file(source_file, destination_folder, file_name):
    destination_file = os.path.join(destination_folder, file_name)
    os.rename(source_file, destination_file)
    print(f"Fichier archivé : {source_file} -> {destination_file}")

def read_csv_chunks(csv_file_path, chunk_size=1000):
    with open(csv_file_path, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        chunk = []
        for row in reader:
            chunk.append(row)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk

def process_csv_data(csv_file_path, chunk_size=1000):
    print(f"Lecture et traitement du fichier CSV: {csv_file_path}")
    return pd.read_csv(csv_file_path, chunksize=chunk_size, na_filter=False)

def insert_data_to_supabase(supabase, table_name, data_iterator):
    print(f"Insertion des données dans la table '{table_name}'")
    row_count = 0
    for chunk in data_iterator:
        chunk_data = chunk.to_dict(orient='records')
        response = supabase.table(table_name).insert(chunk_data).execute()
        if response:
            print(f"{len(chunk_data)} lignes insérées avec succès")
            row_count += len(chunk_data)
        else:
            print(f"Échec de l'insertion des données : {response.error}")
    print(f"{row_count} lignes insérées au total dans la base de données")

def upload_to_github(token, repo_name, commit_message, branch, files_with_paths):
    g = Github(token)
    repo = g.get_user().get_repo(repo_name)

    for local_file_path, github_file_path in files_with_paths:
        with open(local_file_path, "rb") as file:
            content = file.read()

        repo.create_file(
            path=github_file_path,
            message=commit_message,
            content=content,
            branch=branch
        )

def compress(input_path, output_file):
    destination_directory = os.getcwd()
    output_file_path = os.path.join(destination_directory, output_file)
    with tarfile.open(output_file_path, "w:gz") as tar:
        if os.path.isfile(input_path):
            arcname = os.path.basename(input_path)
        else:
            arcname = ""
        tar.add(input_path, arcname=arcname)