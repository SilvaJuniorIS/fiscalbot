import socket
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.services.dashboard import get_dashboard_data, get_demo_dashboard_data

router = APIRouter()


def database_port_is_reachable(timeout: float = 0.35) -> bool:
    url = make_url(settings.database_url)
    host = url.host
    port = url.port or 5432
    if not host:
        return True
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@router.get("")
def read_dashboard(db: Annotated[Session, Depends(get_db)]) -> dict[str, Any]:
    if not database_port_is_reachable():
        return get_demo_dashboard_data()
    try:
        return get_dashboard_data(db)
    except SQLAlchemyError:
        return get_demo_dashboard_data()
