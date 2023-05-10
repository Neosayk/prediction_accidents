import pickle
import pandas as pd
import category_encoders as ce

def preprocess_data(df: pd.DataFrame, target, selected_features):
    print("Suppression des lignes dont la valeur de la cible n'est pas 1, 2, 3 ou 4...")
    df = df[df[target].isin([1, 2, 3, 4])]
    
    print("Remplacement des valeurs manquantes par le mode de chaque groupe de la cible...")
    df = df.groupby(target).apply(lambda x: x.fillna(x.mode().iloc[0])).reset_index(drop=True)
    
    print("Conversion de la cible en 0 si elle est égale à 1 ou 4, sinon en 1...")
    df[target] = df[target].apply(lambda x: 0 if x in [1, 4] else 1)
    
    df = df[selected_features].drop_duplicates()
    
    return df


def encode_categorical_data(data, target):
    print("Encodage des colonnes catégorielles avec TargetEncoder...")
    categorical_columns = data.select_dtypes(include=['object'])
    numerical_columns = data.select_dtypes(exclude=['object'])
    encoder = ce.TargetEncoder()
    encoded_data = encoder.fit_transform(categorical_columns, data[target])

    filename = f"targetencoder.pkl"
    with open(filename, 'wb') as file:
        pickle.dump(encoder, file)
    print("Encodeur entraîné sauvegardé")

    return pd.concat([numerical_columns, encoded_data], axis=1)