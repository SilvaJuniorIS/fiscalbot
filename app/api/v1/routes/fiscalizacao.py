from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_scoped_secretaria_ids, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.ocorrencia import FiscalizacaoResumo, OcorrenciaCreate, OcorrenciaOut, OcorrenciaUpdate
from app.services import ocorrencia_service

router = APIRouter()


@router.get("/resumo", response_model=FiscalizacaoResumo)
def fiscalizacao_resumo(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> FiscalizacaoResumo:
    return ocorrencia_service.resumo_fiscalizacao(db, scoped_secretaria_ids)


@router.get("/contratos/{contrato_id}/ocorrencias", response_model=list[OcorrenciaOut])
def listar_ocorrencias(
    contrato_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> list[OcorrenciaOut]:
    try:
        return ocorrencia_service.listar_por_contrato(db, contrato_id, scoped_secretaria_ids)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post(
    "/contratos/{contrato_id}/ocorrencias",
    response_model=OcorrenciaOut,
    status_code=status.HTTP_201_CREATED,
)
def criar_ocorrencia(
    contrato_id: int,
    payload: OcorrenciaCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        User, Depends(require_roles(UserRole.admin, UserRole.gestor, UserRole.fiscal))
    ],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> OcorrenciaOut:
    try:
        return ocorrencia_service.criar(db, contrato_id, payload, current_user, scoped_secretaria_ids)
    except ValueError as exc:
        detail = str(exc)
        code = (
            status.HTTP_403_FORBIDDEN
            if "escopo" in detail.lower() or "secretaria" in detail.lower()
            else status.HTTP_404_NOT_FOUND
        )
        raise HTTPException(status_code=code, detail=detail) from exc


@router.get("/ocorrencias/{ocorrencia_id}", response_model=OcorrenciaOut)
def detalhe_ocorrencia(
    ocorrencia_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> OcorrenciaOut:
    try:
        return ocorrencia_service.obter(db, ocorrencia_id, scoped_secretaria_ids)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/ocorrencias/{ocorrencia_id}", response_model=OcorrenciaOut)
def atualizar_ocorrencia(
    ocorrencia_id: int,
    payload: OcorrenciaUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.gestor))],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> OcorrenciaOut:
    try:
        return ocorrencia_service.atualizar_status(
            db, ocorrencia_id, payload, current_user, scoped_secretaria_ids
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
