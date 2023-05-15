# Utiliser une image de base avec Python et Airflow pré-installés
FROM apache/airflow:slim-latest-python3.10

USER root

# Mettre à jour le système et installer les outils de construction essentiel
RUN apt-get update && \
    apt-get install -y build-essential

USER airflow

# Copier les fichiers nécessaires
COPY requirements.txt /requirements.txt
COPY */*.py /opt/airflow/dags/
COPY entrypoint.sh /opt/airflow/entrypoint.sh
COPY config.env /opt/airflow/config.env

# Installer les dépendances
RUN pip install --no-cache-dir -r /requirements.txt
ENTRYPOINT ["/opt/airflow/entrypoint.sh"]