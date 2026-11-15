import os
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    from main import app
    return TestClient(app)

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200

def test_docs(client):
    assert client.get("/openapi.json").status_code == 200

def test_no_api_key(client):
    if os.getenv("CARGOHUB_REQUIRE_API_KEY", "true").lower() == "true":
        assert client.get("/api/v1/warehouses").status_code == 401

def test_invalid_api_key(client):
    if os.getenv("CARGOHUB_REQUIRE_API_KEY", "true").lower() == "true":
        assert client.get("/api/v1/warehouses", headers={"API_KEY":"invalid"}).status_code == 401
