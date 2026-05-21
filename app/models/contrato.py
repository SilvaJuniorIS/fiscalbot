from datetime import date
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class ContratoStatus(StrEnum):
    rascunho = "rascunho"
    ativo = "ativo"
    alerta = "alerta"
    critico = "critico"
    suspenso = "suspenso"
    encerrado = "encerrado"
    rescindido = "rescindido"


class Contrato(Base, TimestampMixin):
    __tablename__ = "contratos"
    __table_args__ = (
        CheckConstraint("valor >= 0", name="contrato_valor_nao_negativo"),
        CheckConstraint("termino >= inicio", name="contrato_periodo_valido"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    orgao: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    objeto: Mapped[str] = mapped_column(Text, nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    inicio: Mapped[date] = mapped_column(Date, nullable=False)
    termino: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(40), default=ContratoStatus.ativo.value, nullable=False
    )
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)

    secretaria_id: Mapped[int] = mapped_column(ForeignKey("secretarias.id"), nullable=False)
    fornecedor_id: Mapped[int] = mapped_column(ForeignKey("fornecedores.id"), nullable=False)
    fiscal_responsavel_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    gestor_responsavel_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    secretaria = relationship("Secretaria", back_populates="contratos")
    fornecedor = relationship("Fornecedor", back_populates="contratos")
    fiscal_responsavel = relationship(
        "User", foreign_keys=[fiscal_responsavel_id], back_populates="contratos_fiscalizados"
    )
    gestor_responsavel = relationship(
        "User", foreign_keys=[gestor_responsavel_id], back_populates="contratos_geridos"
    )
    anexos = relationship("Anexo", back_populates="contrato", cascade="all, delete-orphan")
    alertas = relationship("Alerta", back_populates="contrato", cascade="all, delete-orphan")
    ocorrencias = relationship(
        "Ocorrencia", back_populates="contrato", cascade="all, delete-orphan"
    )
