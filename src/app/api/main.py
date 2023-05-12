# Importation des bibliothèques
import os
import json
import pandas as pd
import numpy as np
import pickle
import glob
from fastapi import FastAPI, Depends, Request, Cookie, FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from typing import Annotated, Union

# Chargement des variables d'environnement
load_dotenv("config.env")

# Connection avec la BDD
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

app = FastAPI()

# Rediriger les images du dossier img sur le localhost
app.mount("/img", StaticFiles(directory="img"), name="img")
# Rediriger les fichiers css du dossier css sur le localhost
app.mount("/css", StaticFiles(directory="css"), name="css")

# Selection du dossier de templates pour les templates
templates = Jinja2Templates(directory="templates")

# Creation des Class
class InputDataPredict(BaseModel):
    long: object
    lat: object
    secu1: int
    locp: int
    actp: object
    agg: int
    obsm: int
    etatp: int
    catv: int
    col: int
    place: int
    obs: int
    vma: int
    catu: int
    manv: int

class InputDataReel(BaseModel):
    long: object
    lat: object
    secu1: int
    locp: int
    actp: object
    agg: int
    obsm: int
    etatp: int
    catv: int
    col: int
    place: int
    obs: int
    vma: int
    catu: int
    manv: int
    grav: int

# Chargement de l'encodeur et du modèles
targetencoder_files = glob.glob('*targetencoder.pkl', recursive=True)
most_recent_targetencoder_file = max(targetencoder_files, key=os.path.getmtime)
with open(most_recent_targetencoder_file, 'rb') as pickle_file:
    encoder = pickle.load(pickle_file)

xgboost_files = glob.glob('*xgboost.pkl', recursive=True)
most_recent_xgboost_file = max(xgboost_files, key=os.path.getmtime)
with open(most_recent_xgboost_file, 'rb') as pickle_file:
    model = pickle.load(pickle_file)

# Route de test de l'API
@app.get("/root")
async def root():
    return {"message": "Hello, bienvenue sur l'API graPYte"}

# Route d'accueil et connexion pour l'utilisateur
@app.get("/")
async def auth_Cookie(request: Request, username: str = "", password: str = ""):
    if (username == "" or password == ""):
        return templates.TemplateResponse("verif.html", {"request": request, "resultat": ""})
    res = supabase.table("data_users").select("*").eq("username", username).execute()
    if (len(res.data) < 1):
        return templates.TemplateResponse("verif.html", {"request": request, "resultat": "Mauvais username"})
    if (res.data[0]["password"] != password):
        return templates.TemplateResponse("verif.html", {"request": request, "resultat": "Mauvais password"})
    response = RedirectResponse(url="/index")
    response.set_cookie(key="username", value=username)
    response.set_cookie(key="password", value=password)
    return response

# Route pour suprrimer le cookie
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie(key="username")
    response.delete_cookie(key="password")
    return response

# Route pour page une fois que l'utilisateur est connecté
@app.get("/index")
async def index(request: Request, username: Annotated[Union[str, None], Cookie()] = None, password: Annotated[Union[str, None], Cookie()] = None):
    if (username == None or password == None):
        return RedirectResponse(url="/")
    res = supabase.table("data_users").select("*").eq("username", username).execute()
    if (len(res.data) < 1):
        return RedirectResponse(url="/")
    if (res.data[0]["password"] != password):
        return RedirectResponse(url="/")
    return templates.TemplateResponse("index.html", {"request": request})

# Route pour page : connaitre les infos de l'utilisateur connecte
@app.get("/role")
async def user_Verif(request: Request, username: Annotated[Union[str, None], Cookie()] = None, password: Annotated[Union[str, None], Cookie()] = None):
    if (username == None or password == None):
        return RedirectResponse(url="/")
    res = supabase.table("data_users").select("*").eq("username", username).execute()
    if (len(res.data) < 1):
        return RedirectResponse(url="/")
    if (res.data[0]["password"] != password):
        return RedirectResponse(url="/")
    result = str(res.data[0])
    return templates.TemplateResponse("role.html", {"request": request, "resultat": result})

# Route pour page : modifier un utilisateur
@app.get("/modif")
async def user_Modif(request: Request, uname: str = "", role: str = "", username: Annotated[Union[str, None], Cookie()] = None, password: Annotated[Union[str, None], Cookie()] = None):
    if (username == None or password == None):
        return RedirectResponse(url="/")
    user = supabase.table("data_users").select("*").eq("username", username).execute()
    user2 = user.data[0]
    if (user2["password"] != password):
        return RedirectResponse(url="/")
    if (user2["role"] != "admin"):
        return templates.TemplateResponse("modif.html", {"request": request, "resultat": "Vous n'avez pas les droits pour modifier un utilisateur"})
    if (uname == "" or role == ""):
        return templates.TemplateResponse("modif.html", {"request": request, "resultat": ""})
    res = supabase.table("data_users").update({"role": role}).eq("username", uname).execute()
    if (len(res.data) == 0):
        return templates.TemplateResponse("modif.html", {"request": request, "resultat": "Utilisateur non trouvé"})
    result = str(res.data[0])
    return templates.TemplateResponse("modif.html", {"request": request, "resultat": result})

