from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.importacao_service import processar_importacao_contratos


@celery_app.task(bind=True, name="app.tasks.importacao.importar_contratos")
def importar_contratos(
    self,
    path: str,
    modo: str,
    scoped_secretaria_ids: list[int] | None,
) -> dict:
    with SessionLocal() as db:
        return processar_importacao_contratos(
            db,
            task_id=self.request.id,
            path=path,
            modo=modo,
            scoped_secretaria_ids=scoped_secretaria_ids,
        )
