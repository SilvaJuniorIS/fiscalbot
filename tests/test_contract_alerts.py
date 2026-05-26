from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.notification import Notification
from app.services.contract_alert_service import check_contract_expiration


def test_check_contract_expiration_creates_threshold_notifications(db_session: Session) -> None:
    today = date(2026, 5, 26)
    contract = Contract(
        status="ativo",
        numero_contrato="18/23",
        fornecedor="Fornecedor Teste",
        fim_vigencia=today + timedelta(days=30),
    )
    db_session.add(contract)
    db_session.commit()

    created = check_contract_expiration(db_session, today=today)

    assert created == 1
    db_session.refresh(contract)
    notification = db_session.query(Notification).one()
    assert notification.contract_id == contract.id
    assert notification.dias_para_vencimento == 30
    assert contract.alerta_30 is True
    assert contract.dias_para_vencimento == 30


def test_check_contract_expiration_does_not_duplicate_notifications(db_session: Session) -> None:
    today = date(2026, 5, 26)
    contract = Contract(
        status="ativo",
        numero_contrato="18/23",
        fornecedor="Fornecedor Teste",
        fim_vigencia=today + timedelta(days=15),
        alerta_15=True,
    )
    db_session.add(contract)
    db_session.commit()

    created = check_contract_expiration(db_session, today=today)

    assert created == 0
    assert db_session.query(Notification).count() == 0
