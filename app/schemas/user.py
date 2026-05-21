from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    nome: str = Field(max_length=160)
    email: EmailStr = Field(max_length=255)
    role: UserRole = UserRole.fiscal
    secretaria_id: int | None = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    nome: str | None = Field(default=None, max_length=160)
    email: EmailStr | None = Field(default=None, max_length=255)
    role: UserRole | None = None
    secretaria_id: int | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: str
