"""Smoke tests for critical API availability."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.smoke
def test_smoke_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["service"] == "SyncUs Backend API"


@pytest.mark.smoke
def test_smoke_root_endpoint(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["docs"] == "/docs"
    assert payload["health"] == "/health"


@pytest.mark.smoke
def test_smoke_docs_endpoint(client: TestClient) -> None:
    response = client.get("/docs")

    assert response.status_code == 200


@pytest.mark.smoke
def test_smoke_auth_login_route_exists(client: TestClient) -> None:
    response = client.post(
        "/accounts/auth/login",
        json={"email": "smoke@example.com", "password": "invalid"},
    )

    # Route should exist and return an auth-related error, not 404.
    assert response.status_code in {400, 401, 422}
