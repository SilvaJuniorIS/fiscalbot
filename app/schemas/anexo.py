from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserRead


class AnexoOut(BaseModel):
    id: int
    contrato_id: int
    nome_arquivo: str = Field(validation_alias="nome_arquivo")
    tipo: str
    versao: int
    uploaded_by: UserRead | None = None
    created_at: datetime
    url: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AnexoUploadMeta(BaseModel):
    tipo: str = Field(max_length=40)
    versao: int | None = None
