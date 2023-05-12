# Projet MlOps : Prédictions des accidents routiers en France

## Structure du repositorie Github

prediction_accident
│
├── .github
│   └── workflows
│       └── main.yml
├── data
│   ├── external
│   ├── interim
│   │   └── data_accidents.csv.zip
│   ├── processed
│   │   └── data_accidents_encoded.csv.zip
│   └── raw
│       ├── data_caracteristiques-2020.csv.zip
│       ├── data_lieux-2020.csv.zip
│       ├── data_usagers-2020.csv.zip
│       └── data_vehicules-2020.csv.zip
├── docs
│   ├── Cahier des charges.pdf
│   ├── 29 - Fiche Projet - Accidents routiers en France-update.pdf
│   ├── Projet MLops Template.pdf
│   └── description-des-bases-de-donnees-onisr-annees-2005-a-2020.pdf
├── experiments
├── models
│   ├── xgboost.pkl
│   └── targetencoder.pkl
├── notebooks
│   └── prediction_accidents.ipynb
├── references
├── reports
│   ├── data-profile.html
│   └── figures
├── src
│   ├── app
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── api
│   │   │   ├── main.py
│   │   │   ├── targetencoder.pkl
│   │   │   └── xgboost.pkl
│   │   └── web
│   │       ├── css
│   │       │   └── style.css
│   │       ├── img
│   │       │   ├── Voiture_Poubelle.png
│   │       │   └── place.png
│   │       └── templates
│   │           ├── create.html
│   │           ├── index.html
│   │           ├── modif.html
│   │           ├── pred.html
│   │           ├── reel.html
│   │           ├── role.html
│   │           └── verif.html
│   ├── data
│   │   ├── data_extraction.py
│   │   ├── data_merging.py
│   │   └── data_processing.py
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── features
│   │   └── data_featuring.py
│   ├── models
│   │   ├── data_deployment.py
│   │   ├── data_modeling.py
│   │   ├── data_monitoring.py
│   │   ├── data_tuning.py
│   │   └── data_validation.py
│   ├── requirements.txt
│   ├── visualization
│   │   └── data_profiling.py
│   └── workflows
│       └── dag_prediction_accidents.py
├── tests
│   ├── app
│   │   └── test_routes.py
│   ├── data
│   ├── features
│   ├── models
│   ├── visualization
│   └── workflows
├── docker-compose.yml
└── README.md

## Initialisation de l'infrastructure

1. Clonez le repositorie Github et utilisez un terminal pour vous rendre dans le répertoire téléchargé
2. Renseignez la variable d'environnement "GITHUB_TOKEN" dans les fichiers "./docker-compose.yml" et "./src/config.env"
2. Exécutez la commande "docker-compose up" et attendez jusqu'à la fin de l'initialisation des conteneurs
3. Ouvrez votre navigateur internet pour accéder à la page "localhost:8000" pour accéder à notre API web
4. Entrez les identifiants de test (login: datascientest | password: datascientest) pour tester l'application
5. Ouvrez votre navigateur internet pour accéder à la page "localhost:8080" pour accéder à notre serveur Airflow
6. Entrez les identifiants de test (login: datascientest | password: datascientest) pour tester notre DAG
7. Ouvrez votre navigateur internet pour accéder à la page "supabase.com" pour accéder à notre base de données
8. Entrez les identifiants de test (login: mlops.datascientest@outlook.fr | password: D@t@scientest2023) pour tester notre DAG
7. Utilisez notre notebook disponible dans le répertoire téléchargé pour découvrir nos différentes étapes de modélisation
8. Analysez les résultats de nos expériences de modélisation en cliquant sur le lien généré dans la partie Mlflow du notebook