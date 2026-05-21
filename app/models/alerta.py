from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class AlertaTipo(StrEnum):
    vencimento = "vencimento"
    reajuste = "reajuste"
    certidao = "certidao"
    sla = "sla"
    pendencia_documental = "pendencia_documental"


class AlertaStatus(StrEnum):
    pendente = "pendente"
    enviado = "enviado"
    lido = "lido"
    resolvido = "resolvido"
    cancelado = "cancelado"


class Alerta(Base, TimestampMixin):
    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(primary_key=True)
    contrato_id: Mapped[int] = mapped_column(ForeignKey("contratos.id"), index=True, nullable=False)
    tipo: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    titulo: Mapped[str] = mapped_column(String(180), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    data_referencia: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(40), default=AlertaStatus.pendente.value, nullable=False
    )
    enviado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    contrato = relationship("Contrato", back_populates="alertas")
