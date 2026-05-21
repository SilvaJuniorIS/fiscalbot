from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.contrato import Contrato, ContratoStatus
from app.models.fornecedor import Fornecedor
from app.models.secretaria import Secretaria
from app.models.user import User, UserRole
from app.services import alerta_service

from tests.conftest import TEST_PASSWORD


def _auth(client: TestClient, email: str) -> dict[str, str]:
    r = client.post("/api/v1/auth/login", data={"username": email, "password": TEST_PASSWORD})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _seed(db: Session) -> tuple[Contrato, User]:
    sec = Secretaria(nome="Saude", sigla="SMS", is_active=True)
    forn = Fornecedor(razao_social="F", cnpj="11.222.333/0001-81", is_active=True)
    db.add_all([sec, forn])
    db.flush()
    admin = User(
        nome="Admin",
        email="admin-alertas@example.com",
        hashed_password=hash_password(TEST_PASSWORD),
        role=UserRole.admin.value,
        is_active=True,
    )
    db.add(admin)
    db.flush()
    hoje = date.today()
    contrato = Contrato(
        numero="ALERT/01",
        orgao="Pref",
        objeto="Teste",
        valor=1000,
        inicio=hoje - timedelta(days=30),
        termino=hoje + timedelta(days=25),
        status=ContratoStatus.ativo.value,
        secretaria_id=sec.id,
        fornecedor_id=forn.id,
        gestor_responsavel_id=admin.id,
    )
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    return contrato, admin


def test_gera_alerta_contrato_25_dias(client: TestClient, db_session: Session) -> None:
    contrato, _ = _seed(db_session)
    alerta = alerta_service.gerar_para_contrato_em_dias(db_session, contrato, 25)
    assert alerta is not None
    assert "25 dias" in alerta.titulo


def test_nao_duplica_alerta(client: TestClient, db_session: Session) -> None:
    contrato, _ = _seed(db_session)
    first = alerta_service.gerar_para_contrato_em_dias(db_session, contrato, 30)
    second = alerta_service.gerar_para_contrato_em_dias(db_session, contrato, 30)
    assert first is not None
    assert second is None


def test_marcar_alerta_como_lido(client: TestClient, db_session: Session) -> None:
    contrato, admin = _seed(db_session)
    alerta = alerta_service.gerar_para_contrato_em_dias(db_session, contrato, 30)
    assert alerta is not None
    headers = _auth(client, admin.email)
    response = client.put(f"/api/v1/alertas/{alerta.id}/lido", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "lido"
