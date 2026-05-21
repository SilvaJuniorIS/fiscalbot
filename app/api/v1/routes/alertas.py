from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_scoped_secretaria_ids, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.alerta import AlertaRead
from app.services import alerta_service, log_auditoria

router = APIRouter()


@router.get("", response_model=list[AlertaRead])
def list_alertas(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
    lido: bool | None = None,
    resolvido: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[AlertaRead]:
    return alerta_service.list_alertas(
        db,
        secretaria_ids=scoped_secretaria_ids,
        lido=lido,
        resolvido=resolvido,
        limit=limit,
        offset=offset,
    )


@router.get("/resumo")
def alertas_resumo(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> dict[str, int]:
    return alerta_service.resumo_alertas(db, scoped_secretaria_ids)


@router.post("/gerar-vencimentos")
def gerar_vencimentos(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.admin))],
) -> dict[str, int]:
    criados = alerta_service.verificar_vencimentos(db)
    return {"criados": criados}


@router.put("/{alerta_id}/lido", response_model=AlertaRead)
def marcar_lido(
    alerta_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AlertaRead:
    try:
        alerta = alerta_service.marcar_como_lido(db, alerta_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    log_auditoria.registrar(
        db,
        user_id=current_user.id,
        entidade="alertas",
        entidade_id=alerta_id,
        acao="marcar_lido",
        depois={"status": alerta.status},
    )
    db.commit()
    return alerta


@router.put("/{alerta_id}/resolver", response_model=AlertaRead)
def resolver_alerta(
    alerta_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AlertaRead:
    try:
        alerta = alerta_service.resolver_alerta(db, alerta_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    log_auditoria.registrar(
        db,
        user_id=current_user.id,
        entidade="alertas",
        entidade_id=alerta_id,
        acao="resolver",
        depois={"status": alerta.status},
    )
    db.commit()
    return alerta
