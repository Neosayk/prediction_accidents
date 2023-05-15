# Importation des bibliothèques nécessaires
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.email_operator import EmailOperator
from supabase import create_client, Client
from dotenv import load_dotenv
import time
import os
import glob
import pandas as pd
import data_extraction
import data_merging
import data_profiling
import data_processing
import data_modeling
import data_deployment
import data_validation
import data_tuning
import data_monitoring


# Initialisation de l'environnement de travail
load_dotenv("config.env")


# Fonctions du DAG
## Tâche pour extraire les données "live" à partir de Supabase
def data_extraction_live_func():
    print("Initialisation du téléchargement des données live...")
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    table_name = "data_live"
    output_file = "data_live.csv"
    data_extraction.export_to_csv(supabase, table_name, output_file)
    print("Téléchargement des données live terminé.")

## Tâche pour extraire les nouvelles données historiques à partir du site web
def data_extraction_historical_new_func():
    print("Initialisation du téléchargement des nouvelles données historiques...")
    url = "https://www.data.gouv.fr/en/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2021/"
    file_patterns = ['usagers-', 'lieux-', 'cteristiques-', 'vehicules-']
    files_filepath = "downloaded_files.txt"
    data_extraction.download_csv_files(url, file_patterns, files_filepath)
    print("Téléchargement des nouvelles données historiques terminé.")

## Tâche pour extraire les anciennes données historiques à partir de Supabase
def data_extraction_historical_old_func():
    print("Initialisation du téléchargement des anciennes données historiques...")
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    table_name = "data_historical"
    output_file = "data_historical_old.csv"
    data_extraction.export_to_csv(supabase, table_name, output_file)
    print("Téléchargement des anciennes données historiques terminé.")

## Tâche pour fusionner les nouvelles données historiques, les anciènnes données historiques et les données "live"
def data_merging_func():
    print("Initialisation de la fusion des données...")
    data_usagers = data_merging.csv_to_dataframe(pattern="*usagers*.csv")
    data_vehicules = data_merging.csv_to_dataframe(pattern="*vehicules*.csv")
    data_caracteristiques = data_merging.csv_to_dataframe(pattern="*cteristiques*.csv")
    data_lieux = data_merging.csv_to_dataframe(pattern="*lieux*.csv")
    if data_usagers is not None and data_vehicules is not None and data_caracteristiques is not None and data_lieux is not None:
        df_list = [data_usagers, data_vehicules, data_caracteristiques, data_lieux]
        merge_keys = [["Num_Acc", "num_veh"], ["Num_Acc"], ["Num_Acc"]]
        data_historical_new = data_merging.merge_dataframes(df_list, merge_keys)
        data_historical_new.to_csv("data_historical_new.csv", index=False, encoding='utf-8')

        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        supabase: Client = create_client(url, key)
        data_merging.upload_to_supabase(
            csv_file_path = "data_historical_new.csv",
            chunk_size = 1000,
            supabase = supabase,
            table_name = "data_historical",
        )

        if os.path.isfile("data_historical_old.csv"):
            data_historical_old = pd.read_csv("data_historical_old.csv", sep=',', encoding='latin1', low_memory=False)
            data_historical = pd.concat([data_historical_new, data_historical_old], axis=0, ignore_index=True)
        else:
            data_historical = data_historical_new
    else:
        data_historical = pd.read_csv("data_historical_old.csv", sep=',', encoding='latin1', low_memory=False)

    if os.path.isfile("data_live.csv"):
        data_live = pd.read_csv("data_live.csv", sep=',', encoding='latin1', low_memory=False)
        data_accidents = pd.concat([data_historical, data_live], axis=0, ignore_index=True)
    else:
        data_accidents = data_historical

    data_accidents.to_csv("data_accidents.csv", index=False, encoding='utf-8')
    print("Fusion des données terminée.")

