from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SecretariaBase(BaseModel):
    nome: str = Field(max_length=180)
    sigla: str | None = Field(default=None, max_length=30)
    is_active: bool = True


class SecretariaCreate(SecretariaBase):
    pass


class SecretariaUpdate(BaseModel):
    nome: str | None = Field(default=None, max_length=180)
    sigla: str | None = Field(default=None, max_length=30)
    is_active: bool | None = None


class SecretariaRead(SecretariaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

