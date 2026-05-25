from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ContractBase(BaseModel):
    status: str | None = Field(default=None, max_length=50)
    numero_contrato: str | None = Field(default=None, max_length=50)
    numero_aditivo: str | None = Field(default=None, max_length=50)
    fornecedor: str | None = None
    cnpj: str | None = Field(default=None, max_length=20)
    secretaria: str | None = Field(default=None, max_length=120)
    secretario: str | None = None
    gestor: str | None = None
    gestor_cpf: str | None = Field(default=None, max_length=14)
    fiscal: str | None = None
    fiscal_cpf: str | None = Field(default=None, max_length=14)
    objeto: str | None = None
    vigencia_texto: str | None = None
    inicio_vigencia: date | None = None
    fim_vigencia: date | None = None
    data_os: date | None = None
    processo_administrativo: str | None = Field(default=None, max_length=80)
    processo_execucao: str | None = Field(default=None, max_length=80)
    audesp_licitacao: str | None = Field(default=None, max_length=80)
    audesp_ajuste: str | None = None
    modalidade: str | None = Field(default=None, max_length=100)
    valor_total: Decimal | None = None
    data_assinatura: date | None = None
    data_publicacao: date | None = None
    observacao: str | None = None
    dias_para_vencimento: int | None = None
    alerta_30: bool = False
    alerta_15: bool = False
    alerta_07: bool = False
    alerta_01: bool = False


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    status: str | None = Field(default=None, max_length=50)
    numero_contrato: str | None = Field(default=None, max_length=50)
    numero_aditivo: str | None = Field(default=None, max_length=50)
    fornecedor: str | None = None
    cnpj: str | None = Field(default=None, max_length=20)
    secretaria: str | None = Field(default=None, max_length=120)
    secretario: str | None = None
    gestor: str | None = None
    gestor_cpf: str | None = Field(default=None, max_length=14)
    fiscal: str | None = None
    fiscal_cpf: str | None = Field(default=None, max_length=14)
    objeto: str | None = None
    vigencia_texto: str | None = None
    inicio_vigencia: date | None = None
    fim_vigencia: date | None = None
    data_os: date | None = None
    processo_administrativo: str | None = Field(default=None, max_length=80)
    processo_execucao: str | None = Field(default=None, max_length=80)
    audesp_licitacao: str | None = Field(default=None, max_length=80)
    audesp_ajuste: str | None = None
    modalidade: str | None = Field(default=None, max_length=100)
    valor_total: Decimal | None = None
    data_assinatura: date | None = None
    data_publicacao: date | None = None
    observacao: str | None = None
    dias_para_vencimento: int | None = None
    alerta_30: bool | None = None
    alerta_15: bool | None = None
    alerta_07: bool | None = None
    alerta_01: bool | None = None


class ContractRead(ContractBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContractPage(BaseModel):
    items: list[ContractRead]
    total: int
    page: int
    limit: int
    pages: int


class ContractDashboard(BaseModel):
    contratos_ativos: int
    vencendo_em_30: int
    vencendo_em_15: int
    vencidos: int
    valor_total_contratado: Decimal


class ContractImportResult(BaseModel):
    importados: int
    ignorados: int
    erros: int
    linhas_processadas: int
    linhas_com_erro: int
    detalhes_erro: list[dict[str, str | int]]
