from typing import Annotated

from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import (
    assert_secretaria_in_scope,
    get_current_user,
    get_scoped_secretaria_ids,
    require_roles,
)
from app.db.session import get_db
from app.models.contrato import Contrato
from app.models.user import User, UserRole
from app.repositories import contrato_repository
from app.schemas.contrato import (
    ContratoCreate,
    ContratoDashboard,
    ContratoFiltros,
    ContratoOut,
    ContratoPage,
    ContratoUpdate,
)
from app.services import contrato_service

router = APIRouter()


def _get_contrato_in_scope(
    db: Session,
    contrato_id: int,
    scoped_secretaria_ids: list[int] | None,
) -> Contrato:
    contrato = contrato_repository.get_by_id(db, contrato_id)
    if contrato is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato nao encontrado")
    assert_secretaria_in_scope(contrato.secretaria_id, scoped_secretaria_ids)
    return contrato


@router.get("/dashboard", response_model=ContratoDashboard)
def contratos_dashboard(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> ContratoDashboard:
    return contrato_service.get_dashboard(db, scoped_secretaria_ids)


@router.get("", response_model=list[ContratoOut] | ContratoPage)
def list_contratos(
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
    numero: str | None = None,
    q: Annotated[str | None, Query(max_length=160)] = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    secretaria_id: int | None = None,
    fornecedor_id: int | None = None,
    fiscal_id: int | None = None,
    vencendo_em_dias: Annotated[int | None, Query(ge=1, le=365)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    order_by: str = "termino",
    order_dir: Annotated[str, Query(pattern="^(asc|desc)$")] = "asc",
    formato: Annotated[str, Query(pattern="^(lista|pagina)$")] = "lista",
) -> list[ContratoOut] | ContratoPage:
    filtros = ContratoFiltros(
        numero=numero,
        status=status_filter,
        secretaria_id=secretaria_id,
        fornecedor_id=fornecedor_id,
        fiscal_responsavel_id=fiscal_id,
        vencendo_em_dias=vencendo_em_dias,
    )
    if filtros.secretaria_id is not None:
        assert_secretaria_in_scope(filtros.secretaria_id, scoped_secretaria_ids)

    contratos = contrato_repository.list_with_filters(
        db,
        filtros,
        scoped_secretaria_ids,
        page=page,
        limit=limit,
        q=q,
        order_by=order_by,
        order_dir=order_dir,
    )
    total = contrato_repository.count_with_filters(
        db,
        filtros,
        scoped_secretaria_ids,
        q=q,
    )
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Page"] = str(page)
    response.headers["X-Limit"] = str(limit)
    items = [contrato_service.to_contrato_out(c) for c in contratos]
    if formato == "pagina":
        return ContratoPage(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=max(1, ceil(total / limit)) if total else 1,
        )
    return items


@router.post("", response_model=ContratoOut, status_code=status.HTTP_201_CREATED)
def create_contrato(
    payload: ContratoCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.gestor))],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> ContratoOut:
    assert_secretaria_in_scope(payload.secretaria_id, scoped_secretaria_ids)
    if current_user.role == UserRole.gestor.value:
        if payload.gestor_responsavel_id not in {None, current_user.id}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Gestor so pode criar contratos sob sua responsabilidade",
            )
        payload.gestor_responsavel_id = current_user.id
    return contrato_service.create_contrato(
        db,
        payload,
        current_user,
        ip_address=request.client.host if request.client else None,
    )


@router.get("/{contrato_id}", response_model=ContratoOut)
def get_contrato(
    contrato_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> ContratoOut:
    contrato = _get_contrato_in_scope(db, contrato_id, scoped_secretaria_ids)
    return contrato_service.to_contrato_out(contrato)


@router.put("/{contrato_id}", response_model=ContratoOut)
def update_contrato(
    contrato_id: int,
    payload: ContratoUpdate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> ContratoOut:
    contrato = _get_contrato_in_scope(db, contrato_id, scoped_secretaria_ids)
    if not contrato_service.can_edit_contrato(current_user, contrato):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente o gestor responsavel ou administrador pode editar este contrato",
        )

    updates = payload.model_dump(exclude_unset=True)
    if "secretaria_id" in updates:
        assert_secretaria_in_scope(updates["secretaria_id"], scoped_secretaria_ids)

    return contrato_service.update_contrato(
        db,
        contrato,
        payload,
        current_user,
        ip_address=request.client.host if request.client else None,
    )


@router.delete("/{contrato_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contrato(
    contrato_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin))],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> None:
    contrato = _get_contrato_in_scope(db, contrato_id, scoped_secretaria_ids)
    contrato_service.delete_contrato(
        db,
        contrato,
        current_user,
        ip_address=request.client.host if request.client else None,
    )
