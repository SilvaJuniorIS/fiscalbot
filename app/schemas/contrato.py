from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.fornecedor import FornecedorRead
from app.schemas.secretaria import SecretariaRead
from app.schemas.user import UserRead


class ContratoBase(BaseModel):
    numero: str = Field(max_length=80)
    orgao: str = Field(max_length=180)
    objeto: str
    valor: Decimal = Field(ge=0)
    inicio: date
    termino: date
    tags: str | None = None
    secretaria_id: int
    fornecedor_id: int
    fiscal_responsavel_id: int | None = None
    gestor_responsavel_id: int | None = None

    @model_validator(mode="after")
    def validate_periodo(self) -> "ContratoBase":
        if self.termino < self.inicio:
            raise ValueError("termino deve ser maior ou igual a inicio")
        return self


class ContratoCreate(ContratoBase):
    pass


class ContratoUpdate(BaseModel):
    numero: str | None = Field(default=None, max_length=80)
    orgao: str | None = Field(default=None, max_length=180)
    objeto: str | None = None
    valor: Decimal | None = Field(default=None, ge=0)
    inicio: date | None = None
    termino: date | None = None
    tags: str | None = None
    secretaria_id: int | None = None
    fornecedor_id: int | None = None
    fiscal_responsavel_id: int | None = None
    gestor_responsavel_id: int | None = None

    @model_validator(mode="after")
    def validate_periodo(self) -> "ContratoUpdate":
        if self.inicio is not None and self.termino is not None and self.termino < self.inicio:
            raise ValueError("termino deve ser maior ou igual a inicio")
        return self


class ContratoFiltros(BaseModel):
    numero: str | None = None
    status: str | None = None
    secretaria_id: int | None = None
    fornecedor_id: int | None = None
    fiscal_id: int | None = None
    vencendo_em_dias: int | None = Field(default=None, ge=1, le=365)


class ContratoRead(ContratoBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


UserOut = UserRead


class ContratoOut(ContratoRead):
    fornecedor: FornecedorRead
    fiscal: UserOut | None = None
    gestor: UserOut | None = None
    secretaria: SecretariaRead
    alertas_ativos: int = 0

    model_config = ConfigDict(from_attributes=True)


class SecretariaTotal(BaseModel):
    nome: str
    total: int


class StatusTotal(BaseModel):
    status: str
    total: int


class ContratoDashboard(BaseModel):
    ativos: int
    vencendo_30: int
    valor_total: Decimal
    em_risco: int
    por_secretaria: list[SecretariaTotal]
    por_status: list[StatusTotal]