# Route pour page : creer un utilisateur
@app.get("/create")
async def user_edit(request: Request, uname: str = "", passw: str = "", role: str = "", username: Annotated[Union[str, None], Cookie()] = None, password: Annotated[Union[str, None], Cookie()] = None):
    if (username == None or password == None):
        return RedirectResponse(url="/")
    user = supabase.table("data_users").select("*").eq("username", username).execute()
    user2 = user.data[0]
    if (user2["password"] != password):
        return RedirectResponse(url="/")
    if (user2["role"] != "admin"):
        return templates.TemplateResponse("create.html", {"request": request, "resultat": "Vous n'avez pas les droits pour modifier un utilisateur"})
    if (uname == "" or passw == "" or role == ""):
        return templates.TemplateResponse("create.html", {"request": request, "resultat": "missing parameter(s)"})
    res = supabase.table("data_users").insert({"username": uname, "password": passw, "role": role}).execute()
    result = res.data[0]
    return templates.TemplateResponse("create.html", {"request": request, "resultat": result})

# Route pour page : prédiction
@app.get("/prediction")
async def prediciton(request: Request, username: Annotated[Union[str, None], Cookie()] = None, password: Annotated[Union[str, None], Cookie()] = None, long: str = "string", lat: str = "string", secu1: str = "", locp: str = "", actp: str = "string", agg: str = "", obsm: str = "", etatp: str = "", catv: str = "", col: str = "", place: str = "", obs: str = "", vma: str = "", catu: str = "", manv: str = ""):
    if (username == None or password == None):
        return RedirectResponse(url="/")
    user = supabase.table("data_users").select("*").eq("username", username).execute()
    user2 = user.data[0]
    if (user2["password"] != password):
        return RedirectResponse(url="/")
    if (user2["role"] != "admin" and user2["role"] != "user"):
        return templates.TemplateResponse("pred.html", {"request": request, "resultat": "Vous n'avez pas les droits pour modifier un utilisateur"})

    if (not place.isdigit() or not vma.isdigit()):
        return templates.TemplateResponse("pred.html", {"request": request, "resultat": "Missing parameter(s)"})

    data = InputDataPredict(
        long = str(long),
        lat = str(lat),
        secu1 = int(secu1),
        locp = int(locp),
        actp = str(actp),
        agg = int(agg),
        obsm = int(obsm),
        etatp = int(etatp),
        catv = int(catv),
        col = int(col),
        place = int(place),
        obs = int(obs),
        vma = int(vma),
        catu = int(catu),
        manv = int(manv),
    )

    # Préparation des données pour la prédiction    
    input_features = [
        data.long,
        data.lat,
        data.secu1,
        data.locp,
        data.actp,
        data.agg,
        data.obsm,
        data.etatp,
        data.catv,
        data.col,
        data.place,
        data.obs,
        data.vma,
        data.catu,
        data.manv,
    ]

    # Création du DataFrame à partir des données d'entrée
    df = pd.DataFrame([input_features], columns=['long', 'lat', 'secu1', 'locp', 'actp', 'agg', 'obsm', 'etatp', 'catv', 'col', 'place', 'obs', 'vma', 'catu', 'manv'])

    # Encodage des variables catégorielles
    categorical_columns = df.select_dtypes(include=['object'])
    numerical_columns = df.select_dtypes(exclude=['object'])
    encoded_data = encoder.transform(categorical_columns)
    df = pd.concat([numerical_columns, encoded_data], axis=1)

    # Prédiction
    to_predict = np.array(df)
    output = model.predict(to_predict)[0]
    df["grav"] = output

    # Enregistrement de la prédiction
    json_data = df.to_json(orient='records')
    json_data = json.loads(json_data)
    supabase.table("data_prediction").insert(json_data).execute()

    # resultat
    if (int(output)== 0):
        result = "Non Grave, vehicule leger a prendre"
    elif (int(output)== 1):
        result = "Grave, il faut prendre la grande échelle"
    else :
        result = "Il manque des informations"
    return templates.TemplateResponse("pred.html", {"request": request, "resultat": result})

# Route pour page : reel
@app.get("/reel")
async def sauvegarder(request: Request, username: Annotated[Union[str, None], Cookie()] = None, password: Annotated[Union[str, None], Cookie()] = None, long: str = "string", lat: str = "string", secu1: str = "", locp: str = "", actp: str = "string", agg: str = "", obsm: str = "", etatp: str = "", catv: str = "", col: str = "", place: str = "", obs: str = "", vma: str = "", catu: str = "", manv: str = "", grav: str = ""):
    if (username == None or password == None):
        return RedirectResponse(url="/")
    user = supabase.table("data_users").select("*").eq("username", username).execute()
    user2 = user.data[0]
    if (user2["password"] != password):
        return RedirectResponse(url="/")
    if (user2["role"] != "admin" and user2["role"] != "user"):
        return templates.TemplateResponse("reel.html", {"request": request, "resultat": "Vous n'avez pas les droits pour modifier un utilisateur"})

    if (not place.isdigit() or not vma.isdigit()):
        return templates.TemplateResponse("reel.html", {"request": request, "resultat": "Missing parameter(s)"})

    jsonBody = InputDataReel(
        long = str(long),
        lat = str(lat),
        secu1 = int(secu1),
        locp = int(locp),
        actp = str(actp),
        agg = int(agg),
        obsm = int(obsm),
        etatp = int(etatp),
        catv = int(catv),
        col = int(col),
        place = int(place),
        obs = int(obs),
        vma = int(vma),
        catu = int(catu),
        manv = int(manv),
        grav = int(grav),
    )

	# Modification des valeurs
    res = supabase.table("data_live").insert({
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