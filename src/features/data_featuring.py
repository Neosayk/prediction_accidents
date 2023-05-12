import mlflow
import pickle
import os
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split


def train_model(experiment_name, df_encoded, target):
    print("Début de l'entraînement du modèle...")
    current_experiment = mlflow.get_experiment_by_name(experiment_name)
    if current_experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
        print(f"Création d'une nouvelle expérience MLflow avec l'ID : {experiment_id}")
    else:
        experiment_id = current_experiment.experiment_id
        print(f"Utilisation de l'expérience MLflow existante avec l'ID : {experiment_id}")

    with mlflow.start_run(experiment_id = experiment_id):
        print("Préparation des données pour l'entraînement...")
        X = df_encoded.drop(target, axis=1)
        y = df_encoded[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        print("Construction et entraînement du modèle XGBClassifier...")
        model = XGBClassifier()
        model.fit(X_train, y_train)

        print("Classement des features en fonction de leurs importances...")
        importances = model.feature_importances_
        feature_importances = sorted(zip(X.columns, importances), key=lambda x: x[1], reverse=True)
        selected_features = [feature for feature, importance in feature_importances[:15]]
        print(f"Les 15 features les plus importantes sont : {selected_features}")

        print("Prédiction et calcul des métriques...")
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average=None)
        recall = recall_score(y_test, y_pred, average=None)
        f1_scores = f1_score(y_test, y_pred, average=None)

        print("Enregistrement des paramètres et des métriques dans MLflow...")
        mlflow.log_param("model", "XGBoost Classifier")
        mlflow.log_param("top15_feature", selected_features)
        mlflow.log_metric("accuracy", accuracy)
        for label, p in enumerate(precision):
            mlflow.log_metric(f"precision_class_{label}", p)
        for label, r in enumerate(recall):
            mlflow.log_metric(f"recall_class_{label}", r)
        for label, f1 in enumerate(f1_scores):
            mlflow.log_metric(f"f1_score_class_{label}", f1)

        print("Sauvegarde du modèle...")
        filename = "xgboost.pkl"
        with open(filename, 'wb') as file:
            pickle.dump(model, file)

        print("Enregistrement des artefacts dans MLflow...")
        csv_files = [f for f in os.listdir() if f.endswith(".csv")]
        txt_files = [f for f in os.listdir() if f.endswith(".txt")]
        pkl_files = [f for f in os.listdir() if f.endswith(".pkl")]
        files = [csv_files, txt_files, pkl_files]
        for file_list in files:
            for file in file_list:
                print(f"Sauvegarde de l'artefact: {file}")
                mlflow.log_artifact(file)