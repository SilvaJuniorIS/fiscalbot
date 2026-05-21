import io
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


def _seed(db: Session) -> tuple[int, User]:
    sec = Secretaria(nome="Saude", sigla="SMS", is_active=True)
    forn = Fornecedor(razao_social="F", cnpj="11.222.333/0001-81", is_active=True)
    db.add_all([sec, forn])
    db.flush()
    user = User(
        nome="Gestor",
        email="gestor-doc@example.com",
        hashed_password=hash_password(TEST_PASSWORD),
        role=UserRole.gestor.value,
        secretaria_id=sec.id,
        is_active=True,
    )
    db.add(user)
    db.flush()
    hoje = date.today()
    c = Contrato(
        numero="DOC/01",
        orgao="Pref",
        objeto="Teste doc",
        valor=1000,
        inicio=hoje,
        termino=hoje + timedelta(days=90),
        status=ContratoStatus.ativo.value,
        secretaria_id=sec.id,
        fornecedor_id=forn.id,
        gestor_responsavel_id=user.id,
    )
    db.add(c)
    db.commit()
    return c.id, user


def test_upload_pdf_valido(client: TestClient, db_session: Session, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    from app.core.config import get_settings

    get_settings.cache_clear()
    contrato_id, user = _seed(db_session)
    headers = _auth(client, user.email)
    files = {"file": ("contrato.pdf", io.BytesIO(b"%PDF-1.4 test"), "application/pdf")}
    data = {"tipo": "contrato", "versao": "1"}
    response = client.post(
        f"/api/v1/contratos/{contrato_id}/documentos",
        headers=headers,
        files=files,
        data=data,
    )
    assert response.status_code == 201
    assert response.json()["nome_arquivo"] == "contrato.pdf"


def test_rejeita_extensao_invalida(client: TestClient, db_session: Session, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    from app.core.config import get_settings

    get_settings.cache_clear()
    contrato_id, user = _seed(db_session)
    headers = _auth(client, user.email)
    files = {"file": ("virus.exe", io.BytesIO(b"MZ"), "application/octet-stream")}
    response = client.post(
        f"/api/v1/contratos/{contrato_id}/documentos",
        headers=headers,
        files=files,
        data={"tipo": "contrato"},
    )
    assert response.status_code == 400


def test_download_retorna_bytes(client: TestClient, db_session: Session, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    from app.core.config import get_settings

    get_settings.cache_clear()
    contrato_id, user = _seed(db_session)
    headers = _auth(client, user.email)
    content = b"%PDF-download-test"
    files = {"file": ("doc.pdf", io.BytesIO(content), "application/pdf")}
    created = client.post(
        f"/api/v1/contratos/{contrato_id}/documentos",
        headers=headers,
        files=files,
        data={"tipo": "contrato"},
    )
    anexo_id = created.json()["id"]
    download = client.get(f"/api/v1/documentos/{anexo_id}/download", headers=headers)
    assert download.status_code == 200
    assert download.content == content
