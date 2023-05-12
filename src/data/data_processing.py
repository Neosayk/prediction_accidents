import pickle
import pandas as pd
import category_encoders as ce


def preprocess_data(df: pd.DataFrame, target, selected_features):
    print("Prétraitement des données...")
    df = df[df[target].isin([1, 2, 3, 4])]
    df = df.groupby(target).apply(lambda x: x.fillna(x.mode().iloc[0])).reset_index(drop=True)
    df[target] = df[target].apply(lambda x: 0 if x in [1, 4] else 1)
    df = df[selected_features].drop_duplicates()
    print("Prétraitement des données terminé.")
    return df


def encode_data(data, target):
    print("Encodage des données...")
    categorical_columns = data.select_dtypes(include=['object'])
    numerical_columns = data.select_dtypes(exclude=['object'])
    encoder = ce.TargetEncoder()
    encoded_data = encoder.fit_transform(categorical_columns, data[target])
    print("Encodage des données terminé.")

    print("Enregistrement de l'encodeur...")
    filename = f"targetencoder.pkl"
    with open(filename, 'wb') as file:
        pickle.dump(encoder, file)
    print("L'encodeur a été enregistré avec succès.")

    return pd.concat([numerical_columns, encoded_data], axis=1)