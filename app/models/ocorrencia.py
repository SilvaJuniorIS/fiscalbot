from datetime import date
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class OcorrenciaTipo(StrEnum):
    vistoria = "vistoria"
    notificacao = "notificacao"
    pendencia = "pendencia"
    aceite_parcial = "aceite_parcial"


class OcorrenciaStatus(StrEnum):
    aberta = "aberta"
    em_tratamento = "em_tratamento"
    em_andamento = "em_andamento"
    resolvida = "resolvida"
    concluida = "concluida"
    cancelada = "cancelada"


class Ocorrencia(Base, TimestampMixin):
    __tablename__ = "ocorrencias"
    __table_args__ = (
        CheckConstraint(
            "latitude IS NULL OR latitude BETWEEN -90 AND 90",
            name="ocorrencia_latitude_valida",
        ),
        CheckConstraint(
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
            name="ocorrencia_longitude_valida",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    contrato_id: Mapped[int] = mapped_column(ForeignKey("contratos.id"), index=True, nullable=False)
    fiscal_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    tipo: Mapped[str | None] = mapped_column(String(60), nullable=True)
    titulo: Mapped[str] = mapped_column(String(180), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    data_ocorrencia: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(40), default=OcorrenciaStatus.aberta.value, nullable=False
    )
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    plano_acao: Mapped[str | None] = mapped_column(Text, nullable=True)

    contrato = relationship("Contrato", back_populates="ocorrencias")
    fiscal = relationship(
        "User",
        foreign_keys=[fiscal_id],
        back_populates="ocorrencias_fiscalizadas",
    )
