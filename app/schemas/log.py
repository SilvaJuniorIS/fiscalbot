from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserRead


class LogOut(BaseModel):
    id: int
    user: UserRead | None = None
    entidade: str
    entidade_id: int
    acao: str
    antes: dict[str, Any] | None = None
    depois: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