## Tâche pour générer un rapport d'analyse exploratoire des données
def data_profiling_func():
    print("Initialisation de la création du rapport d'analyse exploratoire des données...")
    df = pd.read_csv("data_accidents.csv", sep=',', encoding='latin1', low_memory=False)
    output_file = "data_profile.html"
    title = "Analyse exploratoire des accidents routiers en France"
    data_profiling.generate_analysis_report(df, output_file, title)
    print("Création du rapport d'analyse exploratoire des données terminée.")

## Tâche pour prétraiter et encoder les données
def data_processing_func():
    print("Initialisation du traitement des données...")
    df = pd.read_csv("data_accidents.csv", sep=',', encoding='latin1', low_memory=False)
    target = "grav"
    selected_features = ["long", "lat", "secu1", "locp", "actp", "agg", "obsm", "etatp", "catv", "col", "place", "obs", "vma", "catu", "manv", "grav"]
    df_preprocessed = data_processing.preprocess_data(df, target, selected_features)
    df_encoded = data_processing.encode_data(df_preprocessed, target)
    df_encoded.to_csv("data_accidents_encoded.csv", index=False, encoding='utf-8')
    print("Traitement des données terminée.")

## Tâche pour entraîner et évaluer le modèle de prédiction
def data_modeling_func():
    print("Initialisation de la création du model de machine learning...")
    experiment_name = "Accidents_Model"
    df_encoded = pd.read_csv("data_accidents_encoded.csv", sep=',', encoding='latin1', low_memory=False)
    target = "grav"
    data_modeling.train_model(experiment_name, df_encoded, target)
    print("Création du model de machine learning terminée.")

## Tâche pour vérifier les performances du modèle
def data_validation_func1(ti):
    print("Initialisation de la vérification des métriques de performance...")
    experiment_name = "Accidents_Model"
    alert = data_validation.check_metrics(experiment_name, ti)
    print("Vérification des métriques de performance terminée...")
    if alert:
        return 'data_tuning_task'
    else:
        return 'data_deployment_task'

## Tâche pour améliorer les performances du modèle
def data_tuning_func():
    print("Initialisation du tuning des performances du model de machine learning...")
    experiment_name = "Accidents_Model"
    df_encoded = pd.read_csv("data_accidents_encoded.csv", sep=',', encoding='latin1', low_memory=False)
    target = "grav"
    data_tuning.xgboost_fine_tuning(experiment_name, df_encoded, target)
    print("Tuning des performances du model de machine learning terminée.")

## Tâche pour vérifier les performances du modèle
def data_validation_func2(ti):
    print("Initialisation de la vérification des métriques de performance...")
    experiment_name = "Accidents_Model"
    alert = data_validation.check_metrics(experiment_name, ti)
    print("Vérification des métriques de performance terminée...")
    if alert:
        return 'data_alert_task'
    else:
        return 'data_deployment_task'

## Tâche pour déployer le modèle de machine learning en production
def data_deployment_func():
    print("Initialisation du déploiement du model de machine learning en production...")
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    token = os.getenv("GITHUB_TOKEN")

    targetencoder_files = glob.glob('/opt/airflow/mlruns/**/targetencoder.pkl', recursive=True)
    most_recent_targetencoder_file = max(targetencoder_files, key=os.path.getmtime)
    data_deployment.upload_to_github(
        timestamp = timestamp,
        input_path = most_recent_targetencoder_file,
        token = token,
        repo_name = "prediction_accidents",
        commit_message = "Airflow : Ajout du dernier encodeur entrainé",
        branch = "main",
    )
    print("Déploiement du model de machine learning en production terminée.")

    xgboost_files = glob.glob('/opt/airflow/mlruns/**/xgboost.pkl', recursive=True)
    most_recent_xgboost_file = max(xgboost_files, key=os.path.getmtime)
    data_deployment.upload_to_github(
        timestamp = timestamp,
        input_path = most_recent_xgboost_file,
        token = token,
        repo_name = "prediction_accidents",
        commit_message = "Airflow : Ajout du dernier model entrainé",
        branch = "main",
    )

