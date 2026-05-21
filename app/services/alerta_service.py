from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.alerta import Alerta, AlertaStatus
from app.models.anexo import Anexo, AnexoTipo
from app.models.contrato import Contrato, ContratoStatus
from app.services import email_service

VENCIMENTO_WINDOWS = (180, 90, 60, 30)
ACTIVE_STATUSES = {
    ContratoStatus.ativo.value,
    ContratoStatus.alerta.value,
    ContratoStatus.critico.value,
}


def _dias_para_termino(termino: date, referencia: date | None = None) -> int:
    return (termino - (referencia or date.today())).days


def _tipo_vencimento(dias: int) -> str:
    return f"vencimento_{dias}"


def _alerta_existe(db: Session, contrato_id: int, tipo: str, data_referencia: date) -> bool:
    existing = db.scalar(
        select(Alerta.id).where(
            Alerta.contrato_id == contrato_id,
            Alerta.tipo == tipo,
            Alerta.data_referencia == data_referencia,
        )
    )
    return existing is not None


def verificar_vencimentos(db: Session, referencia: date | None = None) -> int:
    hoje = referencia or date.today()
    criados = 0
    contratos = db.scalars(select(Contrato).where(Contrato.status.in_(ACTIVE_STATUSES))).all()

    for contrato in contratos:
        dias = _dias_para_termino(contrato.termino, hoje)
        if dias not in VENCIMENTO_WINDOWS:
            continue
        tipo = _tipo_vencimento(dias)
        if _alerta_existe(db, contrato.id, tipo, contrato.termino):
            continue
        alerta = Alerta(
            contrato_id=contrato.id,
            tipo=tipo,
            titulo=f"Contrato {contrato.numero} vence em {dias} dias",
            mensagem=(
                f"O contrato {contrato.numero} vence em {dias} dias. "
                "Avalie renovacao, prorrogacao ou encerramento."
            ),
            data_referencia=contrato.termino,
            status=AlertaStatus.pendente.value,
        )
        db.add(alerta)
        criados += 1

    if criados:
        db.commit()
    return criados


def verificar_reajustes(db: Session, referencia: date | None = None) -> int:
    hoje = referencia or date.today()
    criados = 0
    contratos = db.scalars(select(Contrato).where(Contrato.status.in_(ACTIVE_STATUSES))).all()

    for contrato in contratos:
        aniversario = contrato.inicio.replace(year=contrato.inicio.year + 1)
        if aniversario >= hoje:
            continue
        tem_aditivo = db.scalar(
            select(Anexo.id).where(
                Anexo.contrato_id == contrato.id,
                Anexo.tipo == AnexoTipo.aditivo.value,
            )
        )
        if tem_aditivo:
            continue
        tipo = "reajuste_anual"
        if _alerta_existe(db, contrato.id, tipo, aniversario):
            continue
        db.add(
            Alerta(
                contrato_id=contrato.id,
                tipo=tipo,
                titulo=f"Reajuste anual pendente — contrato {contrato.numero}",
                mensagem="Contrato elegivel a reajuste anual sem aditivo registrado.",
                data_referencia=aniversario,
                status=AlertaStatus.pendente.value,
            )
        )
        criados += 1

    if criados:
        db.commit()
    return criados


def _notificar_responsaveis(db: Session, alertas: list[Alerta]) -> None:
    for alerta in alertas:
        contrato = db.get(Contrato, alerta.contrato_id)
        if contrato is None:
            continue
        for user in (contrato.fiscal_responsavel, contrato.gestor_responsavel):
            if user and user.email:
                email_service.send_alert_email(user.email, alerta, contrato)


def marcar_como_lido(db: Session, alerta_id: int, user_id: int) -> Alerta:
    alerta = db.get(Alerta, alerta_id)
    if alerta is None:
        raise ValueError("Alerta nao encontrado")
    alerta.status = AlertaStatus.lido.value
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta


def resolver_alerta(db: Session, alerta_id: int, user_id: int) -> Alerta:
    alerta = db.get(Alerta, alerta_id)
    if alerta is None:
        raise ValueError("Alerta nao encontrado")
    alerta.status = AlertaStatus.resolvido.value
    alerta.enviado_em = alerta.enviado_em or datetime.now(timezone.utc)
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta


def list_alertas(
    db: Session,
    *,
    secretaria_ids: list[int] | None,
    lido: bool | None = None,
    resolvido: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Alerta]:
    stmt = (
        select(Alerta)
        .join(Contrato, Contrato.id == Alerta.contrato_id)
        .order_by(Alerta.data_referencia.asc())
        .limit(limit)
        .offset(offset)
    )
    if secretaria_ids is not None:
        stmt = stmt.where(Contrato.secretaria_id.in_(secretaria_ids))
    if lido is True:
        stmt = stmt.where(Alerta.status == AlertaStatus.lido.value)
    elif lido is False:
        stmt = stmt.where(Alerta.status.not_in([AlertaStatus.lido.value, AlertaStatus.resolvido.value]))
    if resolvido is True:
        stmt = stmt.where(Alerta.status == AlertaStatus.resolvido.value)
    elif resolvido is False:
        stmt = stmt.where(Alerta.status != AlertaStatus.resolvido.value)
    return list(db.scalars(stmt))


def resumo_alertas(db: Session, secretaria_ids: list[int] | None) -> dict[str, int]:
    alertas = list_alertas(db, secretaria_ids=secretaria_ids, limit=10_000, offset=0)
    urgentes = atencao = info = 0
    nao_lidos = 0
    for alerta in alertas:
        if alerta.status in {AlertaStatus.lido.value, AlertaStatus.resolvido.value}:
            continue
        nao_lidos += 1
        if alerta.tipo in {"vencimento_30", "vencimento_60"} or "critico" in alerta.titulo.lower():
            urgentes += 1
        elif alerta.tipo in {"vencimento_90", "reajuste_anual"}:
            atencao += 1
        else:
            info += 1
    return {"urgentes": urgentes, "atencao": atencao, "info": info, "total_nao_lidos": nao_lidos}


def gerar_para_contrato_em_dias(db: Session, contrato: Contrato, dias: int) -> Alerta | None:
    """Gera alerta de vencimento para contrato com N dias restantes (uso em testes/jobs)."""
    tipo = _tipo_vencimento(dias) if dias in VENCIMENTO_WINDOWS else f"vencimento_{dias}"
    if _alerta_existe(db, contrato.id, tipo, contrato.termino):
        return None
    alerta = Alerta(
        contrato_id=contrato.id,
        tipo=tipo,
        titulo=f"Contrato {contrato.numero} vence em {dias} dias",
        mensagem=f"Contrato vence em {dias} dias.",
        data_referencia=contrato.termino,
        status=AlertaStatus.pendente.value,
    )
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta
