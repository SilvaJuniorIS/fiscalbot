from sqlalchemy import select

from app.core.config import Settings, settings
from app.core.security import verify_password
from app.models.user import User
from scripts import bootstrap_admin


def test_seed_is_not_exposed(client):
    assert client.get("/run-seed").status_code == 404


def test_neon_url_uses_installed_driver():
    config = Settings(
        _env_file=None, database_url="postgresql://user:pass@localhost/db?sslmode=require"
    )
    assert config.database_url == "postgresql+psycopg://user:pass@localhost/db?sslmode=require"


def test_bootstrap_preserves_existing_admin(db_session, monkeypatch):
    from contextlib import nullcontext

    monkeypatch.setattr(settings, "secret_key", "a" * 40)
    monkeypatch.setattr(settings, "admin_password", "unique-test-password")
    monkeypatch.setattr(bootstrap_admin, "SessionLocal", lambda: nullcontext(db_session))
    bootstrap_admin.bootstrap_admin()
    admin = db_session.scalar(select(User).where(User.email == settings.admin_email))
    assert admin.role == "admin"
    assert verify_password("unique-test-password", admin.hashed_password)
    monkeypatch.setattr(settings, "admin_password", "a-different-password")
    bootstrap_admin.bootstrap_admin()
    db_session.refresh(admin)
    assert verify_password("unique-test-password", admin.hashed_password)


def test_import_without_redis(client, auth_headers, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "celery_enabled", False)
    monkeypatch.setattr(settings, "storage_path", str(tmp_path))
    content = (
        "numero,orgao,objeto,valor,inicio,termino,secretaria,fornecedor,cnpj\n"
        "FREE-1,Prefeitura,Teste,100,2026-01-01,2027-01-01,Saude,Fornecedor,12345678000190\n"
    )
    response = client.post(
        "/api/v1/importacao/contratos",
        headers=auth_headers,
        files={"file": ("contratos.csv", content, "text/csv")},
    )
    assert response.status_code == 202
    task = response.json()
    assert task["status"] == "success"
    result = client.get(f"/api/v1/importacao/contratos/{task['task_id']}", headers=auth_headers)
    assert result.status_code == 200
    assert result.json()["resultado"]["importados"] == 1
    assert (
        client.get("/api/v1/importacao/contratos/unknown", headers=auth_headers).status_code == 404
    )
