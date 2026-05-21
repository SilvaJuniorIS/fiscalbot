from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def create(db: Session, payload: UserCreate) -> User:
    data = payload.model_dump(exclude={"password"})
    user = User(**data, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, user: User, payload: UserUpdate) -> User:
    for field, value in payload.model_dump(exclude_unset=True, exclude={"password"}).items():
        setattr(user, field, value)
    if payload.password is not None:
        user.hashed_password = hash_password(payload.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def deactivate(db: Session, user: User) -> User:
    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_all(
    db: Session,
    *,
    search: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[User]:
    stmt = select(User).order_by(User.nome.asc()).limit(limit).offset(offset)
    if search:
        term = f"%{search}%"
        stmt = stmt.where(User.nome.ilike(term) | User.email.ilike(term))
    if role:
        stmt = stmt.where(User.role == role)
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    return list(db.scalars(stmt))
