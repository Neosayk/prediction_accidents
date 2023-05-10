import pandas as pd
from pandas_profiling import ProfileReport

def generate_data_profile(df: pd.DataFrame, output_file: str, title: str):
    print("Création du profile...")
    profile = ProfileReport(
        df,
        title=title,
        minimal=True,
        correlations=None,
        html={'style': {'full_width': True}},
    )
    print("Génération du rapport...")
    profile.to_file(output_file=output_file)
    print(f"Le rapport a été généré avec succès et enregistré dans le fichier {output_file}.")