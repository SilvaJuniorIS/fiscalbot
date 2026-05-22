from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.models.contrato import Contrato, ContratoStatus
from app.models.user import User, UserRole
from app.repositories import contrato_repository
from app.schemas.contrato import (
    ContratoCreate,
    ContratoDashboard,
    ContratoOut,
    ContratoRead,
    ContratoUpdate,
    SecretariaTotal,
    StatusTotal,
)
from app.services import log_auditoria


def calcular_status(termino: date, referencia: date | None = None) -> str:
    hoje = referencia or date.today()
    dias_restantes = (termino - hoje).days
    if dias_restantes < 0:
        return ContratoStatus.encerrado.value
    if dias_restantes <= 30:
        return ContratoStatus.critico.value
    if dias_restantes <= 60:
        return ContratoStatus.alerta.value
    return ContratoStatus.ativo.value


def contrato_snapshot(contrato: Contrato) -> dict[str, Any]:
    return {
        "id": contrato.id,
        "numero": contrato.numero,
        "orgao": contrato.orgao,
        "objeto": contrato.objeto,
        "valor": str(contrato.valor),
        "inicio": contrato.inicio.isoformat(),
        "termino": contrato.termino.isoformat(),
        "status": contrato.status,
        "tags": contrato.tags,
        "secretaria_id": contrato.secretaria_id,
        "fornecedor_id": contrato.fornecedor_id,
        "fiscal_responsavel_id": contrato.fiscal_responsavel_id,
        "gestor_responsavel_id": contrato.gestor_responsavel_id,
    }


def to_contrato_out(contrato: Contrato) -> ContratoOut:
    base = ContratoRead.model_validate(contrato)
    return ContratoOut(
        **base.model_dump(),
        fornecedor=contrato.fornecedor,
        secretaria=contrato.secretaria,
        fiscal=contrato.fiscal_responsavel,
        gestor=contrato.gestor_responsavel,
        alertas_ativos=contrato_repository.count_alertas_ativos(contrato),
    )


def create_contrato(
    db: Session,
    payload: ContratoCreate,
    current_user: User,
    *,
    ip_address: str | None = None,
) -> ContratoOut:
    data = payload.model_dump()
    data["status"] = payload.status or calcular_status(payload.termino)
    contrato = contrato_repository.create(db, data)
    log_auditoria.registrar(
        db,
        user_id=current_user.id,
        entidade="contratos",
        entidade_id=contrato.id,
        acao="criar",
        depois=contrato_snapshot(contrato),
        ip_address=ip_address,
    )
    db.commit()
    return to_contrato_out(contrato)


def update_contrato(
    db: Session,
    contrato: Contrato,
    payload: ContratoUpdate,
    current_user: User,
    *,
    ip_address: str | None = None,
) -> ContratoOut:
    antes = contrato_snapshot(contrato)
    updates = payload.model_dump(exclude_unset=True)
    termino = updates.get("termino", contrato.termino)
    updates["status"] = updates.get("status") or calcular_status(termino)
    contrato = contrato_repository.update(db, contrato, updates)
    log_auditoria.registrar(
        db,
        user_id=current_user.id,
        entidade="contratos",
        entidade_id=contrato.id,
        acao="atualizar",
        antes=antes,
        depois=contrato_snapshot(contrato),
        ip_address=ip_address,
    )
    db.commit()
    return to_contrato_out(contrato)


def delete_contrato(
    db: Session,
    contrato: Contrato,
    current_user: User,
    *,
    ip_address: str | None = None,
) -> None:
    antes = contrato_snapshot(contrato)
    entidade_id = contrato.id
    contrato_repository.delete(db, contrato)
    log_auditoria.registrar(
        db,
        user_id=current_user.id,
        entidade="contratos",
        entidade_id=entidade_id,
        acao="excluir",
        antes=antes,
        ip_address=ip_address,
    )
    db.commit()


def get_dashboard(
    db: Session,
    secretaria_ids: list[int] | None,
) -> ContratoDashboard:
    por_status_raw = contrato_repository.count_by_status(db, secretaria_ids)
    return ContratoDashboard(
        ativos=contrato_repository.count_ativos(db, secretaria_ids),
        vencendo_30=contrato_repository.count_vencendo_30(db, secretaria_ids),
        valor_total=contrato_repository.sum_valor(db, secretaria_ids),
        em_risco=contrato_repository.count_em_risco(db, secretaria_ids),
        por_secretaria=[
            SecretariaTotal(nome=nome, total=total)
            for nome, total in contrato_repository.totals_por_secretaria(db, secretaria_ids)
        ],
        por_status=[
            StatusTotal(status=status, total=total) for status, total in por_status_raw.items()
        ],
    )


def can_edit_contrato(user: User, contrato: Contrato) -> bool:
    if user.role == UserRole.admin.value:
        return True
    if user.role != UserRole.gestor.value:
        return False
    return contrato.gestor_responsavel_id == user.id
