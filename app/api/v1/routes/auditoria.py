from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.log_auditoria import LogAuditoria
from app.models.user import User, UserRole
from app.schemas.log import LogOut

router = APIRouter()


@router.get("", response_model=list[LogOut])
def listar_logs(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.admin))],
    user_id: int | None = None,
    entidade: str | None = Query(default=None, alias="tabela"),
    registro_id: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[LogOut]:
    offset = (page - 1) * limit
    stmt = (
        select(LogAuditoria)
        .options(joinedload(LogAuditoria.user))
        .order_by(LogAuditoria.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if user_id is not None:
        stmt = stmt.where(LogAuditoria.user_id == user_id)
    if entidade:
        stmt = stmt.where(LogAuditoria.entidade == entidade)
    if registro_id is not None:
        stmt = stmt.where(LogAuditoria.entidade_id == registro_id)
    if data_inicio:
        stmt = stmt.where(LogAuditoria.created_at >= data_inicio)
    if data_fim:
        stmt = stmt.where(LogAuditoria.created_at <= data_fim)
    logs = db.scalars(stmt).all()
    return [
        LogOut(
            id=log.id,
            user=log.user,
            entidade=log.entidade,
            entidade_id=log.entidade_id,
            acao=log.acao,
            antes=log.antes,
            depois=log.depois,
            created_at=log.created_at,
        )
        for log in logs
    ]


@router.get("/{registro_id}", response_model=list[LogOut])
def historico_registro(
    registro_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.admin))],
    entidade: str | None = Query(default=None, alias="tabela"),
) -> list[LogOut]:
    stmt = (
        select(LogAuditoria)
        .options(joinedload(LogAuditoria.user))
        .where(LogAuditoria.entidade_id == registro_id)
        .order_by(LogAuditoria.created_at.asc())
    )
    if entidade:
        stmt = stmt.where(LogAuditoria.entidade == entidade)
    logs = db.scalars(stmt).all()
    if not logs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Historico nao encontrado")
    return [
        LogOut(
            id=log.id,
            user=log.user,
            entidade=log.entidade,
            entidade_id=log.entidade_id,
            acao=log.acao,
            antes=log.antes,
            depois=log.depois,
            created_at=log.created_at,
        )
        for log in logs
    ]
