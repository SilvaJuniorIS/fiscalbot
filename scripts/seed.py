import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402

from app.models import (  # noqa: E402
    Contrato,
    Fornecedor,
    Secretaria,
    User,
)

from app.models.contrato import ContratoStatus  # noqa: E402
from app.models.user import UserRole  # noqa: E402


def get_or_create(session, model, lookup: dict, defaults: dict | None = None):
    instance = session.scalar(select(model).filter_by(**lookup))

    if instance:
        return instance

    instance = model(**lookup, **(defaults or {}))

    session.add(instance)
    session.flush()

    return instance


def seed():
    password_hash = hash_password(settings.admin_password)

    today = date.today()

    with SessionLocal() as session:
        secretarias = [
            get_or_create(session, Secretaria, {"nome": "Saude"}, {"sigla": "SMS"}),
            get_or_create(session, Secretaria, {"nome": "Educacao"}, {"sigla": "SME"}),
            get_or_create(session, Secretaria, {"nome": "Obras"}, {"sigla": "SMO"}),
            get_or_create(session, Secretaria, {"nome": "Administracao"}, {"sigla": "SMA"}),
            get_or_create(session, Secretaria, {"nome": "Financas"}, {"sigla": "SMF"}),
        ]

        fornecedores = [
            get_or_create(
                session,
                Fornecedor,
                {"cnpj": "12.345.678/0001-90"},
                {
                    "razao_social": "Vida Plena Medicamentos Ltda",
                    "email": "contratos@vidaplena.example",
                },
            ),
            get_or_create(
                session,
                Fornecedor,
                {"cnpj": "23.456.789/0001-01"},
                {
                    "razao_social": "Oficina Central Servicos Automotivos",
                    "email": "frota@oficina.example",
                },
            ),
        ]

        admin = get_or_create(
            session,
            User,
            {"email": settings.admin_email},
            {
                "nome": "Administrador FiscalBot",
                "hashed_password": password_hash,
                "role": UserRole.admin.value,
                "is_active": True,
            },
        )

        admin.hashed_password = password_hash

        gestor = get_or_create(
            session,
            User,
            {"email": "gestor@fiscalbot.com"},
            {
                "nome": "Gestor Demo",
                "hashed_password": password_hash,
                "role": UserRole.gestor.value,
                "secretaria_id": secretarias[0].id,
                "is_active": True,
            },
        )

        fiscal = get_or_create(
            session,
            User,
            {"email": "fiscal@fiscalbot.com"},
            {
                "nome": "Fiscal Demo",
                "hashed_password": password_hash,
                "role": UserRole.fiscal.value,
                "secretaria_id": secretarias[0].id,
                "is_active": True,
            },
        )

        contratos = [
            (
                "001/2026",
                secretarias[0],
                120,
                ContratoStatus.ativo.value,
                fornecedores[0],
                "Fornecimento de medicamentos hospitalares",
                "850000.00",
            ),
            (
                "002/2026",
                secretarias[1],
                25,
                ContratoStatus.critico.value,
                fornecedores[1],
                "Manutencao da frota escolar",
                "120000.00",
            ),
            (
                "003/2025",
                secretarias[2],
                -10,
                ContratoStatus.encerrado.value,
                fornecedores[0],
                "Reforma de unidade basica de saude",
                "420000.00",
            ),
            (
                "004/2026",
                secretarias[0],
                300,
                ContratoStatus.ativo.value,
                fornecedores[0],
                "Aquisição de insumos hospitalares",
                "1350000.00",
            ),
            (
                "005/2026",
                secretarias[1],
                90,
                ContratoStatus.alerta.value,
                fornecedores[1],
                "Merenda escolar municipal",
                "980000.00",
            ),
            (
                "006/2026",
                secretarias[2],
                15,
                ContratoStatus.critico.value,
                fornecedores[1],
                "Pavimentacao asfaltica bairro central",
                "4200000.00",
            ),
            (
                "007/2026",
                secretarias[3],
                180,
                ContratoStatus.ativo.value,
                fornecedores[0],
                "Licenciamento de software de gestao",
                "250000.00",
            ),
            (
                "008/2026",
                secretarias[4],
                60,
                ContratoStatus.alerta.value,
                fornecedores[1],
                "Consultoria contabil e financeira",
                "180000.00",
            ),
            (
                "009/2026",
                secretarias[0],
                45,
                ContratoStatus.alerta.value,
                fornecedores[0],
                "Servicos laboratoriais",
                "340000.00",
            ),
            (
                "010/2026",
                secretarias[1],
                365,
                ContratoStatus.ativo.value,
                fornecedores[1],
                "Transporte escolar rural",
                "2200000.00",
            ),
            (
                "011/2026",
                secretarias[2],
                -30,
                ContratoStatus.encerrado.value,
                fornecedores[1],
                "Construcao de ponte vicinal",
                "3100000.00",
            ),
            (
                "012/2026",
                secretarias[3],
                20,
                ContratoStatus.critico.value,
                fornecedores[0],
                "Suporte tecnico de TI",
                "95000.00",
            ),
            (
                "013/2026",
                secretarias[4],
                730,
                ContratoStatus.ativo.value,
                fornecedores[1],
                "Digitalizacao de arquivos publicos",
                "450000.00",
            ),
            (
                "014/2026",
                secretarias[0],
                10,
                ContratoStatus.critico.value,
                fornecedores[0],
                "Fornecimento de oxigenio hospitalar",
                "780000.00",
            ),
            (
                "015/2026",
                secretarias[1],
                150,
                ContratoStatus.ativo.value,
                fornecedores[1],
                "Aquisição de mobiliario escolar",
                "290000.00",
            ),
            (
                "016/2026",
                secretarias[2],
                40,
                ContratoStatus.alerta.value,
                fornecedores[1],
                "Manutencao de iluminacao publica",
                "610000.00",
            ),
            (
                "017/2026",
                secretarias[3],
                -5,
                ContratoStatus.encerrado.value,
                fornecedores[0],
                "Atualizacao de servidores internos",
                "135000.00",
            ),
            (
                "018/2026",
                secretarias[4],
                210,
                ContratoStatus.ativo.value,
                fornecedores[1],
                "Treinamento de servidores municipais",
                "99000.00",
            ),
            (
                "019/2026",
                secretarias[0],
                18,
                ContratoStatus.critico.value,
                fornecedores[0],
                "Servico de ambulancias terceirizadas",
                "1700000.00",
            ),
            (
                "020/2026",
                secretarias[1],
                80,
                ContratoStatus.alerta.value,
                fornecedores[1],
                "Compra de uniformes escolares",
                "560000.00",
            ),
            (
                "021/2026",
                secretarias[2],
                540,
                ContratoStatus.ativo.value,
                fornecedores[1],
                "Recapeamento viario urbano",
                "5000000.00",
            ),
            (
                "022/2026",
                secretarias[3],
                12,
                ContratoStatus.critico.value,
                fornecedores[0],
                "Firewall e seguranca de rede",
                "145000.00",
            ),
            (
                "023/2026",
                secretarias[4],
                95,
                ContratoStatus.alerta.value,
                fornecedores[1],
                "Auditoria tributaria municipal",
                "320000.00",
            ),
            (
                "024/2026",
                secretarias[0],
                400,
                ContratoStatus.ativo.value,
                fornecedores[0],
                "Gestao integrada de prontuarios",
                "890000.00",
            ),
        ]

        for numero, secretaria, dias, status, fornecedor, objeto, valor in contratos:
            get_or_create(
                session,
                Contrato,
                {"numero": numero},
                {
                    "orgao": "Prefeitura Municipal",
                    "objeto": objeto,
                    "valor": Decimal(valor),
                    "inicio": today - timedelta(days=180),
                    "termino": today + timedelta(days=dias),
                    "status": status,
                    "secretaria_id": secretaria.id,
                    "fornecedor_id": fornecedor.id,
                    "fiscal_responsavel_id": fiscal.id,
                    "gestor_responsavel_id": gestor.id,
                },
            )

        session.commit()

    print("Seed concluido.")
    print(f"Admin: {settings.admin_email} / {settings.admin_password}")


if __name__ == "__main__":
    seed()
