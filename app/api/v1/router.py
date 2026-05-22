from fastapi import APIRouter

from app.api.v1.routes import (
    alertas,
    auditoria,
    auth,
    contratos,
    dashboard,
    documentos,
    fiscalizacao,
    fornecedores,
    importacao,
    secretarias,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(secretarias.router, prefix="/secretarias", tags=["secretarias"])
api_router.include_router(fornecedores.router, prefix="/fornecedores", tags=["fornecedores"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(contratos.router, prefix="/contratos", tags=["contratos"])
api_router.include_router(alertas.router, prefix="/alertas", tags=["alertas"])
api_router.include_router(documentos.router, tags=["documentos"])
api_router.include_router(fiscalizacao.router, prefix="/fiscalizacao", tags=["fiscalizacao"])
api_router.include_router(auditoria.router, prefix="/auditoria", tags=["auditoria"])
api_router.include_router(importacao.router, prefix="/importacao", tags=["importacao"])
