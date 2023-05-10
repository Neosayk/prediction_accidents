# Import des bibliothèques nécessaires
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import BranchPythonOperator
import pandas as pd
from sklearn.model_selection import train_test_split
from supabase import create_client, Client
from datetime import timedelta
from dotenv import load_dotenv
import os
import time
import data_extraction
import data_merge
import data_profile
import data_processing
import data_model
import data_management
import data_check
import data_tuning

# Chargement des variables d'environnement
load_dotenv("config.env")

# Fonctions du DAG
## Tâche pour extraire les données "live" à partir de Supabase
def data_extraction_live_func():
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)

    table_name = "data_live"
    output_file = "data_live.csv"
    data_extraction.export_table_to_csv(supabase, table_name, output_file)

## Tâche pour extraire les nouvelles données historiques à partir d'un site Web
def data_extraction_historical_new_func():
    url = "https://www.data.gouv.fr/en/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2021/"
    csv_links = data_extraction.get_csv_links(url)

    downloaded_files_list_filepath = "downloaded_files.txt"
    downloaded_files = data_extraction.get_downloaded_files_list(downloaded_files_list_filepath)

    file_patterns = ['usagers-', 'lieux-', 'cteristiques-', 'vehicules-']
    new_files = data_extraction.download_new_files(csv_links, file_patterns, downloaded_files)

    downloaded_files += new_files
    data_extraction.save_downloaded_files_list(downloaded_files, downloaded_files_list_filepath)

## Tâche pour extraire les anciennes données historiques à partir de Supabase
def data_extraction_historical_old_func():
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)

    table_name = "data_historical"
    output_file = "data_historical_old.csv"
    data_extraction.export_table_to_csv(supabase, table_name, output_file)

## Tâche pour fusionner les nouvelles données historiques, les anciènnes données historiques et les données "live"
def data_merge_func():
    usagers_file = data_merge.find_most_recent_csv_file("*usagers*.csv")
    lieux_file = data_merge.find_most_recent_csv_file("*lieux*.csv")
    caracteristiques_file = data_merge.find_most_recent_csv_file("*cteristiques*.csv")
    vehicules_file = data_merge.find_most_recent_csv_file("*vehicules*.csv")

    if usagers_file and lieux_file and caracteristiques_file and vehicules_file:
        delimiter_usagers = data_merge.find_csv_delimiter(usagers_file)
        delimiter_lieux = data_merge.find_csv_delimiter(lieux_file)
        delimiter_caracteristiques = data_merge.find_csv_delimiter(caracteristiques_file)
        delimiter_vehicules = data_merge.find_csv_delimiter(vehicules_file)

        data_usagers = data_merge.read_csv_with_delimiter(usagers_file, delimiter_usagers)
        data_lieux = data_merge.read_csv_with_delimiter(lieux_file, delimiter_lieux)
        data_caracteristiques = data_merge.read_csv_with_delimiter(caracteristiques_file, delimiter_caracteristiques)
        data_vehicules = data_merge.read_csv_with_delimiter(vehicules_file, delimiter_vehicules)

        data_usagers.to_csv("data_usagers.csv", index=False, encoding='utf-8')
        data_lieux.to_csv("data_lieux.csv", index=False, encoding='utf-8')
        data_caracteristiques.to_csv("data_caracteristiques.csv", index=False, encoding='utf-8')
        data_vehicules.to_csv("data_vehicules.csv", index=False, encoding='utf-8')

        data_management.compress("data_usagers.csv", "data_usagers.csv.tar.gz")
        data_management.compress("data_lieux.csv", "data_lieux.csv.tar.gz")
        data_management.compress("data_caracteristiques.csv", "data_caracteristiques.csv.tar.gz")
        data_management.compress("data_vehicules.csv", "data_vehicules.csv.tar.gz")

        dataframes = [data_usagers, data_vehicules, data_caracteristiques, data_lieux]
        merge_keys = [["Num_Acc", "num_veh"], ["Num_Acc"], ["Num_Acc"]]
        data_historical_new = data_merge.merge_dataframes(dataframes, merge_keys)
        data_historical_new.to_csv("data_historical_new.csv", index=False, encoding='utf-8')
        data_historical_old = pd.read_csv("data_historical_old.csv", sep=',', encoding='latin1', low_memory=False)
        data_historical = pd.concat([data_historical_new, data_historical_old], axis=0, ignore_index=True)
    else:
        data_historical = pd.read_csv("data_historical_old.csv", sep=',', encoding='latin1', low_memory=False)

    if os.path.isfile("data_live.csv"):
        data_live = pd.read_csv("data_live.csv", sep=',', encoding='latin1', low_memory=False)
        data_accidents = pd.concat([data_historical, data_live], axis=0, ignore_index=True)
    else:
        data_accidents = data_historical

    data_accidents.to_csv("data_accidents.csv", index=False, encoding='utf-8')
    data_management.compress("data_accidents.csv", "data_accidents.csv.tar.gz")

