from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_scoped_secretaria_ids
from app.core import storage
from app.db.session import get_db
from app.models.user import User
from app.schemas.anexo import AnexoOut
from app.services import anexo_service

router = APIRouter()


@router.get("/contratos/{contrato_id}/documentos", response_model=list[AnexoOut])
def listar_documentos(
    contrato_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> list[AnexoOut]:
    try:
        return anexo_service.list_by_contrato(db, contrato_id, scoped_secretaria_ids)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/contratos/{contrato_id}/documentos",
    response_model=AnexoOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_documento(
    contrato_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
    file: UploadFile = File(...),
    tipo: str = Form(...),
    versao: int | None = Form(default=None),
) -> AnexoOut:
    try:
        return await anexo_service.upload(
            db, contrato_id, file, tipo, versao, current_user, scoped_secretaria_ids
        )
    except ValueError as exc:
        if "Extensao" in str(exc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/documentos/{anexo_id}/download")
def download_documento(
    anexo_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> FileResponse:
    try:
        anexo = anexo_service.get_anexo(db, anexo_id, scoped_secretaria_ids)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    path = storage.resolve_path(anexo.caminho_storage)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo nao encontrado")
    return FileResponse(path, filename=anexo.nome_arquivo, media_type=anexo.content_type)


@router.delete("/documentos/{anexo_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_documento(
    anexo_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
) -> None:
    try:
        anexo_service.delete(db, anexo_id, current_user, scoped_secretaria_ids)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
