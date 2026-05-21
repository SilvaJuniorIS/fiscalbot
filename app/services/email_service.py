import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.models.alerta import Alerta
from app.models.contrato import Contrato

logger = logging.getLogger(__name__)


def send_alert_email(user_email: str, alerta: Alerta, contrato: Contrato) -> bool:
    if not settings.smtp_host:
        logger.info(
            "SMTP nao configurado; alerta %s para %s (contrato %s)",
            alerta.id,
            user_email,
            contrato.numero,
        )
        return False

    dias = (contrato.termino - alerta.data_referencia).days if alerta.data_referencia else "—"
    body = (
        f"FiscalBot — Alerta de contrato\n\n"
        f"Contrato: {contrato.numero}\n"
        f"Tipo: {alerta.tipo}\n"
        f"Titulo: {alerta.titulo}\n"
        f"Mensagem: {alerta.mensagem}\n"
        f"Data de referencia: {alerta.data_referencia}\n"
        f"Dias restantes (aprox.): {dias}\n"
    )
    message = EmailMessage()
    message["Subject"] = f"[FiscalBot] {alerta.titulo}"
    message["From"] = settings.smtp_from
    message["To"] = user_email
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_pass)
            server.send_message(message)
        return True
    except OSError as exc:
        logger.warning("Falha ao enviar e-mail para %s: %s", user_email, exc)
        return False
