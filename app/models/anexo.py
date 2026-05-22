from enum import StrEnum

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class AnexoTipo(StrEnum):
    contrato = "contrato"
    aditivo = "aditivo"
    nota_fiscal = "nota_fiscal"
    relatorio = "relatorio"
    foto = "foto"
    notificacao = "notificacao"
    ata = "ata"
    outro = "outro"


class Anexo(Base, TimestampMixin):
    __tablename__ = "anexos"

    id: Mapped[int] = mapped_column(primary_key=True)
    contrato_id: Mapped[int] = mapped_column(ForeignKey("contratos.id"), index=True, nullable=False)
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    caminho_storage: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    versao: Mapped[int] = mapped_column(default=1, nullable=False)
    texto_ocr: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    contrato = relationship("Contrato", back_populates="anexos")
    uploaded_by = relationship(
        "User",
        foreign_keys=[uploaded_by_id],
        back_populates="anexos_enviados",
    )

