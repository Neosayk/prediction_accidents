import csv
import os
import requests
from bs4 import BeautifulSoup

def fetch_table_data_columns(supabase, table_name):
    print(f"Récupération des données et des colonnes de la table {table_name}...")
    response = supabase.table(table_name).select("*").execute()
    data = response.data
    if not data:
        print(f"Aucune donnée trouvée pour la table {table_name}.")
        return None, None
    columns = data[0].keys()
    print(f"Données récupérées avec succès pour la table {table_name}.")
    return data, columns

def write_data_to_csv(data, columns, output_file):
    print(f"Écriture des données au format CSV dans le fichier {output_file}...")
    with open(output_file, mode='w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        if data:
            for row in data:
                writer.writerow(row)
    print(f"Exportation réussie vers {output_file}.")

def export_table_to_csv(supabase, table_name, output_file):
    print("Début de l'exportation de la table au format CSV...")
    data, columns = fetch_table_data_columns(supabase, table_name)
    if data:
        write_data_to_csv(data, columns, output_file)
    print("Exportation terminée.")

def get_csv_links(url):
    print("Récupération des liens CSV depuis l'URL...")
    try:
        html_content = requests.get(url).text
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de l'URL : {e}")
        return []
    soup = BeautifulSoup(html_content, 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.csv')]

def get_downloaded_files_list(filepath):
    print("Récupération de la liste des fichiers téléchargés...")
    try:
        with open(filepath, "r") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []

def save_downloaded_files_list(downloaded_files, filepath):
    print("Sauvegarde de la liste des fichiers téléchargés...")
    with open(filepath, "w") as f:
        f.write("\n".join(downloaded_files))

def download_new_files(csv_links, file_patterns, downloaded_files):
    print("Téléchargement des nouveaux fichiers...")
    new_files = []
    for link in csv_links:
        filename = os.path.basename(link)
        if any(pattern in filename for pattern in file_patterns):
            if filename not in downloaded_files:
                print(f"Téléchargement du fichier : {filename}")
                try:
                    content = requests.get(link).content
                except requests.exceptions.RequestException as e:
                    print(f"Erreur lors du téléchargement du fichier {filename} : {e}")
                    continue
                with open(filename, "wb") as f:
                    f.write(content)
                new_files.append(filename)
        else:
            print(f"Le fichier {filename} ne correspond à aucun des motifs de fichier attendus et ne sera pas téléchargé.")
    return new_files