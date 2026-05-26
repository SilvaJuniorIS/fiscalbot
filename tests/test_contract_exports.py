from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.contract import Contract


def _create_contract(db_session: Session) -> Contract:
    contract = Contract(
        status="ativo",
        numero_contrato="18/23",
        fornecedor="ESPACO 2 TECNOLOGIA",
        cnpj="09066243000105",
        secretaria="ADMINISTRACAO",
        fiscal="Fabio Eduardo Garcia",
        objeto="Locacao de equipamentos multifuncionais.",
        fim_vigencia=date(2026, 5, 23),
        dias_para_vencimento=30,
        valor_total=Decimal("248220.00"),
    )
    db_session.add(contract)
    db_session.commit()
    return contract


def test_export_contracts_csv(
    client: TestClient, db_session: Session, auth_headers: dict[str, str]
) -> None:
    _create_contract(db_session)

    response = client.get("/api/v1/contracts/export/csv", headers=auth_headers)

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "18/23" in response.text
    assert "ESPACO 2 TECNOLOGIA" in response.text


def test_export_contracts_xlsx(
    client: TestClient, db_session: Session, auth_headers: dict[str, str]
) -> None:
    _create_contract(db_session)

    response = client.get("/api/v1/contracts/export/xlsx", headers=auth_headers)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert response.content.startswith(b"PK")


def test_export_contracts_pdf(
    client: TestClient, db_session: Session, auth_headers: dict[str, str]
) -> None:
    _create_contract(db_session)

    response = client.get("/api/v1/contracts/export/pdf", headers=auth_headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
