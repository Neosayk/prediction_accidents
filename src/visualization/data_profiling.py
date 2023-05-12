import pandas as pd
from pandas_profiling import ProfileReport


def generate_analysis_report(df: pd.DataFrame, output_file: str, title: str):
    print("Initialisation du rapport...")
    profile = ProfileReport(
        df,
        title=title,
        minimal=True,
        correlations=None,
        html={'style': {'full_width': True}},
    )
    print("Génération du rapport...")
    profile.to_file(output_file=output_file)