from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
import json

def test_create_claim_detection_predicts(client: TestClient):
    """
    Test create claim detection predicts success
    """
    test_data = {"text": "test claim 1. test claim 2. test claim 3."}
    response = client.post(
        "/claim_detection/insert_claims",
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
        json=test_data,
    )
    res_data = response.json()
    assert response.status_code == 200
    assert isinstance(res_data, list)
    assert len(res_data) == 3
    assert all(item['text'] in ['test claim 1', 'test claim 2', 'test claim 3'] for item in res_data)

def test_create_claim_detection_predicts_fail1(client: TestClient):
    """
    Test create claim detection predicts fail:
    Case 1: required field is missing. Expected Validation Error with error code 422
    """
    response = client.post(
        "/claim_detection/insert_claims",
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
        json={"something_very_wrong": ""},
    )
    res_data = response.json()  
    assert response.status_code == 422
    assert isinstance(res_data, dict)
    assert "detail" in res_data
    assert res_data["detail"][0]["type"] == "missing"
    assert res_data["detail"][0]["msg"] == "Field required"
    
def test_create_claim_detection_predicts_fail2(client: TestClient):
    """
    Test create claim detection predicts fail:
    Case 2: empty text field. Expected Validation Error with error code 422
    """
    response = client.post(
        "/claim_detection/insert_claims",
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
        json={"text": ""},
    )
    res_data = response.json()  
    assert response.status_code == 422
    assert isinstance(res_data, dict)
    assert "detail" in res_data
    assert res_data["detail"][0]["type"] == "string_too_short"
    assert res_data["detail"][0]["msg"] == "String should have at least 1 character"

def test_create_claim_detection_predicts_fail3(client: TestClient):
    """
    Test create claim detection predicts fail:
    Case 3: insert_claims is duplicated, the expected result should be error
    """
    for i in range(1,4):
        get_response = client.get(f"claim_detection?claim_id={i}")
        assert get_response.status_code == 200
        assert isinstance(get_response.json(), list)
    test_data = {"text": "test claim 1. test claim 2. test claim 3."}
    response = client.post(
        "/claim_detection/insert_claims",
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
        json=test_data,
    )
    res_data = response.json()
    assert response.status_code == 500
    assert isinstance(res_data, dict)
    assert res_data["detail"] == "Failed to insert claims: All claims are already in the database. No claims inserted."

def test_update_claim_detection_predicts_success(client: TestClient):
    """
    Test update claim detection predicts success
    """
    
    test_data = {
        "text": "Test claim 1 ",
        "label": False
    }
    response = client.put(
        "/claim_detection/1",
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
        json=test_data,
    )
    res_data = response.json()
    assert response.status_code == 200
    assert isinstance(res_data, dict)
    assert res_data["message"] == "Claim at ID=1 updated successfully"

def test_update_claim_detection_predicts_not_found(client: TestClient):
    """
    Test update claim detection predicts not found:
    Case 1: claim_id is not found, the expected result should be error 404
    """
    test_data = {
        "text": "Test claim 1 ",
        "label": False
    }
    response = client.put("/claim_detection/10",
        headers={"accept": "application/json",
                 "Content-Type": "application/json"},
        json=test_data,
    )
    res_data = response.json()
    assert response.status_code == 404
    assert isinstance(res_data, dict)
    assert res_data["detail"] == "Claim ID=10 not found"
    
def test_delete_claim_detection_predicts_success(client: TestClient):
    """
    Test delete claim detection predicts success
    """
    response = client.delete("/claim_detection/1")
    res_data = response.json()
    assert response.status_code == 200
    assert isinstance(res_data, dict)
    assert res_data["message"] == "Claim at ID=1 deleted successfully"
    
def test_delete_claim_detection_predicts_not_found(client: TestClient):
    """
    Test delete claim detection predicts not found:
    Case 1: claim_id is not found, the expected result should be error 404
    """
    response = client.delete("/claim_detection/1")
    res_data = response.json()
    assert response.status_code == 404  
    assert isinstance(res_data, dict)
    assert res_data["detail"] == "Claim ID=1 not found"
    