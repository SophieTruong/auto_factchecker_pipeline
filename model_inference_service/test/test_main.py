from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app

def test_predict(client: TestClient):
    response = client.post(
        "/predict",
        json=["Test sentence"]
    )
    print(response.json())
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert "timestamp" in response.json()[0].keys()
    assert "claim_label" in response.json()[0].keys()

def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
