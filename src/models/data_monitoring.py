import os
import time
from github import Github

def upload_to_github(input_path, token, repo_name, commit_message, branch, timestamp):
    print("Préparation pour l'envoi à Github...")
    g = Github(token)
    repo = g.get_user().get_repo(repo_name)
    for dirpath, dirnames, filenames in os.walk(input_path):
        print(f"Dossier actuel : '{dirpath}', sous-dossiers : {dirnames}")
        for filename in filenames:
            local_file_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(local_file_path, input_path).replace('\\', '/')
            github_file_path = f"experiments/mlruns/{timestamp}_{rel_path}"
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