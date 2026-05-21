from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class AlertaBase(BaseModel):
    contrato_id: int
    tipo: str = Field(max_length=60)
    titulo: str = Field(max_length=180)
    mensagem: str
    data_referencia: date
    status: str = "pendente"
    enviado_em: datetime | None = None


class AlertaCreate(AlertaBase):
    pass


class AlertaUpdate(BaseModel):
    status: str | None = Field(default=None, max_length=40)
    enviado_em: datetime | None = None


class AlertaRead(AlertaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

