from datetime import date, datetime
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from app.schemas.fornecedor import FornecedorRead
from app.schemas.secretaria import SecretariaRead
from app.schemas.user import UserRead


class ContratoBase(BaseModel):
    numero: str = Field(max_length=80)
    orgao: str = Field(max_length=180)
    objeto: str
    valor: Decimal = Field(ge=0)
    inicio: date = Field(validation_alias=AliasChoices("inicio", "data_inicio"))
    termino: date = Field(validation_alias=AliasChoices("termino", "data_termino"))
    tags: str | None = None
    secretaria_id: int
    fornecedor_id: int
    fiscal_responsavel_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("fiscal_responsavel_id", "fiscal_id"),
    )
    gestor_responsavel_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("gestor_responsavel_id", "gestor_id"),
    )
    status: str | None = Field(default=None, max_length=40)

    model_config = ConfigDict(populate_by_name=True)

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
    inicio: date | None = Field(
        default=None,
        validation_alias=AliasChoices("inicio", "data_inicio"),
    )
    termino: date | None = Field(
        default=None,
        validation_alias=AliasChoices("termino", "data_termino"),
    )
    tags: str | None = None
    secretaria_id: int | None = None
    fornecedor_id: int | None = None
    fiscal_responsavel_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("fiscal_responsavel_id", "fiscal_id"),
    )
    gestor_responsavel_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("gestor_responsavel_id", "gestor_id"),
    )
    status: str | None = Field(default=None, max_length=40)

    model_config = ConfigDict(populate_by_name=True)

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
    fiscal_responsavel_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("fiscal_responsavel_id", "fiscal_id"),
    )

    vencendo_em_dias: int | None = Field(default=None, ge=1, le=365)

    model_config = ConfigDict(populate_by_name=True)


class ContratoRead(ContratoBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


UserOut = UserRead


class ContratoOut(ContratoRead):
    fornecedor: FornecedorRead
    fiscal: UserOut | None = None
    gestor: UserOut | None = None
    secretaria: SecretariaRead
    alertas_ativos: int = 0

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


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


class ContratoPage(BaseModel):
    items: list[ContratoOut]
    total: int
    page: int
    limit: int
    pages: int
