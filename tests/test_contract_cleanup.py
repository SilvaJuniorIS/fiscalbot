from datetime import date, timedelta
from io import BytesIO

from openpyxl import Workbook
from sqlalchemy import func, select

from app.models.contract import Contract, ContractImportLog


def spreadsheet(rows):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(
        [
            "Tipo",
            "Contrato",
            "Fornecedor",
            "Secretaria",
            "Objeto",
            "Vencimento",
            "Valor",
            "Fiscal",
            "Gestor",
        ]
    )
    for row in rows:
        sheet.append(row)
    content = BytesIO()
    workbook.save(content)
    return {
        "file": (
            "dados.xlsx",
            content.getvalue(),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }


def test_preview_dedup_and_repeat_import(client, auth_headers, db_session):
    rows = [
        [
            "contrato",
            "01/26",
            "Fornecedor A",
            "Saude",
            "Material",
            date.today(),
            100,
            "Maria",
            "Joao",
        ],
        [
            "contrato",
            "01/26",
            "Fornecedor A",
            "Saude",
            "Material",
            date.today(),
            100,
            "Maria",
            "Joao",
        ],
        ["ata", "01/26", "Fornecedor A", "Saude", "Material", date.today(), 100, "Maria", "Joao"],
    ]
    response = client.post(
        "/api/v1/contracts/import/preview", headers=auth_headers, files=spreadsheet(rows)
    )
    assert response.status_code == 200
    preview = response.json()
    assert preview["simulacao"] is True
    assert preview["importados"] == 2
    assert preview["duplicados"] == 1
    assert db_session.scalar(select(func.count(Contract.id))) == 0
    assert db_session.scalar(select(func.count(ContractImportLog.id))) == 0
    response = client.post(
        "/api/v1/contracts/import", headers=auth_headers, files=spreadsheet(rows)
    )
    assert response.status_code == 201
    assert response.json()["importados"] == 2
    response = client.post(
        "/api/v1/contracts/import", headers=auth_headers, files=spreadsheet(rows)
    )
    assert response.json()["importados"] == 0
    assert response.json()["duplicados"] == 3
    assert db_session.scalar(select(func.count(Contract.id))) == 2


def test_update_is_opt_in_and_preserves_blanks_and_status(client, auth_headers, db_session):
    contract = Contract(
        tipo="ata",
        numero_contrato="ATA 01/26",
        fornecedor="Empresa",
        secretaria="Saude",
        objeto="Original",
        valor_total=100,
        fiscal="Fiscal",
        gestor="Gestor",
        status="suspenso",
    )
    db_session.add(contract)
    db_session.commit()
    rows = [["ata", "01/26", "Empresa", "Saude", "Novo objeto", None, None, None, None]]
    ignored = client.post("/api/v1/contracts/import", headers=auth_headers, files=spreadsheet(rows))
    assert ignored.json()["ignorados"] == 1
    db_session.refresh(contract)
    assert contract.objeto == "Original"
    preview = client.post(
        "/api/v1/contracts/import/preview?modo=atualizar",
        headers=auth_headers,
        files=spreadsheet(rows),
    )
    assert preview.json()["atualizados"] == 1
    db_session.refresh(contract)
    assert contract.objeto == "Original"
    updated = client.post(
        "/api/v1/contracts/import?modo=atualizar", headers=auth_headers, files=spreadsheet(rows)
    )
    assert updated.json()["atualizados"] == 1
    db_session.refresh(contract)
    assert contract.objeto == "Novo objeto"
    assert contract.valor_total == 100
    assert contract.fiscal == "Fiscal"
    assert contract.status == "suspenso"


def test_ambiguous_existing_duplicates_are_preserved(client, auth_headers, db_session):
    for amount in (100, 200):
        db_session.add(
            Contract(
                tipo="contrato",
                numero_contrato="DUP",
                fornecedor="Empresa",
                secretaria="Obras",
                valor_total=amount,
            )
        )
    db_session.commit()
    response = client.post(
        "/api/v1/contracts/import?modo=atualizar",
        headers=auth_headers,
        files=spreadsheet(
            [["contrato", "DUP", "Empresa", "Obras", "Teste", None, 500, None, None]]
        ),
    )
    assert response.json()["atualizados"] == 0
    assert response.json()["ignorados"] == 1
    assert sorted(db_session.scalars(select(Contract.valor_total))) == [100, 200]
    dashboard = client.get("/api/v1/contracts/dashboard", headers=auth_headers).json()
    assert dashboard["grupos_duplicados"] == 1
    assert len(dashboard["duplicados"]) == 2


def test_dynamic_filters_and_missing_data(client, auth_headers, db_session):
    today = date.today()
    for kind, number, end, stored, status in [
        ("ata", "SOON", today + timedelta(days=5), -100, "ativo"),
        ("contrato", "OLD", today - timedelta(days=5), 100, "ativo"),
        ("contrato", "STOP", today - timedelta(days=1), 100, "suspenso"),
    ]:
        db_session.add(
            Contract(
                tipo=kind,
                numero_contrato=number,
                fornecedor="Empresa",
                secretaria="Obras",
                objeto="Teste",
                fim_vigencia=end,
                dias_para_vencimento=stored,
                valor_total=0,
                gestor="Joao",
                fiscal="Maria",
                status=status,
            )
        )
    db_session.add(Contract(numero_contrato="INCOMPLETE", fornecedor="Empresa", status="ativo"))
    db_session.commit()
    soon = client.get("/api/v1/contracts?vencendo_em_30=true&tipo=ata", headers=auth_headers).json()
    assert soon["total"] == 1
    assert soon["items"][0]["numero_contrato"] == "SOON"
    assert soon["items"][0]["dias_para_vencimento"] == 5
    assert soon["items"][0]["situacao"] == "vencendo"
    assert soon["items"][0]["dados_pendentes"] == []  # zero is valid, not missing
    expired = client.get("/api/v1/contracts?situacao=vencido", headers=auth_headers).json()
    assert [item["numero_contrato"] for item in expired["items"]] == ["OLD"]
    missing = client.get("/api/v1/contracts?incompletos=true", headers=auth_headers).json()
    assert missing["total"] == 1
    assert missing["items"][0]["numero_contrato"] == "INCOMPLETE"
    dashboard = client.get("/api/v1/contracts/dashboard", headers=auth_headers).json()
    assert dashboard["total_atas"] == 1
    assert dashboard["total_contratos"] == 3
    assert dashboard["dados_incompletos"] == 1
    assert dashboard["vencidos"] == 1
    assert dashboard["vencendo_em_30"] == 1
    assert {x["status"]: x["total"] for x in dashboard["por_status"]} == {
        "vencendo": 1,
        "vencido": 1,
        "suspenso": 1,
        "sem_vencimento": 1,
    }
    csv = client.get("/api/v1/contracts/export/csv?tipo=ata", headers=auth_headers).text
    assert "SOON" in csv and "OLD" not in csv
    assert "vencendo" in csv


def test_bad_rows_are_reported_without_inventing_values(client, auth_headers):
    rows = [
        ["ata", "A1", "Empresa", "Saude", "Teste", "data invalida", 100, None, None],
        ["ata", "A2", "Empresa", "Saude", "Teste", None, "valor desconhecido", None, None],
        ["ata", "A3", "Empresa", "Saude", "Teste", None, -10, None, None],
    ]
    response = client.post(
        "/api/v1/contracts/import/preview", headers=auth_headers, files=spreadsheet(rows)
    )
    result = response.json()
    assert result["erros"] == 3
    assert result["importados"] == 0
    assert [x["linha"] for x in result["detalhes_erro"]] == [2, 3, 4]


def test_clearing_expiration_returns_no_stale_days(client, auth_headers, db_session):
    contract = Contract(numero_contrato="CLEAR", fim_vigencia=date.today(), dias_para_vencimento=0)
    db_session.add(contract)
    db_session.commit()
    response = client.put(
        f"/api/v1/contracts/{contract.id}", headers=auth_headers, json={"fim_vigencia": None}
    )
    assert response.status_code == 200
    assert response.json()["dias_para_vencimento"] is None
    assert response.json()["situacao"] == "sem_vencimento"


def test_empty_dataset_reports_no_priorities(client, auth_headers):
    dashboard = client.get("/api/v1/contracts/dashboard", headers=auth_headers).json()
    assert dashboard["total_registros"] == 0
    assert dashboard["prioridades"] == []
    assert dashboard["duplicados"] == []


def test_preview_requires_login(client):
    assert client.post("/api/v1/contracts/import/preview", files=spreadsheet([])).status_code == 401


def test_cnpj_column_matches_formatted_existing_cnpj(client, auth_headers, db_session):
    db_session.add(
        Contract(
            tipo="ata",
            numero_contrato="ATA 77/26",
            fornecedor="Empresa",
            secretaria="Saude",
            cnpj="12.345.678/0001-90",
        )
    )
    db_session.commit()
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Tipo", "Contrato", "Fornecedor", "Secretaria", "Objeto", "CNPJ"])
    sheet.append(["ata", "77/26", "Empresa", "Saude", "Teste", "12345678000190"])
    content = BytesIO()
    workbook.save(content)
    response = client.post(
        "/api/v1/contracts/import",
        headers=auth_headers,
        files={"file": ("cnpj.xlsx", content.getvalue(), "application/octet-stream")},
    )
    assert response.status_code == 201
    assert response.json()["duplicados"] == 1
    assert response.json()["importados"] == 0


def test_unchanged_expiration_preserves_alert_flags(client, auth_headers, db_session):
    today = date.today()
    contract = Contract(numero_contrato="FLAGS", fim_vigencia=today, alerta_30=True)
    db_session.add(contract)
    db_session.commit()
    response = client.put(
        f"/api/v1/contracts/{contract.id}",
        headers=auth_headers,
        json={"fim_vigencia": today.isoformat(), "objeto": "Texto revisado"},
    )
    assert response.status_code == 200
    assert response.json()["alerta_30"] is True
