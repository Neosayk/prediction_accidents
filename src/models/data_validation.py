import mlflow


def check_metrics(experiment_name, ti):
    print("Récupération de l'expérience...")
    experiment = mlflow.get_experiment_by_name(experiment_name)

    print("Récupération du dernier run...")
    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=1,
        order_by=["start_time desc"],
    )
    latest_run = runs.iloc[0]

    thresholds = {
        "accuracy": 0.9,
        "precision_class_0": 0.8,
        "precision_class_1": 0.8,
        "recall_class_0": 0.8,
        "recall_class_1": 0.8,
        "f1_score_class_0": 0.8,
        "f1_score_class_1": 0.8,
    }

    alert = False
    metrics = {}
    print("Vérification des métriques...")
    for metric_name, threshold in thresholds.items():
        metric_value = latest_run[f"metrics.{metric_name}"]
        metrics[metric_name] = metric_value
        if metric_value < threshold:
            print(f"Alerte déclenchée pour {metric_name}")
            alert = True

    if alert:
        print("Préparation du contenu de l'e-mail d'alerte...")
        email_content = "Les métriques suivantes sont en dessous des seuils définis:\n\n"
        for metric_name, metric_value in metrics.items():
            email_content += f"{metric_name}: {metric_value}\n"
        ti.xcom_push(key="alert_email_content", value=email_content)
        return True
    else:
        print("Aucune alerte déclenchée.")
        return False