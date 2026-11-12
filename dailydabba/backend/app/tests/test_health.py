"""Verify the Phase 1 HTTP contract and automatic API documentation."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def client():
    """Run startup/shutdown as the real server would, without external services."""
    with TestClient(create_app(Settings(_env_file=None))) as test_client:
        yield test_client


def test_health_returns_expected_public_contract(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_documents_health_response(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    operation = response.json()["paths"]["/api/v1/health"]["get"]
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema["$ref"] == "#/components/schemas/HealthResponse"


def test_swagger_documentation_is_served(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text


def test_unknown_endpoint_returns_404(client: TestClient) -> None:
    assert client.get("/api/v1/unknown").status_code == 404
