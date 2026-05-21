from typing import Any

from sqlalchemy.orm import Session

from app.models.log_auditoria import LogAuditoria


def registrar(
    db: Session,
    *,
    user_id: int | None,
    entidade: str,
    entidade_id: int,
    acao: str,
    antes: dict[str, Any] | None = None,
    depois: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> LogAuditoria:
    log = LogAuditoria(
        user_id=user_id,
        entidade=entidade,
        entidade_id=entidade_id,
        acao=acao,
        antes=antes,
        depois=depois,
        ip_address=ip_address,
    )
    db.add(log)
    return log
