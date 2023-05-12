import os
import csv
import requests
from bs4 import BeautifulSoup


def download_csv_files(url, file_patterns, files_filepath):
    print("Récupération du contenu HTML de l'URL...")
    html_content = requests.get(url).text

    print("Analyse du contenu HTML avec BeautifulSoup...")
    soup = BeautifulSoup(html_content, 'html.parser')

    print("Récupération des liens vers les fichiers CSV dans le contenu HTML...")
    csv_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.csv')]
    
    print("Tentative de récupération de la liste des fichiers déjà téléchargés...")
    try:
        with open(files_filepath, "r") as f:
            downloaded_files = f.read().splitlines()
    except FileNotFoundError:
        print("Le fichier de la liste des téléchargements n'a pas été trouvé. Création d'une nouvelle liste...")
        downloaded_files = []
    
    print("Initialisation de la liste des nouveaux fichiers téléchargés...")
    new_files = []
    
    print("Parcours des liens vers les fichiers CSV...")
    for link in csv_links:
        filename = os.path.basename(link)
        if any(pattern in filename for pattern in file_patterns) and filename not in downloaded_files:
            print(f"Téléchargement et sauvegarde du fichier {filename}...")
            content = requests.get(link).content
            with open(filename, "wb") as f:
                f.write(content)
            new_files.append(filename)
            print(f"Fichier {filename} téléchargé avec succès !")
        else:
            print(f"Le fichier {filename} a déjà été téléchargé ou ne correspond pas aux motifs de fichier. Il ne sera pas téléchargé.")

    print("Ajout des nouveaux fichiers à la liste des fichiers déjà téléchargés...")
    downloaded_files += new_files

    print("Sauvegarde de la liste mise à jour des fichiers téléchargés...")
    with open(files_filepath, "w") as f:
        f.write("\n".join(downloaded_files))


def export_to_csv(supabase, table_name, output_file):
    print(f"Récupération des données de la table '{table_name}'...")
    response = supabase.table(table_name).select("*").execute()
    data = response.data

    if not data:
        print(f"Aucune donnée trouvée dans la table '{table_name}'.")
        return None, None
    
    print("Récupération des noms de colonnes...")
    columns = data[0].keys()

    print(f"Écriture des données dans le fichier CSV '{output_file}'...")
    with open(output_file, mode='w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for row in data:
            writer.writerow(row)