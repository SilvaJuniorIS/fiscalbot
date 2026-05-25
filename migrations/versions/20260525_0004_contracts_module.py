"""contracts module

Revision ID: 20260525_0004
Revises: 20260519_0003
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa

revision = "20260525_0004"
down_revision = "20260519_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contracts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("numero_contrato", sa.String(length=50), nullable=True),
        sa.Column("numero_aditivo", sa.String(length=50), nullable=True),
        sa.Column("fornecedor", sa.Text(), nullable=True),
        sa.Column("cnpj", sa.String(length=20), nullable=True),
        sa.Column("secretaria", sa.String(length=120), nullable=True),
        sa.Column("secretario", sa.Text(), nullable=True),
        sa.Column("gestor", sa.Text(), nullable=True),
        sa.Column("gestor_cpf", sa.String(length=14), nullable=True),
        sa.Column("fiscal", sa.Text(), nullable=True),
        sa.Column("fiscal_cpf", sa.String(length=14), nullable=True),
        sa.Column("objeto", sa.Text(), nullable=True),
        sa.Column("vigencia_texto", sa.Text(), nullable=True),
        sa.Column("inicio_vigencia", sa.Date(), nullable=True),
        sa.Column("fim_vigencia", sa.Date(), nullable=True),
        sa.Column("data_os", sa.Date(), nullable=True),
        sa.Column("processo_administrativo", sa.String(length=80), nullable=True),
        sa.Column("processo_execucao", sa.String(length=80), nullable=True),
        sa.Column("audesp_licitacao", sa.String(length=80), nullable=True),
        sa.Column("audesp_ajuste", sa.Text(), nullable=True),
        sa.Column("modalidade", sa.String(length=100), nullable=True),
        sa.Column("valor_total", sa.Numeric(14, 2), nullable=True),
        sa.Column("data_assinatura", sa.Date(), nullable=True),
        sa.Column("data_publicacao", sa.Date(), nullable=True),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("dias_para_vencimento", sa.Integer(), nullable=True),
        sa.Column("alerta_30", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("alerta_15", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("alerta_07", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("alerta_01", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contracts")),
    )
    op.create_index(op.f("ix_contracts_cnpj"), "contracts", ["cnpj"], unique=False)
    op.create_index(op.f("ix_contracts_fim_vigencia"), "contracts", ["fim_vigencia"], unique=False)
    op.create_index(op.f("ix_contracts_numero_contrato"), "contracts", ["numero_contrato"], unique=False)
    op.create_index(op.f("ix_contracts_secretaria"), "contracts", ["secretaria"], unique=False)
    op.create_index(op.f("ix_contracts_status"), "contracts", ["status"], unique=False)

    op.create_table(
        "contract_import_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("arquivo", sa.String(length=255), nullable=False),
        sa.Column("usuario", sa.String(length=255), nullable=True),
        sa.Column("linhas_processadas", sa.Integer(), nullable=False),
        sa.Column("linhas_importadas", sa.Integer(), nullable=False),
        sa.Column("linhas_com_erro", sa.Integer(), nullable=False),
        sa.Column("detalhes_erro", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contract_import_logs")),
    )


def downgrade() -> None:
    op.drop_table("contract_import_logs")
    op.drop_index(op.f("ix_contracts_status"), table_name="contracts")
    op.drop_index(op.f("ix_contracts_secretaria"), table_name="contracts")
    op.drop_index(op.f("ix_contracts_numero_contrato"), table_name="contracts")
    op.drop_index(op.f("ix_contracts_fim_vigencia"), table_name="contracts")
    op.drop_index(op.f("ix_contracts_cnpj"), table_name="contracts")
    op.drop_table("contracts")
