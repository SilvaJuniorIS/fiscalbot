import logging

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.services import alerta_service
from app.services.contract_alert_service import check_contract_expiration

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.alertas.checar_vencimentos")
def checar_vencimentos() -> dict[str, int]:
    logger.info("Iniciando checagem de vencimentos")
    with SessionLocal() as db:
        criados = alerta_service.verificar_vencimentos(db)
    logger.info("Checagem de vencimentos concluida: %s alertas", criados)
    return {"criados": criados}


@celery_app.task(name="app.tasks.alertas.checar_reajustes")
def checar_reajustes() -> dict[str, int]:
    logger.info("Iniciando checagem de reajustes")
    with SessionLocal() as db:
        criados = alerta_service.verificar_reajustes(db)
    logger.info("Checagem de reajustes concluida: %s alertas", criados)
    return {"criados": criados}


@celery_app.task(name="app.tasks.alertas.check_contract_expiration")
def check_contract_expiration_task() -> dict[str, int]:
    logger.info("Iniciando checagem de vencimentos de contracts")
    with SessionLocal() as db:
        criados = check_contract_expiration(db)
    logger.info("Checagem de contracts concluida: %s notificacoes", criados)
    return {"criados": criados}
