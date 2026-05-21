from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.user import User
from app.repositories import user_repository


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = user_repository.get_by_email(db, email)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
