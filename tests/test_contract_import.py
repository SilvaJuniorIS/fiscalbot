from datetime import date
from decimal import Decimal

import pandas as pd

from app.services.contract_import_service import (
    calculate_days_to_expiration,
    extract_cnpj,
    extract_cpf,
    import_contracts,
    parse_date,
    parse_money,
)


def test_parse_date_supports_brazilian_short_and_long_formats():
    assert parse_date("23/05/2026") == date(2026, 5, 23)
    assert parse_date("24/05/25") == date(2025, 5, 24)
    assert parse_date("01/04/26") == date(2026, 4, 1)


def test_parse_money_pt_br():
    assert parse_money("R$ 248.220,00") == Decimal("248220.00")


def test_extract_cpf_returns_clean_name_and_digits():
    nome, cpf = extract_cpf("Felipe Vieira CPF 361.930.868-38")
    assert nome == "Felipe Vieira"
    assert cpf == "36193086838"


def test_extract_cnpj_returns_clean_supplier_and_digits():
    fornecedor, cnpj = extract_cnpj("LECASA LTDA CNPJ 21.091.888/0001-95")
    assert fornecedor == "LECASA LTDA"
    assert cnpj == "21091888000195"


def test_calculate_days_to_expiration():
    assert calculate_days_to_expiration(date(2026, 5, 30), today=date(2026, 5, 25)) == 5


def test_import_contracts_cleans_and_imports_xlsx(tmp_path):
    path = tmp_path / "contratos.xlsx"
    frame = pd.DataFrame(
        [
            {"Contrato": "CONTRATOS COM VENCIMENTO"},
            {
                "Nº Contrato": "123/2026",
                "Fornecedor": "LECASA LTDA CNPJ 21.091.888/0001-95",
                "Secretária": "Saude",
                "Gestor": "Felipe Vieira CPF 361.930.868-38",
                "Fiscal": "Maria Silva CPF 123.456.789-01",
                "Vigência": "24/05/25 a 23/05/26",
                "Valor Total": "R$ 248.220,00",
                "Objeto": "Servicos continuados",
            },
        ]
    )
    frame.to_excel(path, index=False)

    result = import_contracts(path)

    assert result["importados"] == 1
    assert result["ignorados"] == 1
    contract = result["contracts"][0]
    assert contract.numero_contrato == "123/2026"
    assert contract.fornecedor == "LECASA LTDA"
    assert contract.cnpj == "21091888000195"
    assert contract.gestor_cpf == "36193086838"
    assert contract.fiscal_cpf == "12345678901"
    assert contract.inicio_vigencia == date(2025, 5, 24)
    assert contract.fim_vigencia == date(2026, 5, 23)
    assert contract.valor_total == Decimal("248220.00")
