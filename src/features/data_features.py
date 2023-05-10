import mlflow
import time
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

        importances = model.feature_importances_
        feature_importances = sorted(zip(X.columns, importances), key=lambda x: x[1], reverse=True)
        selected_features = [feature for feature, importance in feature_importances[:15]]
        print(f"Les 15 features les plus importantes sont : {selected_features}")

        mlflow.log_param("model", "XGBoost Classifier")
        mlflow.log_param("top15_feature", selected_features)
        print("Résultats de l'entraînement sauvegardés")
        
    print("Entraînement terminé")