## Tâche pour générer un rapport d'analyse exploratoire des données
def data_profile_func():
    data_file = "data_accidents.csv"
    df = pd.read_csv(data_file, sep=',', encoding='latin1', low_memory=False)

    output_file = "data-profile.html"
    title = "Analyse exploratoire des accidents routiers en France"
    data_profile.generate_data_profile(df, output_file, title)

## Tâche pour prétraiter et encoder les données
def data_processing_func():
    data_file = "data_accidents.csv"
    df = pd.read_csv(data_file, sep=',', encoding='latin1', low_memory=False)

    target = "grav"
    selected_features = ["long", "lat", "secu1", "locp", "actp", "agg", "obsm", "etatp", "catv", "col", "place", "obs", "vma", "catu", "manv", "grav"]
    df_preprocessed = data_processing.preprocess_data(df, target, selected_features)

    df_encoded = data_processing.encode_categorical_data(df_preprocessed, target)

    output_file = "data_accidents_encoded.csv"
    df_encoded.to_csv(output_file, index=False, encoding='utf-8')
    data_management.compress("data_accidents_encoded.csv", "data_accidents_encoded.csv.tar.gz")

## Tâche pour entraîner et évaluer le modèle de prédiction
def data_model_func(ti):
    data_file = "data_accidents_encoded.csv"
    df_encoded = pd.read_csv(data_file, sep=',', encoding='latin1', low_memory=False)

    experiment_name = "Accidents_Model"
    target = "grav"
    data_model.train_model(experiment_name, df_encoded, target)

    alert = data_check.check_metrics_and_alert(experiment_name, ti)
    if alert:
        return 'data_tuning_task'
    else:
        return 'data_management_task'

## Tâche pour améliorer les performances du modèle
def data_tuning_func(ti):
    data_file = "data_accidents_encoded.csv"
    df_encoded = pd.read_csv(data_file, sep=',', encoding='latin1', low_memory=False)

    experiment_name = "Accidents_Model"
    target = "grav"
    data_tuning.xgboost_fine_tuning(experiment_name, df_encoded, target, n_iter=100, cv=2)
    
    alert = data_check.check_metrics_and_alert(experiment_name, ti)
    if alert:
        return 'data_alert_task'
    else:
        return 'data_management_task'

