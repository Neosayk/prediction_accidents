import os
import tarfile
import fnmatch
import glob
from github import Github


def make_tarfile(file_extensions, timestamp):
    target_dir = os.getcwd()

    for file_extension in file_extensions:
        files_to_archive = glob.glob(os.path.join(target_dir, '*' + file_extension))

        for filename in files_to_archive:
            print(f"Commencer la création de l'archive pour {filename}...")
            
            archive_name = os.path.join(target_dir, timestamp + os.path.basename(filename) + '.tar.gz')
            print(f"Le nom de l'archive sera {archive_name}")
            
            with tarfile.open(archive_name, "w:gz") as tar:
                print(f"Ajout de {filename} à l'archive...")
                tar.add(filename, arcname=os.path.basename(filename))
            print(f"Archive {archive_name} créée avec succès.")


def upload_to_github(file_types, token, repo_name, commit_message, branch, file_path_base):
    if isinstance(file_types, str):
        file_types = [file_types]
    print("Préparation pour l'envoi à Github...")
    g = Github(token)
    repo = g.get_user().get_repo(repo_name)

    input_path = os.getcwd()

    for file_type in file_types:
        if os.path.isdir(file_type):
            dir_to_walk = os.path.join(input_path, file_type)
        else:
            dir_to_walk = input_path

        for dirpath, dirnames, filenames in os.walk(dir_to_walk):
            print(f"Dossier actuel : '{dirpath}', sous-dossiers : {dirnames}")
            if not os.path.isdir(file_type):
                filenames = fnmatch.filter(filenames, file_type)
            for filename in filenames:
                local_file_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(local_file_path, input_path).replace('\\', '/')
                
                if rel_path.startswith("mlruns/0"):
                    continue

                if file_type == "mlruns" and rel_path.startswith("mlruns/"):
                    rel_path = rel_path[len("mlruns/"):]
                github_file_path = f"{file_path_base}/{rel_path}"
                with open(local_file_path, "rb") as file:
                    content = file.read()
                try:
                    repo.create_file(
                        path=github_file_path,
                        message=commit_message,
                        content=content,
                        branch=branch
                    )
                except Exception as e:
                    print(f"Erreur lors de la création du fichier '{github_file_path}' sur Github : {str(e)}")
    print(f"Les fichiers ont été téléchargés avec succès sur le dépôt Github '{repo_name}'")


def delete_files(file_extensions):
    for file_extension in file_extensions:
        files_to_delete = glob.glob(f"*{file_extension}")
        for filename in files_to_delete:
            try:
                os.remove(filename)
                print(f"Fichier {filename} supprimé avec succès.")
            except Exception as e:
                print(f"Erreur lors de la suppression du fichier {filename} : {str(e)}")
