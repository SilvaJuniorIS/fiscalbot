from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "FiscalBot"}


def test_dashboard_page_loads() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "FiscalBot Dashboard" in response.text
    assert "/api/v1/dashboard" in response.text


def test_dashboard_endpoint_returns_cards_without_database() -> None:
    response = client.get("/api/v1/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert "cards" in payload
    assert "total_contratos" in payload["cards"]
