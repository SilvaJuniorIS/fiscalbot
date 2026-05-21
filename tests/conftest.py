from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.session import Base, get_db
from app.main import app
from app.models import alerta, anexo, contrato, fornecedor, indicador, log_auditoria, ocorrencia, secretaria, user  # noqa: F401
from app.models.secretaria import Secretaria
from app.models.user import User, UserRole

TEST_PASSWORD = "fiscalbot123"


@pytest.fixture
def db_session() -> Generator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    session = session_factory()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient, admin_user: User) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": admin_user.email, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_user(db_session: Session) -> User:
    secretaria_row = Secretaria(nome="Administracao", sigla="SMA", is_active=True)
    db_session.add(secretaria_row)
    db_session.flush()

    admin = User(
        nome="Admin",
        email="admin@example.com",
        hashed_password=hash_password(TEST_PASSWORD),
        role=UserRole.admin.value,
        secretaria_id=secretaria_row.id,
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin
