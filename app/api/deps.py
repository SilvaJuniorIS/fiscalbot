from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories import user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    email = decode_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_repository.get_by_email(db, email)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inativo ou inexistente",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(*roles: UserRole):
    allowed = {role.value for role in roles}

    def checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissao insuficiente para esta operacao",
            )
        return current_user

    return checker


def get_scoped_secretaria_ids(
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[int] | None:
    if current_user.role in {UserRole.admin.value, UserRole.auditor.value}:
        return None
    if current_user.secretaria_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario sem secretaria vinculada",
        )
    return [current_user.secretaria_id]


def assert_secretaria_in_scope(secretaria_id: int, scoped_ids: list[int] | None) -> None:
    if scoped_ids is not None and secretaria_id not in scoped_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contrato fora do escopo da sua secretaria",
        )
