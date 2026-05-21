from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FornecedorBase(BaseModel):
    razao_social: str = Field(max_length=220)
    cnpj: str = Field(max_length=18)
    email: str | None = Field(default=None, max_length=255)
    telefone: str | None = Field(default=None, max_length=40)
    is_active: bool = True


class FornecedorCreate(FornecedorBase):
    pass


class FornecedorUpdate(BaseModel):
    razao_social: str | None = Field(default=None, max_length=220)
    cnpj: str | None = Field(default=None, max_length=18)
    email: str | None = Field(default=None, max_length=255)
    telefone: str | None = Field(default=None, max_length=40)
    is_active: bool | None = None


class FornecedorRead(FornecedorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

