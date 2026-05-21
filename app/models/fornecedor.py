from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Fornecedor(Base, TimestampMixin):
    __tablename__ = "fornecedores"

    id: Mapped[int] = mapped_column(primary_key=True)
    razao_social: Mapped[str] = mapped_column(String(220), index=True, nullable=False)
    cnpj: Mapped[str] = mapped_column(String(18), unique=True, index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    contratos = relationship("Contrato", back_populates="fornecedor")

