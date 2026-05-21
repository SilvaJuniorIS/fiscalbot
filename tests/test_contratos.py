from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.contrato import ContratoStatus
from app.models.fornecedor import Fornecedor
from app.models.secretaria import Secretaria
from app.models.user import User, UserRole
from app.services.contrato_service import calcular_status
from tests.conftest import TEST_PASSWORD


def _auth_headers(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _seed_base(db_session: Session) -> tuple[Secretaria, Secretaria, Fornecedor, User, User, User]:
    saude = Secretaria(nome="Saude", sigla="SMS", is_active=True)
    educacao = Secretaria(nome="Educacao", sigla="SME", is_active=True)
    fornecedor = Fornecedor(
        razao_social="Fornecedor Teste",
        cnpj="11.222.333/0001-81",
        is_active=True,
    )
    db_session.add_all([saude, educacao, fornecedor])
    db_session.flush()

    password_hash = hash_password(TEST_PASSWORD)
    admin = User(
        nome="Admin",
        email="admin-contratos@example.com",
        hashed_password=password_hash,
        role=UserRole.admin.value,
        is_active=True,
    )
    gestor_saude = User(
        nome="Gestor Saude",
        email="gestor-saude@example.com",
        hashed_password=password_hash,
        role=UserRole.gestor.value,
        secretaria_id=saude.id,
        is_active=True,
    )
    gestor_educacao = User(
        nome="Gestor Educacao",
        email="gestor-educacao@example.com",
        hashed_password=password_hash,
        role=UserRole.gestor.value,
        secretaria_id=educacao.id,
        is_active=True,
    )
    db_session.add_all([admin, gestor_saude, gestor_educacao])
    db_session.commit()
    return saude, educacao, fornecedor, admin, gestor_saude, gestor_educacao


def test_calcular_status_automatico() -> None:
    hoje = date(2026, 5, 19)
    assert calcular_status(hoje + timedelta(days=90), hoje) == ContratoStatus.ativo.value
    assert calcular_status(hoje + timedelta(days=45), hoje) == ContratoStatus.alerta.value
    assert calcular_status(hoje + timedelta(days=15), hoje) == ContratoStatus.critico.value
    assert calcular_status(hoje - timedelta(days=1), hoje) == ContratoStatus.encerrado.value


def test_criar_contrato(client: TestClient, db_session: Session) -> None:
    saude, _, fornecedor, _, gestor_saude, _ = _seed_base(db_session)
    headers = _auth_headers(client, gestor_saude.email)
    inicio = date.today()
    termino = inicio + timedelta(days=120)

    response = client.post(
        "/api/v1/contratos",
        headers=headers,
        json={
            "numero": "001/2026",
            "orgao": "Prefeitura",
            "objeto": "Objeto de teste",
            "valor": "10000.00",
            "inicio": inicio.isoformat(),
            "termino": termino.isoformat(),
            "secretaria_id": saude.id,
            "fornecedor_id": fornecedor.id,
            "gestor_responsavel_id": gestor_saude.id,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["numero"] == "001/2026"
    assert body["status"] == ContratoStatus.ativo.value
    assert body["secretaria"]["nome"] == "Saude"


def test_listar_contratos_com_filtro_status(client: TestClient, db_session: Session) -> None:
    saude, _, fornecedor, _, gestor_saude, _ = _seed_base(db_session)
    headers = _auth_headers(client, gestor_saude.email)
    hoje = date.today()

    client.post(
        "/api/v1/contratos",
        headers=headers,
        json={
            "numero": "002/2026",
            "orgao": "Prefeitura",
            "objeto": "Contrato critico",
            "valor": "5000.00",
            "inicio": hoje.isoformat(),
            "termino": (hoje + timedelta(days=10)).isoformat(),
            "secretaria_id": saude.id,
            "fornecedor_id": fornecedor.id,
            "gestor_responsavel_id": gestor_saude.id,
        },
    )

    response = client.get(
        "/api/v1/contratos",
        headers=headers,
        params={"status": ContratoStatus.critico.value},
    )

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["status"] == ContratoStatus.critico.value


def test_editar_contrato_outra_secretaria_retorna_403(
    client: TestClient, db_session: Session
) -> None:
    saude, educacao, fornecedor, _, gestor_saude, gestor_educacao = _seed_base(db_session)
    headers_saude = _auth_headers(client, gestor_saude.email)
    hoje = date.today()

    create_response = client.post(
        "/api/v1/contratos",
        headers=headers_saude,
        json={
            "numero": "003/2026",
            "orgao": "Prefeitura",
            "objeto": "Contrato da saude",
            "valor": "8000.00",
            "inicio": hoje.isoformat(),
            "termino": (hoje + timedelta(days=200)).isoformat(),
            "secretaria_id": saude.id,
            "fornecedor_id": fornecedor.id,
            "gestor_responsavel_id": gestor_saude.id,
        },
    )
    contrato_id = create_response.json()["id"]

    headers_educacao = _auth_headers(client, gestor_educacao.email)
    update_response = client.put(
        f"/api/v1/contratos/{contrato_id}",
        headers=headers_educacao,
        json={"objeto": "Tentativa de edicao indevida"},
    )

    assert update_response.status_code == 403
    assert educacao.id != saude.id