## Tâche pour gérer les données
def data_management_func(ti):
    if os.path.isfile("data_historical_new.csv"):
        csv_file_path = "data_historical_new.csv"
        data_iterator = data_management.process_csv_data(csv_file_path)

        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        supabase: Client = create_client(url, key)

        table_name = "data_historical"
        data_management.insert_data_to_supabase(supabase, table_name, data_iterator)

    experiment_name = "Accidents_Model"
    alert = data_check.check_metrics_and_alert(experiment_name, ti)
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    if not alert:
        token = os.getenv("GITHUB_TOKEN")
        repo_name = "prediction_accident"
        commit_message = "Ajout des dernières données d'entrainement"
        branch = "main"
        files_with_paths = [
            ("data_usagers.csv.tar.gz", f"data/raw/{timestamp}/data_usagers.csv.tar.gz"),
            ("data_lieux.csv.tar.gz", f"data/raw/{timestamp}/data_lieux.csv.tar.gz"),
            ("data_caracteristiques.csv.tar.gz", f"data/raw/{timestamp}/data_caracteristiques.csv.tar.gz"),
            ("data_vehicules.csv.tar.gz", f"data/raw/{timestamp}/data_vehicules.csv.tar.gz"),
            ("data_accidents.csv.tar.gz", f"data/interim/{timestamp}/data_accidents.csv.tar.gz"),
            ("data_accidents_encoded.csv.tar.gz", f"data/processed/{timestamp}/data_accidents_encoded.csv.tar.gz"),
        ]
        data_management.upload_to_github(token, repo_name, commit_message, branch, files_with_paths)

        token = os.getenv("GITHUB_TOKEN")
        repo_name = "prediction_accident"
        commit_message = "Ajout du dernier model entrainé"
        branch = "main"
        files_with_paths = [
            ("targetencoder.pkl", f"data/processed/{timestamp}/targetencoder.pkl"),
            ("xgboost.pkl", f"data/processed/{timestamp}/xgboost.pkl"),
        ]
        data_management.upload_to_github(token, repo_name, commit_message, branch, files_with_paths)

    data_management.compress("mlruns", f"mlrun_{timestamp}.tar.gz")
    token = os.getenv("GITHUB_TOKEN")
    repo_name = "prediction_accident"
    commit_message = "Ajout des données de l'expérience mlflow"
    branch = "dev"
    files_with_paths = [
        (f"mlrun_{timestamp}.tar.gz", f"experiments/mlrun_{timestamp}.tar.gz"),
    ]
    data_management.upload_to_github(token, repo_name, commit_message, branch, files_with_paths)

# Initialisation du DAG
default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 5, 7),
    #"retries": 1,
    #"retry_delay": timedelta(minutes=1),
    "provide_context": True,
}

dag = DAG(
    dag_id='prediction_accidents',
    default_args=default_args,
    description='Réentrainement périodique du modèle de prédiction des accidents de la route en France',
    tags=['projet_mlops', 'fbazin', 'jnapol', 'datascientest' ],
    schedule_interval='0 0 1 * *',
    catchup=False,
)


# Définition des tâches du DAG
t0 = DummyOperator(
    task_id='start',
    dag=dag,
)

t1 = PythonOperator(
    task_id='data_extraction_live_task',
    python_callable=data_extraction_live_func,
    dag=dag,
)

t2 = PythonOperator(
    task_id='data_extraction_historical_new_task',
    python_callable=data_extraction_historical_new_func,
    dag=dag,
)

t3 = PythonOperator(
    task_id='data_extraction_historical_old_task',
    python_callable=data_extraction_historical_old_func,
    dag=dag,
)

t4 = PythonOperator(
    task_id='data_merge_task',
    python_callable=data_merge_func,
    dag=dag,
)

t5 = PythonOperator(
    task_id='data_profile_task',
    python_callable=data_profile_func,
    dag=dag,
)

t6 = PythonOperator(
    task_id='data_processing_task',
    python_callable=data_processing_func,
    dag=dag,
)

t7 = PythonOperator(
    task_id='data_model_task',
    python_callable=data_model_func,
    dag=dag,
)

t8 = PythonOperator(
    task_id="data_tuning_task",
    python_callable=data_tuning_func,
    dag=dag,
)

t9 = EmailOperator(
    task_id="data_alert_task",
    to="neoception@gmail.com",
    subject="MLflow Metrics Alert",
    html_content="{{ task_instance.xcom_pull(task_ids='check_metrics_and_generate_email_content') }}",
    dag=dag,
)

t10 = PythonOperator(
    task_id='data_management_task',
    python_callable=data_management_func,
    dag=dag,
)

t11 = DummyOperator(
    task_id='end',
    dag=dag,
)


# Définition de l'ordre d'exécution des tâches du DAG
t0 >> t1
t0 >> t2
t0 >> t3
[t1, t2, t3] >> t4
t4 >> t5
t4 >> t6 >> t7
t7 >> t8
t8 >> t9 >> t10 >> t11
t8 >> t10 >> t11