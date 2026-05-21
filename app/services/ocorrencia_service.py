from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import assert_secretaria_in_scope
from app.models.contrato import Contrato
from app.models.ocorrencia import Ocorrencia, OcorrenciaStatus, OcorrenciaTipo
from app.models.user import User
from app.schemas.ocorrencia import FiscalizacaoResumo, OcorrenciaCreate, OcorrenciaOut, OcorrenciaUpdate
from app.services import log_auditoria


def _normalize_status(status: str) -> str:
    if status == OcorrenciaStatus.em_andamento.value:
        return OcorrenciaStatus.em_tratamento.value
    if status == OcorrenciaStatus.concluida.value:
        return OcorrenciaStatus.resolvida.value
    return status


def _to_out(ocorrencia: Ocorrencia) -> OcorrenciaOut:
    return OcorrenciaOut.model_validate(ocorrencia)


def criar(
    db: Session,
    contrato_id: int,
    data: OcorrenciaCreate,
    fiscal: User,
    scoped_secretaria_ids: list[int] | None,
) -> OcorrenciaOut:
    contrato = db.get(Contrato, contrato_id)
    if contrato is None:
        raise ValueError("Contrato nao encontrado")
    assert_secretaria_in_scope(contrato.secretaria_id, scoped_secretaria_ids)

    ocorrencia = Ocorrencia(
        contrato_id=contrato_id,
        fiscal_id=fiscal.id,
        tipo=data.tipo.value,
        titulo=data.titulo,
        descricao=data.descricao,
        data_ocorrencia=data.data_ocorrencia or date.today(),
        status=OcorrenciaStatus.aberta.value,
        latitude=data.latitude,
        longitude=data.longitude,
        plano_acao=data.plano_acao,
    )
    db.add(ocorrencia)
    db.flush()
    log_auditoria.registrar(
        db,
        user_id=fiscal.id,
        entidade="ocorrencias",
        entidade_id=ocorrencia.id,
        acao="criar",
        depois={"titulo": ocorrencia.titulo, "tipo": ocorrencia.tipo},
    )
    db.commit()
    return _load(db, ocorrencia.id)


def atualizar_status(
    db: Session,
    ocorrencia_id: int,
    payload: OcorrenciaUpdate,
    user: User,
    scoped_secretaria_ids: list[int] | None,
) -> OcorrenciaOut:
    ocorrencia = db.get(Ocorrencia, ocorrencia_id)
    if ocorrencia is None:
        raise ValueError("Ocorrencia nao encontrada")
    contrato = db.get(Contrato, ocorrencia.contrato_id)
    if contrato is None:
        raise ValueError("Contrato nao encontrado")
    assert_secretaria_in_scope(contrato.secretaria_id, scoped_secretaria_ids)

    antes = {"status": ocorrencia.status}
    if payload.descricao is not None:
        ocorrencia.descricao = payload.descricao
    if payload.plano_acao is not None:
        ocorrencia.plano_acao = payload.plano_acao
    if payload.status is not None:
        ocorrencia.status = _normalize_status(payload.status.value)
    db.add(ocorrencia)
    log_auditoria.registrar(
        db,
        user_id=user.id,
        entidade="ocorrencias",
        entidade_id=ocorrencia.id,
        acao="atualizar_status",
        antes=antes,
        depois={"status": ocorrencia.status},
    )
    db.commit()
    return _load(db, ocorrencia.id)


def listar_por_contrato(
    db: Session,
    contrato_id: int,
    scoped_secretaria_ids: list[int] | None,
) -> list[OcorrenciaOut]:
    contrato = db.get(Contrato, contrato_id)
    if contrato is None:
        raise ValueError("Contrato nao encontrado")
    assert_secretaria_in_scope(contrato.secretaria_id, scoped_secretaria_ids)
    rows = db.scalars(
        select(Ocorrencia)
        .options(
            joinedload(Ocorrencia.fiscal),
            joinedload(Ocorrencia.contrato),
        )
        .where(Ocorrencia.contrato_id == contrato_id)
        .order_by(Ocorrencia.data_ocorrencia.desc())
    ).all()
    return [_to_out(row) for row in rows]


def obter(db: Session, ocorrencia_id: int, scoped_secretaria_ids: list[int] | None) -> OcorrenciaOut:
    ocorrencia = _load(db, ocorrencia_id)
    if ocorrencia is None:
        raise ValueError("Ocorrencia nao encontrada")
    contrato = db.get(Contrato, ocorrencia.contrato_id)
    if contrato is None:
        raise ValueError("Contrato nao encontrado")
    assert_secretaria_in_scope(contrato.secretaria_id, scoped_secretaria_ids)
    return _to_out(ocorrencia)


def _load(db: Session, ocorrencia_id: int) -> Ocorrencia | None:
    return db.scalar(
        select(Ocorrencia)
        .options(
            joinedload(Ocorrencia.fiscal),
            joinedload(Ocorrencia.contrato),
        )
        .where(Ocorrencia.id == ocorrencia_id)
    )


def _scoped_ocorrencia_stmt(scoped_secretaria_ids: list[int] | None):
    stmt = select(func.count(Ocorrencia.id)).join(
        Contrato, Contrato.id == Ocorrencia.contrato_id
    )
    if scoped_secretaria_ids is not None:
        stmt = stmt.where(Contrato.secretaria_id.in_(scoped_secretaria_ids))
    return stmt


def resumo_fiscalizacao(db: Session, scoped_secretaria_ids: list[int] | None) -> FiscalizacaoResumo:
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)

    vistorias = db.scalar(
        _scoped_ocorrencia_stmt(scoped_secretaria_ids).where(
            Ocorrencia.tipo == OcorrenciaTipo.vistoria.value,
            Ocorrencia.data_ocorrencia >= inicio_mes,
        )
    )
    abertas = db.scalar(
        _scoped_ocorrencia_stmt(scoped_secretaria_ids).where(
            Ocorrencia.status.in_(
                [OcorrenciaStatus.aberta.value, OcorrenciaStatus.em_tratamento.value]
            )
        )
    )
    resolvidas = db.scalar(
        _scoped_ocorrencia_stmt(scoped_secretaria_ids).where(
            Ocorrencia.status == OcorrenciaStatus.resolvida.value
        )
    )
    pendencias = db.scalar(
        _scoped_ocorrencia_stmt(scoped_secretaria_ids).where(
            Ocorrencia.tipo == OcorrenciaTipo.pendencia.value,
            Ocorrencia.status != OcorrenciaStatus.resolvida.value,
        )
    )
    return FiscalizacaoResumo(
        vistorias_mes=int(vistorias or 0),
        ocorrencias_abertas=int(abertas or 0),
        conformes=int(resolvidas or 0),
        com_ressalva=int(pendencias or 0),
        com_pendencia=int(abertas or 0),
    )
