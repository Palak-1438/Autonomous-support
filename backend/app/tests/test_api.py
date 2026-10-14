import pytest
from fastapi.testclient import TestClient
from app.api import app
from app.config import get_settings

client = TestClient(app)

def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert data["domains"] > 0
    assert data["llm_mode"] == "mock"

def test_domain_registry_loaded():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["domains"] >= 3

def test_mock_mode_no_api_key_required():
    settings = get_settings()
    assert settings.llm_mode == "mock"

    conv_response = client.post("/api/conversations", json={"domain_hint": "ecommerce"})
    assert conv_response.status_code == 200
    conv_id = conv_response.json()["id"]

    msg_response = client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"content": "I need help with my order"}
    )
    assert msg_response.status_code == 200
    data = msg_response.json()
    assert data["role"] == "assistant"
    assert data["supervisor"]["outcome"] == "APPROVE"
    assert "mock response" in data["content"].lower()

def test_unsupported_request_escalates():
    conv_response = client.post("/api/conversations", json={"domain_hint": "ecommerce"})
    assert conv_response.status_code == 200
    conv_id = conv_response.json()["id"]

    msg_response = client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"content": "I have an unknown issue that I need to escalate"}
    )
    assert msg_response.status_code == 200
    data = msg_response.json()

    assert data["role"] == "assistant"
    assert data["classification"]["domain"] == "unknown"

    # We escalated directly after route, so supervisor isn't run
    assert data.get("supervisor") is None

    assert "escalated" in data["content"].lower()

def test_root_returns_200():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
