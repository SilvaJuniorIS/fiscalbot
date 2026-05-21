from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.ocorrencia import OcorrenciaStatus, OcorrenciaTipo
from app.schemas.contrato import ContratoRead
from app.schemas.user import UserRead


class OcorrenciaCreate(BaseModel):
    titulo: str = Field(max_length=180)
    descricao: str
    tipo: OcorrenciaTipo = OcorrenciaTipo.vistoria
    data_ocorrencia: date | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    plano_acao: str | None = None


class OcorrenciaUpdate(BaseModel):
    descricao: str | None = None
    status: OcorrenciaStatus | None = None
    plano_acao: str | None = None


class OcorrenciaOut(BaseModel):
    id: int
    contrato_id: int
    titulo: str
    descricao: str
    tipo: str | None
    data_ocorrencia: date
    status: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    plano_acao: str | None = None
    fiscal: UserRead | None = None
    contrato: ContratoRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FiscalizacaoResumo(BaseModel):
    vistorias_mes: int
    ocorrencias_abertas: int
    conformes: int
    com_ressalva: int
    com_pendencia: int
