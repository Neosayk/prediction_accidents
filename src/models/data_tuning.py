# Import des bibliothèques nécessaires
from xgboost import XGBClassifier
import numpy as np
import mlflow
import pickle
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split, RandomizedSearchCV

def xgboost_fine_tuning(experiment_name, df_encoded, target, n_iter=100, cv=3):
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

        model = XGBClassifier(objective='binary:logistic', random_state=42)

        param_grid = {
            "learning_rate": np.logspace(-3, 0, num=200),
            "max_depth": np.arange(1, 10),
            "n_estimators": np.arange(50, 300, step=10),
            "gamma": np.logspace(-8, 0, num=200),
            "min_child_weight": np.arange(1, 10),
            "subsample": np.linspace(0.5, 1, num=100),
            "colsample_bytree": np.linspace(0.5, 1, num=100),
            "reg_alpha": np.logspace(-8, 0, num=200),
            "reg_lambda": np.logspace(-8, 0, num=200),
        }

        random_search = RandomizedSearchCV(
            model, 
            param_distributions=param_grid, 
            n_iter=n_iter, 
            scoring="neg_mean_squared_error", 
            cv=cv, 
            n_jobs=-1, 
            random_state=42
        )

        random_search.fit(X_train, y_train)

        best_hyperparameters = random_search.best_params_
        print(f"Best hyperparameters: {best_hyperparameters}")

        best_model = random_search.best_estimator_
        y_pred = best_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average=None)
        recall = recall_score(y_test, y_pred, average=None)
        f1_scores = f1_score(y_test, y_pred, average=None)
        print("Le modèle a été évalué avec les métriques de performance.")

        mlflow.log_param("model", "XGBoost Classifier")
        mlflow.log_param("method_optimazer", "RandomizedSearchCV")
        mlflow.log_params(best_hyperparameters)
        mlflow.log_metric("accuracy", accuracy)
        for label, p in enumerate(precision):
            mlflow.log_metric(f"precision_class_{label}", p)
        for label, r in enumerate(recall):
            mlflow.log_metric(f"recall_class_{label}", r)
        for label, f1 in enumerate(f1_scores):
            mlflow.log_metric(f"f1_score_class_{label}", f1)
        print("Résultats de l'entraînement sauvegardés")

        filename = f"xgboost.pkl"
        with open(filename, 'wb') as file:
            pickle.dump(best_model, file)
        print("Modèle entraîné sauvegardé")

        mlflow.log_artifact(filename)
        print("Modèle sauvegardé dans MLflow")

    print("Entraînement terminé")