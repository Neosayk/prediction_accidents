# Utiliser l'image ubuntu/mlflow:2.1.1_1.0-22.04 comme image de base
FROM ubuntu/mlflow:2.1.1_1.0-22.04

# Mettre à jour le système et installer les outils de construction essentiel
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get install -y git

# Créer le répertoire /mlflow/projet_mlops et cloner le dépôt Git
RUN mkdir -p /mlflow/projet_mlops  && \
    git clone -b dev https://github.com/neosayk/projet_mlops.git /mlflow/projet_mlops

# Mettre en place le dossier de travail
WORKDIR /mlflow/

# Exposer le port pour MLflow
EXPOSE 5000

# Commande par défaut pour exécuter le serveur MLflow
CMD mlflow server \
    --backend-store-uri /mlflow/projet_mlops/models/mlflow/mlruns \
    --default-artifact-root /mlflow/projet_mlops/models/mlflow/mlruns \
    --host 0.0.0.0 \
    --port 5000