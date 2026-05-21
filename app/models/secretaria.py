from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Secretaria(Base, TimestampMixin):
    __tablename__ = "secretarias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    sigla: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    contratos = relationship("Contrato", back_populates="secretaria")
    usuarios = relationship("User", back_populates="secretaria")

