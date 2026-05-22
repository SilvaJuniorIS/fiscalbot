from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class LogAuditoria(Base, TimestampMixin):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    entidade: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    entidade_id: Mapped[int] = mapped_column(index=True, nullable=False)
    acao: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    antes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    depois: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(80), nullable=True)

    user = relationship("User", back_populates="logs_auditoria")
