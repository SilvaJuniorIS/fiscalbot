import uuid
from datetime import date
from decimal import Decimal

from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Contract(Base, TimestampMixin):
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    status: Mapped[str | None] = mapped_column(String(50), index=True)
    numero_contrato: Mapped[str | None] = mapped_column(String(50), index=True)
    numero_aditivo: Mapped[str | None] = mapped_column(String(50))

    fornecedor: Mapped[str | None] = mapped_column(Text)
    cnpj: Mapped[str | None] = mapped_column(String(20), index=True)

    secretaria: Mapped[str | None] = mapped_column(String(120), index=True)
    secretario: Mapped[str | None] = mapped_column(Text)

    gestor: Mapped[str | None] = mapped_column(Text)
    gestor_cpf: Mapped[str | None] = mapped_column(String(14))

    fiscal: Mapped[str | None] = mapped_column(Text)
    fiscal_cpf: Mapped[str | None] = mapped_column(String(14))

    objeto: Mapped[str | None] = mapped_column(Text)

    vigencia_texto: Mapped[str | None] = mapped_column(Text)
    inicio_vigencia: Mapped[date | None] = mapped_column(Date)
    fim_vigencia: Mapped[date | None] = mapped_column(Date, index=True)

    data_os: Mapped[date | None] = mapped_column(Date)

    processo_administrativo: Mapped[str | None] = mapped_column(String(80))
    processo_execucao: Mapped[str | None] = mapped_column(String(80))

    audesp_licitacao: Mapped[str | None] = mapped_column(String(80))
    audesp_ajuste: Mapped[str | None] = mapped_column(Text)

    modalidade: Mapped[str | None] = mapped_column(String(100))

    valor_total: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))

    data_assinatura: Mapped[date | None] = mapped_column(Date)
    data_publicacao: Mapped[date | None] = mapped_column(Date)

    observacao: Mapped[str | None] = mapped_column(Text)

    dias_para_vencimento: Mapped[int | None] = mapped_column(Integer)

    alerta_30: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    alerta_15: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    alerta_07: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    alerta_01: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")


class ContractImportLog(Base):
    __tablename__ = "contract_import_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    usuario: Mapped[str | None] = mapped_column(String(255))
    linhas_processadas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    linhas_importadas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    linhas_com_erro: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    detalhes_erro: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
