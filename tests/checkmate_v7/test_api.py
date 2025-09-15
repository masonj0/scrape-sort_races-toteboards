import pytest
from fastapi.testclient import TestClient
from src.checkmate_v7.api import app

client = TestClient(app)

def test_read_root():
    """Tests the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Checkmate V7 API is running."}

def test_get_health():
    """Tests the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
