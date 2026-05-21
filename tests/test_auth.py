from datetime import timedelta

from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.models.user import User

TEST_PASSWORD = "fiscalbot123"


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_login_with_valid_credentials(client: TestClient, admin_user: User) -> None:
    token = _login(client, admin_user.email, TEST_PASSWORD)

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == admin_user.email


def test_login_with_invalid_credentials(client: TestClient, admin_user: User) -> None:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": admin_user.email, "password": "senha-errada"},
    )

    assert response.status_code == 401


def test_access_without_token(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_access_with_expired_token(client: TestClient, admin_user: User) -> None:
    expired_token = create_access_token(
        admin_user.email,
        expires_delta=timedelta(seconds=-1),
    )
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
