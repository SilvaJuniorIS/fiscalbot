"""Read-time classification: never rewrite original dates or administrative status."""

from datetime import date, timedelta

from sqlalchemy import case, func, or_

from app.models.contract import Contract


def situation_expression(today: date | None = None):
    today = today or date.today()
    return case(
        (
            func.lower(Contract.status).in_(["encerrado", "suspenso", "cancelado"]),
            func.lower(Contract.status),
        ),
        (Contract.fim_vigencia.is_(None), "sem_vencimento"),
        (Contract.fim_vigencia < today, "vencido"),
        (Contract.fim_vigencia <= today + timedelta(days=30), "vencendo"),
        else_="ativo",
    )


def missing_expression():
    return or_(
        Contract.numero_contrato.is_(None),
        func.trim(Contract.numero_contrato) == "",
        Contract.fornecedor.is_(None),
        func.trim(Contract.fornecedor) == "",
        Contract.secretaria.is_(None),
        func.trim(Contract.secretaria) == "",
        Contract.objeto.is_(None),
        func.trim(Contract.objeto) == "",
        Contract.fim_vigencia.is_(None),
        Contract.valor_total.is_(None),
        Contract.fiscal.is_(None),
        func.trim(Contract.fiscal) == "",
        Contract.gestor.is_(None),
        func.trim(Contract.gestor) == "",
    )
