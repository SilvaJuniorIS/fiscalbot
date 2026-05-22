"""Domain models."""
from .anexo import Anexo
from .alerta import Alerta
from .contrato import Contrato
from .fornecedor import Fornecedor
from .indicador import Indicador
from .log_auditoria import LogAuditoria
from .ocorrencia import Ocorrencia
from .secretaria import Secretaria
from .user import User

__all__ = [
    "Alerta",
    "Anexo",
    "Contrato",
    "Fornecedor",
    "Indicador",
    "LogAuditoria",
    "Ocorrencia",
    "Secretaria",
    "User",
]
