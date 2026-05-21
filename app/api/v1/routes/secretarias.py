from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.secretaria import Secretaria
from app.schemas.secretaria import SecretariaCreate, SecretariaRead, SecretariaUpdate

router = APIRouter()


@router.get("", response_model=list[SecretariaRead])
def list_secretarias(
    db: Annotated[Session, Depends(get_db)],
    search: Annotated[str | None, Query(max_length=120)] = None,
    is_active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Secretaria]:
    stmt = select(Secretaria).order_by(Secretaria.nome.asc()).limit(limit).offset(offset)
    if search:
        term = f"%{search}%"
        stmt = stmt.where(Secretaria.nome.ilike(term) | Secretaria.sigla.ilike(term))
    if is_active is not None:
        stmt = stmt.where(Secretaria.is_active == is_active)
    return list(db.scalars(stmt))


@router.post("", response_model=SecretariaRead, status_code=status.HTTP_201_CREATED)
def create_secretaria(
    payload: SecretariaCreate, db: Annotated[Session, Depends(get_db)]
) -> Secretaria:
    secretaria = Secretaria(**payload.model_dump())
    db.add(secretaria)
    db.commit()
    db.refresh(secretaria)
    return secretaria


@router.get("/{secretaria_id}", response_model=SecretariaRead)
def get_secretaria(secretaria_id: int, db: Annotated[Session, Depends(get_db)]) -> Secretaria:
    secretaria = db.get(Secretaria, secretaria_id)
    if secretaria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Secretaria nao encontrada"
        )
    return secretaria


@router.patch("/{secretaria_id}", response_model=SecretariaRead)
def update_secretaria(
    secretaria_id: int, payload: SecretariaUpdate, db: Annotated[Session, Depends(get_db)]
) -> Secretaria:
    secretaria = db.get(Secretaria, secretaria_id)
    if secretaria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Secretaria nao encontrada"
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(secretaria, field, value)

    db.add(secretaria)
    db.commit()
    db.refresh(secretaria)
    return secretaria


@router.delete("/{secretaria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_secretaria(secretaria_id: int, db: Annotated[Session, Depends(get_db)]) -> None:
    secretaria = db.get(Secretaria, secretaria_id)
    if secretaria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Secretaria nao encontrada"
        )
    db.delete(secretaria)
    db.commit()
