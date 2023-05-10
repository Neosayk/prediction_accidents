import os
import json
from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock, patch
from main import app, Authentification, user

client = TestClient(app)

# Exemple de données d'entrée pour les tests
input_data_predict = {
    "long": "2.34445",
    "lat": "48.86138",
    "secu1": 1,
    "locp": 1,
    "actp": "A",
    "agg": 1,
    "obsm": 1,
    "etatp": 1,
    "catv": 7,
    "col": 3,
    "place": 1,
    "obs": 0,
    "vma": 50,
    "catu": 1,
    "manv": 1
}

input_data_reel = {
    "long": "2.34445",
    "lat": "48.86138",
    "secu1": 1,
    "locp": 1,
    "actp": "A",
    "agg": 1,
    "obsm": 1,
    "etatp": 1,
    "catv": 7,
    "col": 3,
    "place": 1,
    "obs": 0,
    "vma": 50,
    "catu": 1,
    "manv": 1,
    "grav": 1
}

test_user = user(username="test", password="test123", role="admin")

# Route d'accueil
def test_root():
    response = client.get("/rootOK")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, bienvenue sur l'API graPYte"}

# Route de vérification des utilisateurs
@patch("main.Authentification", return_value=test_user)
def test_user_verif(auth_mock):
    response = client.get("/user/verifOK")
    assert response.status_code == 200
    assert "Identifiants incorrects" not in response.text

# Route de modification des utilisateurs
@patch("main.Authentification", return_value=test_user)
def test_user_modif(auth_mock):
    response = client.post("/user/modifOK", json={"username": "test", "role": "admin"})
    assert response.status_code == 200
    assert "Identifiants incorrects" not in response.text

# Route de création des utilisateurs
@patch("main.Authentification", return_value=test_user)
def test_user_create(auth_mock):
    response = client.post("/user/createOK", json={"username": "new_user", "password": "new_password", "role": "user"})
    assert response.status_code == 200
    assert "Identifiants incorrects" not in response.text

# Route de prédiction
@patch("main.Authentification", return_value=test_user)
def test_prediction(auth_mock):
    response = client.post("/predictionOK", json=input_data_predict)
    assert response.status_code == 200
    assert "Identifiants incorrects" not in response.text

# Route de sauvegarde
@app.post("/reelOK")
async def sauvegarder(jsonBody: InputDataReel, request: Request, username: Annotated[Union[str, None], Cookie()] = None, password: Annotated[Union[str, None], Cookie()] = None):
    print(username, password)
    user = supabase.table("Data_Users").select("*").eq("username", username).execute()
    user2 = user.data[0]
    if (username == None or password == None):
        return {"message": "Identifiants incorrects"}
    if (user2["role"] != "admin"):
        return {"message": "Vous n'avez pas les droits pour créer un utilisateur"}
    if (user2["password"] != password):
        return {"message": "Identifiants incorrects"}
	# Modification des valeurs
    res = supabase.table("Data_Reels").insert({
		"long": jsonBody.long,
		"lat": jsonBody.lat,
		"secu1": jsonBody.secu1,
		"locp": jsonBody.locp,
		"actp": jsonBody.actp,
		"agg": jsonBody.agg,
		"obsm": jsonBody.obsm,
		"etatp": jsonBody.etatp,
		"catv": jsonBody.catv,
		"col": jsonBody.col,
		"place": jsonBody.place,
		"obs": jsonBody.obs,
		"vma": jsonBody.vma, 
		"catu": jsonBody.catu, 
		"manv": jsonBody.manv, 
		"grav": jsonBody.grav,
	}).execute()
    result = "Vos données sont sauvegardées"
    return templates.TemplateResponse("reel.html", {"request": request, "resultat": result})