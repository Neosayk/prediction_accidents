# Projet MlOps : Prédictions des accidents routiers en France


## Structure du repositorie Github

prediction_accidents
├── tests
│   └── app
│       └── api
│           ├── cleanup_pkl.py
│           └── test_routes.py
├── models
│   └── mlflow
│       ├── Dockerfile
│       └── mlruns
│           └── see_dev_branch
├── docs
│   ├── Cahier des charges.pdf
│   ├── 29 - Fiche Projet - Accidents routiers en France-update.pdf
│   ├── Projet MLops Template.pdf
│   └── description-des-bases-de-donnees-onisr-annees-2005-a-2020.pdf
├── README.md
├── docker-compose.yml
├── data
│   └── see_dev_branch
├── notebooks
│   └── prediction_accidents.ipynb
├── reports
│   └── see_dev_branch
└── src
    ├── visualization
    │   └── data_profiling.py
    ├── app
    │   ├── requirements.txt
    │   ├── Dockerfile
    │   ├── config.env
    │   └── web
    │       ├── css
    │       │   └── style.css
    │       ├── img
    │       │   ├── place.png
    │       │   └── Voiture_Poubelle.png
    │       └── templates
    │           ├── index.html
    │           ├── modif.html
    │           ├── create.html
    │           ├── reel.html
    │           ├── role.html
    │           ├── verif.html
    │           └── pred.html
    ├── api
    │   ├── 2023XXXX_XXXXXX_targetencoder.pkl
    │   ├── 2023XXXX_XXXXXX_xgboost.pkl
    │   └── main.py
    ├── requirements.txt
    ├── Dockerfile
    ├── features
    │   └── data_featuring.py
    ├── workflows
    │   └── dag_prediction_accidents.py
    ├── models
    │   ├── data_monitoring.py
    │   ├── data_tuning.py
    │   ├── data_deployment.py
    │   ├── data_modeling.py
    │   └── data_validation.py
    ├── config.env
    ├── data
    │   ├── data_processing.py
    │   ├── data_extraction.py
    │   └── data_merging.py
    └── entrypoint.sh


## Initialisation de l'infrastructure

1. Clonez le repositorie Github et utilisez un terminal pour vous rendre dans le répertoire téléchargé
2. Renseignez les variables d'environnement dans les fichiers "./docker-compose.yml", "./src/config.env" et "./src/app/config.env"
2. Exécutez la commande "docker-compose up" depuis l'emplacement du répertoire téléchargé et attendez la fin de l'initialisation des conteneurs

3. Ouvrez votre navigateur internet à la page "localhost:8000" afin d'accéder à notre API web
5. Ouvrez votre navigateur internet à la page "localhost:8080" afin d'accéder à notre DAG Airflow
6. Ouvrez votre navigateur internet à la page "localhost:5001" afin d'accéder à nos expériences Mlflow
7. Ouvrez votre navigateur internet à la page "supabase.com" afin d'accéder à notre base de données
8. Ouvrez notre notebook disponible dans le répertoire téléchargé pour découvrir les différentes étapes de modélisation

N.B. : Contactez-nous pour obtenir les différents identifiants de connexion.