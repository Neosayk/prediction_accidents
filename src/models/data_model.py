import mlflow
import pickle
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

def train_model(experiment_name, df_encoded, target):
    current_experiment = mlflow.get_experiment_by_name(experiment_name)
    if current_experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
        print("L'expérience a été créée.")
    else:
        experiment_id = current_experiment.experiment_id
        print("L'expérience existe déjà.")

    with mlflow.start_run(experiment_id = experiment_id):
        X = df_encoded.drop(target, axis=1)
        y = df_encoded[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        print("Les données ont été préparées.")

        model = XGBClassifier()
        model.fit(X_train, y_train)
        print("Le modèle a été entraîné avec les features sélectionnées.")

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average=None)
        recall = recall_score(y_test, y_pred, average=None)
        f1_scores = f1_score(y_test, y_pred, average=None)
        print("Le modèle a été évalué avec les métriques de performance.")

        mlflow.log_param("model", "XGBoost Classifier")
        mlflow.log_metric("accuracy", accuracy)
        for label, p in enumerate(precision):
            mlflow.log_metric(f"precision_class_{label}", p)
        for label, r in enumerate(recall):
            mlflow.log_metric(f"recall_class_{label}", r)
        for label, f1 in enumerate(f1_scores):
            mlflow.log_metric(f"f1_score_class_{label}", f1)
        print("Résultats de l'entraînement sauvegardés")

        filename = "xgboost.pkl"
        with open(filename, 'wb') as file:
            pickle.dump(model, file)
        print("Modèle entraîné sauvegardé")

        mlflow.log_artifact(filename)
        print("Modèle sauvegardé dans MLflow")
        
    print("Entraînement terminé")