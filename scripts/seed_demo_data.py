from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.alerta import Alerta
from app.models.contrato import Contrato
from app.models.fornecedor import Fornecedor
from app.models.secretaria import Secretaria
from app.models.user import User


def get_or_create(session, model, lookup: dict, defaults: dict | None = None):
    instance = session.scalar(select(model).filter_by(**lookup))
    if instance is not None:
        return instance

    instance = model(**lookup, **(defaults or {}))
    session.add(instance)
    session.flush()
    return instance


DEMO_PASSWORD = "fiscalbot123"


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    password_hash = hash_password(DEMO_PASSWORD)
    today = date.today()

    with SessionLocal() as session:
        saude = get_or_create(session, Secretaria, {"nome": "Saude"}, {"sigla": "SMS"})
        educacao = get_or_create(session, Secretaria, {"nome": "Educacao"}, {"sigla": "SME"})
        obras = get_or_create(session, Secretaria, {"nome": "Obras"}, {"sigla": "SMO"})
        administracao = get_or_create(
            session, Secretaria, {"nome": "Administracao"}, {"sigla": "SMA"}
        )

        fornecedor_medicamentos = get_or_create(
            session,
            Fornecedor,
            {"cnpj": "12.345.678/0001-90"},
            {
                "razao_social": "Vida Plena Medicamentos Ltda",
                "email": "contratos@vidaplena.example",
                "telefone": "(11) 3000-1000",
            },
        )
        fornecedor_frota = get_or_create(
            session,
            Fornecedor,
            {"cnpj": "23.456.789/0001-01"},
            {
                "razao_social": "Oficina Central Servicos Automotivos",
                "email": "licitacoes@oficinacentral.example",
                "telefone": "(11) 3000-2000",
            },
        )
        fornecedor_limpeza = get_or_create(
            session,
            Fornecedor,
            {"cnpj": "34.567.890/0001-12"},
            {
                "razao_social": "LimpaMais Conservacao Predial",
                "email": "publico@limpamais.example",
                "telefone": "(11) 3000-3000",
            },
        )

        fiscal = get_or_create(
            session,
            User,
            {"email": "fiscal@fiscalbot.local"},
            {
                "nome": "Fiscal de Contratos",
                "role": "fiscal",
                "hashed_password": password_hash,
                "secretaria_id": saude.id,
            },
        )
        gestor = get_or_create(
            session,
            User,
            {"email": "gestor@fiscalbot.local"},
            {
                "nome": "Gestor de Contratos",
                "role": "gestor",
                "hashed_password": password_hash,
                "secretaria_id": administracao.id,
            },
        )
        admin = get_or_create(
            session,
            User,
            {"email": "admin@fiscalbot.local"},
            {
                "nome": "Administrador FiscalBot",
                "role": "admin",
                "hashed_password": password_hash,
            },
        )
        for demo_user in (fiscal, gestor, admin):
            demo_user.hashed_password = password_hash
            session.add(demo_user)

        contratos = [
            {
                "numero": "012/2025",
                "orgao": "Prefeitura Municipal",
                "objeto": "Fornecimento de medicamentos essenciais",
                "valor": Decimal("850000.00"),
                "inicio": today - timedelta(days=210),
                "termino": today + timedelta(days=12),
                "secretaria_id": saude.id,
                "fornecedor_id": fornecedor_medicamentos.id,
                "fiscal_responsavel_id": fiscal.id,
                "gestor_responsavel_id": gestor.id,
                "tags": "saude,medicamentos,critico",
            },
            {
                "numero": "044/2024",
                "orgao": "Prefeitura Municipal",
                "objeto": "Manutencao preventiva da frota municipal",
                "valor": Decimal("420000.00"),
                "inicio": today - timedelta(days=320),
                "termino": today + timedelta(days=24),
                "secretaria_id": administracao.id,
                "fornecedor_id": fornecedor_frota.id,
                "fiscal_responsavel_id": fiscal.id,
                "gestor_responsavel_id": gestor.id,
                "tags": "frota,manutencao",
            },
            {
                "numero": "078/2024",
                "orgao": "Prefeitura Municipal",
                "objeto": "Limpeza e conservacao de predios publicos",
                "valor": Decimal("1200000.00"),
                "inicio": today - timedelta(days=280),
                "termino": today + timedelta(days=43),
                "secretaria_id": educacao.id,
                "fornecedor_id": fornecedor_limpeza.id,
                "fiscal_responsavel_id": fiscal.id,
                "gestor_responsavel_id": gestor.id,
                "tags": "limpeza,servicos-continuados",
            },
            {
                "numero": "103/2025",
                "orgao": "Prefeitura Municipal",
                "objeto": "Pequenas obras de manutencao em unidades escolares",
                "valor": Decimal("675000.00"),
                "inicio": today - timedelta(days=60),
                "termino": today + timedelta(days=170),
                "secretaria_id": obras.id,
                "fornecedor_id": fornecedor_limpeza.id,
                "fiscal_responsavel_id": fiscal.id,
                "gestor_responsavel_id": admin.id,
                "tags": "obras,educacao",
            },
        ]

        for item in contratos:
            contrato = get_or_create(
                session,
                Contrato,
                {"numero": item["numero"]},
                {key: value for key, value in item.items() if key != "numero"},
            )
            alerta_key = {
                "contrato_id": contrato.id,
                "tipo": "vencimento",
                "data_referencia": contrato.termino,
            }
            get_or_create(
                session,
                Alerta,
                alerta_key,
                {
                    "titulo": f"Contrato {contrato.numero} proximo do vencimento",
                    "mensagem": "Avaliar renovacao, prorrogacao ou nova contratacao.",
                    "status": "pendente",
                },
            )

        session.commit()


if __name__ == "__main__":
    seed()
    print("Dados de demonstracao inseridos com sucesso.")
    print(f"Senha padrao dos usuarios demo: {DEMO_PASSWORD}")

