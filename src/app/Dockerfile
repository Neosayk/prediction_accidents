# Utiliser l'image Python officielle comme base
FROM python:slim

# Mettre à jour le système et installer les outils de construction
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get install -y curl

# Définir le répertoire de travail
WORKDIR /app

# Copier les exigences de l'API et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'API web
COPY ./api .
COPY ./web .
COPY config.env .

# Exposer le port sur lequel l'application sera accessible
EXPOSE 8000

# Démarrer l'API avec Uvicorn
CMD ["/bin/sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000"]