## Tâche pour enregistrer les données de l'expérience
def data_monitoring_func():
    print("Initialisation de l'enregistrement des données de l'expérience...")
    token = os.getenv("GITHUB_TOKEN")

    file_extensions = ['csv', 'html']
    data_monitoring.make_tarfile(file_extensions)

    data_monitoring.upload_to_github(
        paths="*.csv.tar.gz",
        token=token,
        repo_name="prediction_accidents",
        commit_message="Airflow : Ajout des données du dernier entrainement",
        branch="dev",
        file_path_base="data",
    )

    data_monitoring.upload_to_github(
        paths="*.html.tar.gz",
        token=token,
        repo_name="prediction_accidents",
        commit_message="Airflow : Ajout du dernier rapport d'analyse exploratoire",
        branch="dev",
        file_path_base="reports",
    )

    data_monitoring.upload_to_github(
        paths="mlruns",
        token=token,
        repo_name="prediction_accidents",
        commit_message="Airflow : Ajout des artifacts mlflow du dernier entrainement",
        branch="dev",
        file_path_base="models/mlflow/mlruns",
    )

    file_extensions = ['.txt', '.csv', '.html', '.pkl', '.tar.gz']
    data_monitoring.delete_files(file_extensions)
    print("Enregistrement des données de l'expérience terminée.")


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
    tags=['fbazin', 'jnapol', 'datascientest' ],
    schedule_interval='0 0 1 * *',
    catchup=False,
)


# Définition des tâches du DAG
start = DummyOperator(
    task_id='start',
    dag=dag,
)

task1 = PythonOperator(
    task_id='data_extraction_live_task',
    python_callable=data_extraction_live_func,
    dag=dag,
)

task2 = PythonOperator(
    task_id='data_extraction_historical_new_task',
    python_callable=data_extraction_historical_new_func,
    dag=dag,
)

task3 = PythonOperator(
    task_id='data_extraction_historical_old_task',
    python_callable=data_extraction_historical_old_func,
    dag=dag,
)

task4 = PythonOperator(
    task_id='data_merging_task',
    python_callable=data_merging_func,
    dag=dag,
)

task5 = PythonOperator(
    task_id='data_profiling_task',
    python_callable=data_profiling_func,
    dag=dag,
)

task6 = PythonOperator(
    task_id='data_processing_task',
    python_callable=data_processing_func,
    dag=dag,
)

task7 = PythonOperator(
    task_id='data_modeling_task',
    python_callable=data_modeling_func,
    dag=dag,
)

branch1 = BranchPythonOperator(
    task_id='data_validation_task1',
    python_callable=data_validation_func1,
    dag=dag,
)

task8 = PythonOperator(
    task_id="data_tuning_task",
    python_callable=data_tuning_func,
    dag=dag,
)

branch2 = BranchPythonOperator(
    task_id='data_validation_task2',
    python_callable=data_validation_func2,
    dag=dag,
)

task9 = EmailOperator(
    task_id="data_alert_task",
    to="mlops.datascientest@outlook.fr",
    subject="MLflow Metrics Alert",
    html_content="{{ task_instance.xcom_pull(task_ids='data_tuning_task') }}",
    dag=dag,
)

task10 = PythonOperator(
    task_id='data_deployment_task',
    python_callable=data_deployment_func,
    dag=dag,
    trigger_rule='none_failed',
)

task11 = PythonOperator(
    task_id='data_monitoring_task',
    python_callable=data_monitoring_func,
    dag=dag,
    trigger_rule='none_failed',
)

end = DummyOperator(
    task_id='end',
    dag=dag,
    trigger_rule='none_failed',
)


# Définition de l'ordre d'exécution des tâches du DAG
start >> [task1, task2, task3] >> task4
task4 >> task5 >> end
task4 >> task6 >> task7 >> branch1

branch1 >> [task8, task10]
task8 >> branch2
task10 >> task11 >> end

branch2 >> [task9, task10]
task9 >> task11 >> end
task10 >> task11 >> end