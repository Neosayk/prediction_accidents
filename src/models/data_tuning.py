import os
import numpy as np
import mlflow
import pickle
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split, RandomizedSearchCV


def xgboost_fine_tuning(experiment_name, df_encoded, target, n_iter=100, cv=3):
    print("Commencement de l'exécution de la fonction xgboost_fine_tuning...")
    current_experiment = mlflow.get_experiment_by_name(experiment_name)
    if current_experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
    else:
        experiment_id = current_experiment.experiment_id

    with mlflow.start_run(experiment_id = experiment_id):
        print("Début d'une nouvelle exécution MLflow...")
        X = df_encoded.drop(target, axis=1)
        y = df_encoded[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        print("Début de la recherche d'hyperparamètres avec RandomizedSearchCV...")
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

        print("Terminé avec RandomizedSearchCV. Début du calcul des métriques et de la journalisation...")
        best_hyperparameters = random_search.best_params_
        best_model = random_search.best_estimator_
        y_pred = best_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average=None)
        recall = recall_score(y_test, y_pred, average=None)
        f1_scores = f1_score(y_test, y_pred, average=None)

        mlflow.log_param("model", "XGBoost Classifier")
        mlflow.log_param("optimization_method", "RandomizedSearchCV")
        mlflow.log_params(best_hyperparameters)
        mlflow.log_metric("accuracy", accuracy)
        for label, p in enumerate(precision):
            mlflow.log_metric(f"precision_class_{label}", p)
        for label, r in enumerate(recall):
            mlflow.log_metric(f"recall_class_{label}", r)
        for label, f1 in enumerate(f1_scores):
            mlflow.log_metric(f"f1_score_class_{label}", f1)

        print("Sauvegarde du meilleur modèle...")
        filename = "xgboost.pkl"
        with open(filename, 'wb') as file:
            pickle.dump(best_model, file)

        print("Enregistrement des artefacts dans MLflow...")
        pkl_files = [f for f in os.listdir() if f.endswith(".pkl")]
        for pkl_file in pkl_files:
            print(f"Sauvegarde de l'artefact: {pkl_file}")
            mlflow.log_artifact(pkl_file)
