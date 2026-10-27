"""Create the deployment administrator once; never reset an existing password."""

from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import User
from app.models.user import UserRole


def bootstrap_admin() -> None:
    if settings.secret_key == "change-me-in-production" or len(settings.secret_key) < 32:
        raise ValueError("Configure SECRET_KEY com pelo menos 32 caracteres")
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == settings.admin_email)):
            return
        password = settings.admin_password
        if password == "fiscalbot123" or not 12 <= len(password.encode()) <= 72:
            raise ValueError("Configure ADMIN_PASSWORD com 12 a 72 bytes, sem usar a senha demo")
        db.add(
            User(
                nome="Administrador FiscalBot",
                email=settings.admin_email,
                hashed_password=hash_password(password),
                role=UserRole.admin.value,
                is_active=True,
            )
        )
        db.commit()
    print("Administrador inicial criado; credenciais omitidas.")


if __name__ == "__main__":
    bootstrap_admin()
