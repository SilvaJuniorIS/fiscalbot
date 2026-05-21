from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.contrato import Contrato, ContratoStatus
from app.models.fornecedor import Fornecedor
from app.models.log_auditoria import LogAuditoria
from app.models.secretaria import Secretaria
from app.models.user import User, UserRole

from tests.conftest import TEST_PASSWORD


def _auth(client: TestClient, email: str) -> dict[str, str]:
    r = client.post("/api/v1/auth/login", data={"username": email, "password": TEST_PASSWORD})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _seed_users(db: Session) -> tuple[User, User]:
    sec = Secretaria(nome="SMA", sigla="SMA", is_active=True)
    forn = Fornecedor(razao_social="F", cnpj="11.222.333/0001-81", is_active=True)
    db.add_all([sec, forn])
    db.flush()
    pw = hash_password(TEST_PASSWORD)
    admin = User(
        nome="Admin",
        email="admin-audit@example.com",
        hashed_password=pw,
        role=UserRole.admin.value,
        is_active=True,
    )
    gestor = User(
        nome="Gestor",
        email="gestor-audit@example.com",
        hashed_password=pw,
        role=UserRole.gestor.value,
        secretaria_id=sec.id,
        is_active=True,
    )
    db.add_all([admin, gestor])
    db.commit()
    return admin, gestor


def test_criar_contrato_gera_log(client: TestClient, db_session: Session) -> None:
    admin, _ = _seed_users(db_session)
    sec = db_session.scalar(select(Secretaria))
    forn = db_session.scalar(select(Fornecedor))
    headers = _auth(client, admin.email)
    hoje = date.today()
    response = client.post(
        "/api/v1/contratos",
        headers=headers,
        json={
            "numero": "AUD/01",
            "orgao": "Pref",
            "objeto": "Auditoria",
            "valor": "1000.00",
            "inicio": hoje.isoformat(),
            "termino": (hoje + timedelta(days=90)).isoformat(),
            "secretaria_id": sec.id,
            "fornecedor_id": forn.id,
        },
    )
    assert response.status_code == 201
    contrato_id = response.json()["id"]
    log = db_session.scalar(
        select(LogAuditoria).where(
            LogAuditoria.entidade == "contratos",
            LogAuditoria.entidade_id == contrato_id,
            LogAuditoria.acao == "criar",
        )
    )
    assert log is not None
    assert log.depois is not None


def test_auditoria_403_nao_admin(client: TestClient, db_session: Session) -> None:
    _, gestor = _seed_users(db_session)
    headers = _auth(client, gestor.email)
    response = client.get("/api/v1/auditoria", headers=headers)
    assert response.status_code == 403


def test_editar_contrato_gera_log_com_antes(client: TestClient, db_session: Session) -> None:
    admin, _ = _seed_users(db_session)
    sec = db_session.scalar(select(Secretaria))
    forn = db_session.scalar(select(Fornecedor))
    headers = _auth(client, admin.email)
    hoje = date.today()
    created = client.post(
        "/api/v1/contratos",
        headers=headers,
        json={
            "numero": "AUD/02",
            "orgao": "Pref",
            "objeto": "Antes",
            "valor": "1000.00",
            "inicio": hoje.isoformat(),
            "termino": (hoje + timedelta(days=120)).isoformat(),
            "secretaria_id": sec.id,
            "fornecedor_id": forn.id,
            "gestor_responsavel_id": admin.id,
        },
    )
    contrato_id = created.json()["id"]
    client.put(
        f"/api/v1/contratos/{contrato_id}",
        headers=headers,
        json={"objeto": "Depois"},
    )
    log = db_session.scalar(
        select(LogAuditoria).where(
            LogAuditoria.entidade == "contratos",
            LogAuditoria.entidade_id == contrato_id,
            LogAuditoria.acao == "atualizar",
        )
    )
    assert log is not None
    assert log.antes is not None
    assert log.depois is not None
