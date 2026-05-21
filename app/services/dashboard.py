from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.alerta import Alerta
from app.models.contrato import Contrato
from app.models.fornecedor import Fornecedor
from app.models.ocorrencia import Ocorrencia
from app.models.secretaria import Secretaria


def _money(value: Decimal | int | None) -> float:
    if value is None:
        return 0.0
    return float(value)


def get_dashboard_data(db: Session) -> dict[str, Any]:
    today = date.today()
    in_30_days = today + timedelta(days=30)
    in_90_days = today + timedelta(days=90)

    total_contratos = db.scalar(select(func.count(Contrato.id))) or 0
    contratos_ativos = (
        db.scalar(select(func.count(Contrato.id)).where(Contrato.status == "ativo")) or 0
    )
    contratos_vencendo_30 = (
        db.scalar(
            select(func.count(Contrato.id)).where(
                Contrato.termino >= today,
                Contrato.termino <= in_30_days,
                Contrato.status == "ativo",
            )
        )
        or 0
    )
    contratos_vencendo_90 = (
        db.scalar(
            select(func.count(Contrato.id)).where(
                Contrato.termino >= today,
                Contrato.termino <= in_90_days,
                Contrato.status == "ativo",
            )
        )
        or 0
    )
    valor_total = _money(db.scalar(select(func.coalesce(func.sum(Contrato.valor), 0))))
    alertas_pendentes = (
        db.scalar(select(func.count(Alerta.id)).where(Alerta.status == "pendente")) or 0
    )
    ocorrencias_abertas = (
        db.scalar(select(func.count(Ocorrencia.id)).where(Ocorrencia.status == "aberta")) or 0
    )
    fornecedores = db.scalar(select(func.count(Fornecedor.id))) or 0

    por_secretaria_rows = db.execute(
        select(Secretaria.nome, func.count(Contrato.id))
        .join(Contrato, Contrato.secretaria_id == Secretaria.id, isouter=True)
        .group_by(Secretaria.nome)
        .order_by(func.count(Contrato.id).desc(), Secretaria.nome.asc())
        .limit(8)
    ).all()

    proximos_vencimentos_rows = db.execute(
        select(Contrato.numero, Contrato.objeto, Contrato.termino, Contrato.status)
        .where(Contrato.termino >= today)
        .order_by(Contrato.termino.asc())
        .limit(8)
    ).all()

    return {
        "mode": "live",
        "generated_at": today.isoformat(),
        "cards": {
            "total_contratos": total_contratos,
            "contratos_ativos": contratos_ativos,
            "vencendo_30_dias": contratos_vencendo_30,
            "vencendo_90_dias": contratos_vencendo_90,
            "valor_total": valor_total,
            "alertas_pendentes": alertas_pendentes,
            "ocorrencias_abertas": ocorrencias_abertas,
            "fornecedores": fornecedores,
        },
        "por_secretaria": [
            {"secretaria": nome or "Sem secretaria", "contratos": total}
            for nome, total in por_secretaria_rows
        ],
        "proximos_vencimentos": [
            {
                "numero": numero,
                "objeto": objeto,
                "termino": termino.isoformat(),
                "status": status,
            }
            for numero, objeto, termino, status in proximos_vencimentos_rows
        ],
    }


def get_demo_dashboard_data() -> dict[str, Any]:
    today = date.today()
    return {
        "mode": "demo",
        "generated_at": today.isoformat(),
        "cards": {
            "total_contratos": 128,
            "contratos_ativos": 93,
            "vencendo_30_dias": 11,
            "vencendo_90_dias": 27,
            "valor_total": 18450230.75,
            "alertas_pendentes": 34,
            "ocorrencias_abertas": 7,
            "fornecedores": 58,
        },
        "por_secretaria": [
            {"secretaria": "Saude", "contratos": 34},
            {"secretaria": "Educacao", "contratos": 28},
            {"secretaria": "Obras", "contratos": 21},
            {"secretaria": "Administracao", "contratos": 17},
            {"secretaria": "Assistencia Social", "contratos": 9},
        ],
        "proximos_vencimentos": [
            {
                "numero": "012/2025",
                "objeto": "Fornecimento de medicamentos essenciais",
                "termino": (today + timedelta(days=12)).isoformat(),
                "status": "ativo",
            },
            {
                "numero": "044/2024",
                "objeto": "Manutencao preventiva da frota municipal",
                "termino": (today + timedelta(days=24)).isoformat(),
                "status": "ativo",
            },
            {
                "numero": "078/2024",
                "objeto": "Limpeza e conservacao de predios publicos",
                "termino": (today + timedelta(days=43)).isoformat(),
                "status": "ativo",
            },
        ],
    }

