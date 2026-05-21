from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import assert_secretaria_in_scope
from app.core import storage
from app.models.anexo import Anexo
from app.models.contrato import Contrato
from app.models.user import User
from app.schemas.anexo import AnexoOut
from app.services import log_auditoria


def _to_out(anexo: Anexo) -> AnexoOut:
    return AnexoOut(
        id=anexo.id,
        contrato_id=anexo.contrato_id,
        nome_arquivo=anexo.nome_arquivo,
        tipo=anexo.tipo,
        versao=anexo.versao,
        uploaded_by=anexo.uploaded_by,
        created_at=anexo.created_at,
        url=storage.get_file_url(anexo.caminho_storage),
    )


async def upload(
    db: Session,
    contrato_id: int,
    file: UploadFile,
    tipo: str,
    versao: int | None,
    user: User,
    scoped_secretaria_ids: list[int] | None,
) -> AnexoOut:
    contrato = db.get(Contrato, contrato_id)
    if contrato is None:
        raise ValueError("Contrato nao encontrado")
    assert_secretaria_in_scope(contrato.secretaria_id, scoped_secretaria_ids)

    caminho = await storage.save_file(file, f"contratos/{contrato_id}")
    anexo = Anexo(
        contrato_id=contrato_id,
        tipo=tipo,
        nome_arquivo=file.filename or "arquivo",
        caminho_storage=caminho,
        content_type=file.content_type,
        versao=versao or 1,
        uploaded_by_id=user.id,
    )
    db.add(anexo)
    db.flush()
    log_auditoria.registrar(
        db,
        user_id=user.id,
        entidade="anexos",
        entidade_id=anexo.id,
        acao="upload",
        depois={"contrato_id": contrato_id, "arquivo": anexo.nome_arquivo, "tipo": tipo},
    )
    db.commit()
    loaded = db.scalar(
        select(Anexo)
        .options(joinedload(Anexo.uploaded_by))
        .where(Anexo.id == anexo.id)
    )
    return _to_out(loaded)  # type: ignore[arg-type]


def delete(db: Session, anexo_id: int, user: User, scoped_secretaria_ids: list[int] | None) -> None:
    anexo = db.get(Anexo, anexo_id)
    if anexo is None:
        raise ValueError("Anexo nao encontrado")
    contrato = db.get(Contrato, anexo.contrato_id)
    if contrato is None:
        raise ValueError("Contrato nao encontrado")
    assert_secretaria_in_scope(contrato.secretaria_id, scoped_secretaria_ids)
    antes = {"arquivo": anexo.nome_arquivo, "caminho": anexo.caminho_storage}
    storage.delete_file(anexo.caminho_storage)
    db.delete(anexo)
    log_auditoria.registrar(
        db,
        user_id=user.id,
        entidade="anexos",
        entidade_id=anexo_id,
        acao="excluir",
        antes=antes,
    )
    db.commit()


def list_by_contrato(
    db: Session,
    contrato_id: int,
    scoped_secretaria_ids: list[int] | None,
) -> list[AnexoOut]:
    contrato = db.get(Contrato, contrato_id)
    if contrato is None:
        raise ValueError("Contrato nao encontrado")
    assert_secretaria_in_scope(contrato.secretaria_id, scoped_secretaria_ids)
    anexos = db.scalars(
        select(Anexo)
        .options(joinedload(Anexo.uploaded_by))
        .where(Anexo.contrato_id == contrato_id)
        .order_by(Anexo.created_at.desc())
    ).all()
    return [_to_out(a) for a in anexos]


def get_anexo(db: Session, anexo_id: int, scoped_secretaria_ids: list[int] | None) -> Anexo:
    anexo = db.get(Anexo, anexo_id)
    if anexo is None:
        raise ValueError("Anexo nao encontrado")
    contrato = db.get(Contrato, anexo.contrato_id)
    if contrato is None:
        raise ValueError("Contrato nao encontrado")
    assert_secretaria_in_scope(contrato.secretaria_id, scoped_secretaria_ids)
    return anexo
