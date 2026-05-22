from enum import StrEnum

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class UserRole(StrEnum):
    admin = "admin"
    gestor = "gestor"
    fiscal = "fiscal"
    auditor = "auditor"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(40), default=UserRole.fiscal.value, nullable=False)
    secretaria_id: Mapped[int | None] = mapped_column(ForeignKey("secretarias.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    secretaria = relationship("Secretaria", back_populates="usuarios")

    contratos_fiscalizados = relationship(
        "Contrato",
        foreign_keys="Contrato.fiscal_responsavel_id",
        back_populates="fiscal_responsavel",
    )
    contratos_geridos = relationship(
        "Contrato",
        foreign_keys="Contrato.gestor_responsavel_id",
        back_populates="gestor_responsavel",
    )
    ocorrencias_fiscalizadas = relationship(
        "Ocorrencia",
        foreign_keys="Ocorrencia.fiscal_id",
        back_populates="fiscal",
    )
    anexos_enviados = relationship(
        "Anexo",
        foreign_keys="Anexo.uploaded_by_id",
        back_populates="uploaded_by",
    )
    logs_auditoria = relationship("LogAuditoria", back_populates="user")
