from datetime import date, timedelta
from io import BytesIO

from openpyxl import Workbook

from app.models.contract import Contract


def test_dashboard_shows_imported_contracts(client, auth_headers):
    today = date.today()
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Contrato", "Fornecedor", "Objeto", "Secretaria", "Vencimento", "Valor"])
    sheet.append(["TEST-1", "Empresa A", "Servico A", "Saude", today + timedelta(days=10), 100])
    sheet.append(["ATA TEST-2", "Empresa B", "Servico B", "Obras", today - timedelta(days=1), 200])
    content = BytesIO()
    workbook.save(content)
    response = client.post(
        "/api/v1/contracts/import",
        headers=auth_headers,
        files={
            "file": (
                "teste.xlsx",
                content.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert response.status_code == 201
    assert response.json()["importados"] == 2
    response = client.get("/api/v1/contracts/dashboard", headers=auth_headers)
    assert response.status_code == 200
    dashboard = response.json()
    assert dashboard["contratos_ativos"] == 1
    assert dashboard["vencendo_em_30"] == 1
    assert dashboard["vencendo_em_15"] == 1
    assert dashboard["vencidos"] == 1
    assert float(dashboard["valor_total_contratado"]) == 300
    assert {item["nome"]: item["total"] for item in dashboard["por_secretaria"]} == {
        "Saude": 1,
        "Obras": 1,
    }
    assert sum(item["total"] for item in dashboard["por_status"]) == 2
    assert {item["numero_contrato"] for item in dashboard["ultimos_contratos"]} == {
        "TEST-1",
        "ATA TEST-2",
    }


def test_dashboard_uses_current_dates_not_cached_days(client, auth_headers, db_session):
    db_session.add(
        Contract(
            numero_contrato="STALE",
            status="ativo",
            fim_vigencia=date.today() - timedelta(days=1),
            dias_para_vencimento=90,
        )
    )
    db_session.commit()
    dashboard = client.get("/api/v1/contracts/dashboard", headers=auth_headers).json()
    assert dashboard["vencidos"] == 1
    assert dashboard["contratos_ativos"] == 0
    assert dashboard["vencendo_em_30"] == 0


def test_dashboard_requires_authentication(client):
    assert client.get("/api/v1/contracts/dashboard").status_code == 401
