from fastapi.testclient import TestClient
import pytest
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/root")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, bienvenue sur l'API graPYte"}

def test_auth_cookie():
    response = client.get("/")
    assert response.status_code == 200

def test_logout():
    response = client.get("/logout")
    assert response.status_code == 200

def test_index():
    response = client.get("/index")
    assert response.status_code == 200

def test_role():
    response = client.get("/role")
    assert response.status_code == 200

def test_modif():
    response = client.get("/modif")
    assert response.status_code == 200

def test_create():
    response = client.get("/create")
    assert response.status_code == 200

def test_prediction():
    response = client.get("/prediction")
    assert response.status_code == 200

def test_reel():
    response = client.get("/reel")
    assert response.status_code == 200
