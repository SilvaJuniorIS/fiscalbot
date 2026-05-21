from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.fornecedor import Fornecedor
from app.schemas.fornecedor import FornecedorCreate, FornecedorRead, FornecedorUpdate

router = APIRouter()


@router.get("", response_model=list[FornecedorRead])
def list_fornecedores(
    db: Annotated[Session, Depends(get_db)],
    search: Annotated[str | None, Query(max_length=120)] = None,
    is_active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Fornecedor]:
    stmt = select(Fornecedor).order_by(Fornecedor.razao_social.asc()).limit(limit).offset(offset)
    if search:
        term = f"%{search}%"
        stmt = stmt.where(Fornecedor.razao_social.ilike(term) | Fornecedor.cnpj.ilike(term))
    if is_active is not None:
        stmt = stmt.where(Fornecedor.is_active == is_active)
    return list(db.scalars(stmt))


@router.post("", response_model=FornecedorRead, status_code=status.HTTP_201_CREATED)
def create_fornecedor(
    payload: FornecedorCreate, db: Annotated[Session, Depends(get_db)]
) -> Fornecedor:
    fornecedor = Fornecedor(**payload.model_dump())
    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor


@router.get("/{fornecedor_id}", response_model=FornecedorRead)
def get_fornecedor(fornecedor_id: int, db: Annotated[Session, Depends(get_db)]) -> Fornecedor:
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if fornecedor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor nao encontrado"
        )
    return fornecedor


@router.patch("/{fornecedor_id}", response_model=FornecedorRead)
def update_fornecedor(
    fornecedor_id: int, payload: FornecedorUpdate, db: Annotated[Session, Depends(get_db)]
) -> Fornecedor:
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if fornecedor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor nao encontrado"
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(fornecedor, field, value)

    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor


@router.delete("/{fornecedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fornecedor(fornecedor_id: int, db: Annotated[Session, Depends(get_db)]) -> None:
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if fornecedor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor nao encontrado"
        )
    db.delete(fornecedor)
    db.commit()
