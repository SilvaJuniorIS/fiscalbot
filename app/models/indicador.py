from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Indicador(Base, TimestampMixin):
    __tablename__ = "indicadores"
    __table_args__ = (CheckConstraint("valor >= 0", name="indicador_valor_nao_negativo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    chave: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    escopo: Mapped[str] = mapped_column(String(120), default="global", index=True, nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    competencia: Mapped[date] = mapped_column(Date, index=True, nullable=False)
