import os
from github import Github


def upload_to_github(input_path, token, repo_name, commit_message, branch, timestamp):
    print("Préparation pour l'envoi à Github...")
    g = Github(token)
    repo = g.get_user().get_repo(repo_name)

    local_file_path = input_path
    github_file_path = f"src/app/api/{timestamp}_{os.path.basename(local_file_path)}"
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
    print(f"Le fichier '{github_file_path}' a été téléchargé avec succès sur le dépôt Github '{repo_name}'")