from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ContractBase(BaseModel):
    tipo: Literal["contrato", "ata"] = "contrato"
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
    tipo: Literal["contrato", "ata"] | None = None
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

    situacao: str = "ativo"
    dados_pendentes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def classify(self):
        self.dias_para_vencimento = (
            (self.fim_vigencia - date.today()).days if self.fim_vigencia else None
        )
        administrative = (self.status or "").lower()
        if administrative in {"encerrado", "suspenso", "cancelado"}:
            self.situacao = administrative
        elif self.dias_para_vencimento is None:
            self.situacao = "sem_vencimento"
        elif self.dias_para_vencimento < 0:
            self.situacao = "vencido"
        elif self.dias_para_vencimento <= 30:
            self.situacao = "vencendo"
        else:
            self.situacao = "ativo"
        labels = {
            "numero_contrato": "Numero",
            "fornecedor": "Fornecedor",
            "secretaria": "Secretaria",
            "objeto": "Objeto",
            "fim_vigencia": "Vencimento",
            "valor_total": "Valor",
            "gestor": "Gestor",
            "fiscal": "Fiscal",
        }
        self.dados_pendentes = [
            label
            for field, label in labels.items()
            if getattr(self, field) is None
            or (isinstance(getattr(self, field), str) and not getattr(self, field).strip())
        ]
        return self

    model_config = ConfigDict(from_attributes=True)


class ContractPage(BaseModel):
    items: list[ContractRead]
    total: int
    page: int
    limit: int
    pages: int


class ContractDashboard(BaseModel):
    total_registros: int = 0
    total_contratos: int = 0
    total_atas: int = 0
    dados_incompletos: int = 0
    grupos_duplicados: int = 0
    duplicados: list[ContractRead] = Field(default_factory=list)
    prioridades: list[ContractRead] = Field(default_factory=list)
    contratos_ativos: int
    vencendo_em_30: int
    vencendo_em_15: int
    vencidos: int
    valor_total_contratado: Decimal
    por_secretaria: list[dict[str, str | int]] = Field(default_factory=list)
    por_status: list[dict[str, str | int]] = Field(default_factory=list)
    ultimos_contratos: list[ContractRead] = Field(default_factory=list)


class ContractImportResult(BaseModel):
    atualizados: int = 0
    duplicados: int = 0
    importados: int
    ignorados: int
    erros: int
    linhas_processadas: int
    linhas_com_erro: int
    detalhes_erro: list[dict[str, str | int]]
