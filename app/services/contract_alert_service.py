from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.notification import Notification

ALERT_THRESHOLDS = {
    30: "alerta_30",
    15: "alerta_15",
    7: "alerta_07",
    1: "alerta_01",
}


def check_contract_expiration(db: Session, today: date | None = None) -> int:
    reference = today or date.today()
    contracts = db.scalars(select(Contract).where(Contract.fim_vigencia.is_not(None))).all()
    created = 0
    for contract in contracts:
        assert contract.fim_vigencia is not None
        days = (contract.fim_vigencia - reference).days
        contract.dias_para_vencimento = days
        flag = ALERT_THRESHOLDS.get(days)
        if flag is None or getattr(contract, flag):
            db.add(contract)
            continue
        db.add(
            Notification(
                contract_id=contract.id,
                tipo="contract_expiration",
                titulo=f"Contrato vence em {days} dia(s)",
                mensagem=(
                    f"Contrato {contract.numero_contrato or contract.id} de "
                    f"{contract.fornecedor or 'fornecedor nao informado'} vence em {days} dia(s)."
                ),
                dias_para_vencimento=days,
            )
        )
        setattr(contract, flag, True)
        db.add(contract)
        created += 1
    db.commit()
    return created
