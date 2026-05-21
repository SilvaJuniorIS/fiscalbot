from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.alerta import AlertaStatus
from app.models.contrato import Contrato
from app.schemas.contrato import ContratoFiltros


def _base_query():
    return select(Contrato).options(
        joinedload(Contrato.fornecedor),
        joinedload(Contrato.secretaria),
        joinedload(Contrato.fiscal_responsavel),
        joinedload(Contrato.gestor_responsavel),
        joinedload(Contrato.alertas),
    )


def _apply_scope(stmt, secretaria_ids: list[int] | None):
    if secretaria_ids is not None:
        stmt = stmt.where(Contrato.secretaria_id.in_(secretaria_ids))
    return stmt


def _apply_filtros(stmt, filtros: ContratoFiltros, today: date):
    if filtros.numero:
        stmt = stmt.where(Contrato.numero.ilike(f"%{filtros.numero}%"))
    if filtros.status:
        stmt = stmt.where(Contrato.status == filtros.status)
    if filtros.secretaria_id is not None:
        stmt = stmt.where(Contrato.secretaria_id == filtros.secretaria_id)
    if filtros.fornecedor_id is not None:
        stmt = stmt.where(Contrato.fornecedor_id == filtros.fornecedor_id)
    if filtros.fiscal_id is not None:
        stmt = stmt.where(Contrato.fiscal_responsavel_id == filtros.fiscal_id)
    if filtros.vencendo_em_dias is not None:
        limite = today + timedelta(days=filtros.vencendo_em_dias)
        stmt = stmt.where(Contrato.termino >= today, Contrato.termino <= limite)
    return stmt


def get_by_id(db: Session, contrato_id: int) -> Contrato | None:
    stmt = _base_query().where(Contrato.id == contrato_id)
    return db.scalar(stmt)


def create(db: Session, data: dict) -> Contrato:
    contrato = Contrato(**data)
    db.add(contrato)
    db.flush()
    loaded = get_by_id(db, contrato.id)
    assert loaded is not None
    return loaded


def update(db: Session, contrato: Contrato, data: dict) -> Contrato:
    for field, value in data.items():
        setattr(contrato, field, value)
    db.add(contrato)
    db.flush()
    loaded = get_by_id(db, contrato.id)
    assert loaded is not None
    return loaded


def delete(db: Session, contrato: Contrato) -> None:
    db.delete(contrato)
    db.flush()


def list_with_filters(
    db: Session,
    filtros: ContratoFiltros,
    secretaria_ids: list[int] | None,
    *,
    page: int = 1,
    limit: int = 50,
    today: date | None = None,
) -> list[Contrato]:
    today = today or date.today()
    offset = (page - 1) * limit
    stmt = _base_query().order_by(Contrato.termino.asc())
    stmt = _apply_scope(stmt, secretaria_ids)
    stmt = _apply_filtros(stmt, filtros, today)
    stmt = stmt.limit(limit).offset(offset)
    return list(db.scalars(stmt).unique())


def count_by_status(
    db: Session,
    secretaria_ids: list[int] | None,
) -> dict[str, int]:
    stmt = select(Contrato.status, func.count(Contrato.id)).group_by(Contrato.status)
    stmt = _apply_scope(stmt, secretaria_ids)
    rows = db.execute(stmt).all()
    return {status: total for status, total in rows}


def get_vencendo(
    db: Session,
    dias: int,
    secretaria_ids: list[int] | None,
    today: date | None = None,
) -> list[Contrato]:
    today = today or date.today()
    filtros = ContratoFiltros(vencendo_em_dias=dias)
    return list_with_filters(db, filtros, secretaria_ids, page=1, limit=10_000, today=today)


def count_alertas_ativos(contrato: Contrato) -> int:
    ativos = {AlertaStatus.pendente.value, AlertaStatus.enviado.value}
    return sum(1 for alerta in contrato.alertas if alerta.status in ativos)


def sum_valor(db: Session, secretaria_ids: list[int] | None) -> Decimal:
    stmt = select(func.coalesce(func.sum(Contrato.valor), 0))
    stmt = _apply_scope(stmt, secretaria_ids)
    return Decimal(str(db.scalar(stmt) or 0))


def count_ativos(db: Session, secretaria_ids: list[int] | None) -> int:
    from app.models.contrato import ContratoStatus

    stmt = select(func.count(Contrato.id)).where(
        Contrato.status.in_(
            [
                ContratoStatus.ativo.value,
                ContratoStatus.alerta.value,
                ContratoStatus.critico.value,
            ]
        )
    )
    stmt = _apply_scope(stmt, secretaria_ids)
    return int(db.scalar(stmt) or 0)


def count_em_risco(db: Session, secretaria_ids: list[int] | None) -> int:
    from app.models.contrato import ContratoStatus

    stmt = select(func.count(Contrato.id)).where(
        Contrato.status.in_([ContratoStatus.alerta.value, ContratoStatus.critico.value])
    )
    stmt = _apply_scope(stmt, secretaria_ids)
    return int(db.scalar(stmt) or 0)


def count_vencendo_30(
    db: Session,
    secretaria_ids: list[int] | None,
    today: date | None = None,
) -> int:
    today = today or date.today()
    limite = today + timedelta(days=30)
    stmt = select(func.count(Contrato.id)).where(
        Contrato.termino >= today,
        Contrato.termino <= limite,
    )
    stmt = _apply_scope(stmt, secretaria_ids)
    return int(db.scalar(stmt) or 0)


def totals_por_secretaria(
    db: Session,
    secretaria_ids: list[int] | None,
) -> list[tuple[str, int]]:
    from app.models.secretaria import Secretaria

    stmt = (
        select(Secretaria.nome, func.count(Contrato.id))
        .join(Contrato, Contrato.secretaria_id == Secretaria.id)
        .group_by(Secretaria.nome)
        .order_by(func.count(Contrato.id).desc(), Secretaria.nome.asc())
    )
    if secretaria_ids is not None:
        stmt = stmt.where(Contrato.secretaria_id.in_(secretaria_ids))
    return list(db.execute(stmt).all())
