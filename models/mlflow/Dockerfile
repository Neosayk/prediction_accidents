# Utiliser l'image ubuntu/mlflow:2.1.1_1.0-22.04 comme image de base
FROM ubuntu/mlflow:2.1.1_1.0-22.04

# Mettre à jour le système et installer les outils de construction essentiel
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get install -y git

# Créer le répertoire /mlflow/prediction_accidents et cloner le dépôt Git
RUN mkdir -p /mlflow/prediction_accidents  && \
    git clone -b dev https://github.com/neosayk/prediction_accidents.git /mlflow/prediction_accidents

# Mettre en place le dossier de travail
WORKDIR /mlflow/

# Exposer le port pour MLflow
EXPOSE 5000

# Commande par défaut pour exécuter le serveur MLflow
CMD mlflow server \
    --backend-store-uri /mlflow/prediction_accidents/models/mlflow/mlruns \
    --default-artifact-root /mlflow/prediction_accidents/models/mlflow/mlruns \
    --host 0.0.0.0 \
    --port 5000