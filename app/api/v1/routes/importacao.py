from pathlib import Path
from typing import Annotated, Any

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse

from app.api.deps import get_current_user, get_scoped_secretaria_ids, require_roles
from app.core.celery_app import celery_app
from app.models.user import User, UserRole
from app.services.importacao_service import diretorio_importacoes, salvar_upload_importacao
from app.tasks.importacao import importar_contratos

router = APIRouter()


@router.post("/contratos", status_code=status.HTTP_202_ACCEPTED)
async def importar_contratos_endpoint(
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.gestor))],
    scoped_secretaria_ids: Annotated[list[int] | None, Depends(get_scoped_secretaria_ids)],
    file: UploadFile = File(...),
    modo: Annotated[str, Query(pattern="^(append|overwrite)$")] = "append",
) -> dict[str, Any]:
    try:
        path = salvar_upload_importacao(file.filename or "contratos.csv", await file.read())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    scope = scoped_secretaria_ids
    if current_user.role == UserRole.gestor.value and current_user.secretaria_id is not None:
        scope = [current_user.secretaria_id]

    task = importar_contratos.delay(str(path), modo, scope)
    return {"task_id": task.id, "status": "queued"}


@router.get("/contratos/template.csv")
def download_template_importacao(
    _: Annotated[User, Depends(get_current_user)],
) -> FileResponse:
    path = Path("examples") / "contratos_importacao.csv"
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template nao encontrado")
    return FileResponse(path, filename="contratos_importacao.csv", media_type="text/csv")


@router.get("/contratos/{task_id}/relatorio.csv")
def download_relatorio_importacao(
    task_id: str,
    _: Annotated[User, Depends(get_current_user)],
) -> FileResponse:
    path = diretorio_importacoes() / task_id / "relatorio.csv"
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relatorio nao encontrado")
    return FileResponse(path, filename=f"relatorio_importacao_{task_id}.csv", media_type="text/csv")


@router.get("/contratos/{task_id}")
def status_importacao_contratos(
    task_id: str,
    _: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    result = AsyncResult(task_id, app=celery_app)
    payload: dict[str, Any] = {"task_id": task_id, "status": result.status.lower()}
    if result.failed():
        payload["erro"] = str(result.result)
    elif result.ready():
        payload["resultado"] = result.result
    return payload
