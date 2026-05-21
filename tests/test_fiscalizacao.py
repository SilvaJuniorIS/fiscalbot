from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.contrato import Contrato, ContratoStatus
from app.models.fornecedor import Fornecedor
from app.models.secretaria import Secretaria
from app.models.user import User, UserRole

from tests.conftest import TEST_PASSWORD


def _auth(client: TestClient, email: str) -> dict[str, str]:
    r = client.post("/api/v1/auth/login", data={"username": email, "password": TEST_PASSWORD})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _seed(db: Session) -> tuple[int, int, User, User]:
    saude = Secretaria(nome="Saude", sigla="SMS", is_active=True)
    educacao = Secretaria(nome="Educacao", sigla="SME", is_active=True)
    forn = Fornecedor(razao_social="F", cnpj="11.222.333/0001-81", is_active=True)
    db.add_all([saude, educacao, forn])
    db.flush()
    pw = hash_password(TEST_PASSWORD)
    fiscal_saude = User(
        nome="Fiscal Saude",
        email="fiscal-saude@example.com",
        hashed_password=pw,
        role=UserRole.fiscal.value,
        secretaria_id=saude.id,
        is_active=True,
    )
    fiscal_educacao = User(
        nome="Fiscal Educ",
        email="fiscal-educ@example.com",
        hashed_password=pw,
        role=UserRole.fiscal.value,
        secretaria_id=educacao.id,
        is_active=True,
    )
    gestor = User(
        nome="Gestor",
        email="gestor-fisc@example.com",
        hashed_password=pw,
        role=UserRole.gestor.value,
        secretaria_id=saude.id,
        is_active=True,
    )
    db.add_all([fiscal_saude, fiscal_educacao, gestor])
    db.flush()
    hoje = date.today()
    c_saude = Contrato(
        numero="FISC-S",
        orgao="Pref",
        objeto="Saude",
        valor=1000,
        inicio=hoje,
        termino=hoje + timedelta(days=60),
        status=ContratoStatus.ativo.value,
        secretaria_id=saude.id,
        fornecedor_id=forn.id,
        fiscal_responsavel_id=fiscal_saude.id,
        gestor_responsavel_id=gestor.id,
    )
    c_educ = Contrato(
        numero="FISC-E",
        orgao="Pref",
        objeto="Educ",
        valor=1000,
        inicio=hoje,
        termino=hoje + timedelta(days=60),
        status=ContratoStatus.ativo.value,
        secretaria_id=educacao.id,
        fornecedor_id=forn.id,
    )
    db.add_all([c_saude, c_educ])
    db.commit()
    return c_saude.id, c_educ.id, fiscal_saude, gestor


def test_fiscal_registra_ocorrencia(client: TestClient, db_session: Session) -> None:
    contrato_id, _, fiscal, _ = _seed(db_session)
    headers = _auth(client, fiscal.email)
    response = client.post(
        f"/api/v1/fiscalizacao/contratos/{contrato_id}/ocorrencias",
        headers=headers,
        json={
            "titulo": "Vistoria",
            "descricao": "Tudo conforme",
            "tipo": "vistoria",
        },
    )
    assert response.status_code == 201


def test_fiscal_nao_registra_outra_secretaria(client: TestClient, db_session: Session) -> None:
    _, contrato_educ, fiscal_saude, _ = _seed(db_session)
    headers = _auth(client, fiscal_saude.email)
    response = client.post(
        f"/api/v1/fiscalizacao/contratos/{contrato_educ}/ocorrencias",
        headers=headers,
        json={"titulo": "X", "descricao": "Y", "tipo": "vistoria"},
    )
    assert response.status_code == 403


def test_gestor_atualiza_status(client: TestClient, db_session: Session) -> None:
    contrato_id, _, fiscal, gestor = _seed(db_session)
    headers_fiscal = _auth(client, fiscal.email)
    created = client.post(
        f"/api/v1/fiscalizacao/contratos/{contrato_id}/ocorrencias",
        headers=headers_fiscal,
        json={"titulo": "Pendencia", "descricao": "Ajustar", "tipo": "pendencia"},
    )
    ocorrencia_id = created.json()["id"]
    headers_gestor = _auth(client, gestor.email)
    response = client.put(
        f"/api/v1/fiscalizacao/ocorrencias/{ocorrencia_id}",
        headers=headers_gestor,
        json={"status": "concluida"},
    )
    assert response.status_code == 200
    assert response.json()["status"] in {"resolvida", "concluida"}
