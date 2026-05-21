"""initial schema

Revision ID: 20260519_0001
Revises:
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa

revision = "20260519_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fornecedores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("razao_social", sa.String(length=220), nullable=False),
        sa.Column("cnpj", sa.String(length=18), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("telefone", sa.String(length=40), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_fornecedores")),
        sa.UniqueConstraint("cnpj", name=op.f("uq_fornecedores_cnpj")),
    )
    op.create_index(op.f("ix_fornecedores_cnpj"), "fornecedores", ["cnpj"], unique=False)
    op.create_index(op.f("ix_fornecedores_razao_social"), "fornecedores", ["razao_social"], unique=False)

    op.create_table(
        "indicadores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chave", sa.String(length=120), nullable=False),
        sa.Column("escopo", sa.String(length=120), nullable=False),
        sa.Column("valor", sa.Numeric(14, 2), nullable=False),
        sa.Column("competencia", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("valor >= 0", name=op.f("ck_indicadores_indicador_valor_nao_negativo")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_indicadores")),
    )
    op.create_index(op.f("ix_indicadores_chave"), "indicadores", ["chave"], unique=False)
    op.create_index(op.f("ix_indicadores_competencia"), "indicadores", ["competencia"], unique=False)
    op.create_index(op.f("ix_indicadores_escopo"), "indicadores", ["escopo"], unique=False)

    op.create_table(
        "secretarias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=180), nullable=False),
        sa.Column("sigla", sa.String(length=30), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_secretarias")),
        sa.UniqueConstraint("nome", name=op.f("uq_secretarias_nome")),
    )
    op.create_index(op.f("ix_secretarias_nome"), "secretarias", ["nome"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)

    op.create_table(
        "contratos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("numero", sa.String(length=80), nullable=False),
        sa.Column("orgao", sa.String(length=180), nullable=False),
        sa.Column("objeto", sa.Text(), nullable=False),
        sa.Column("valor", sa.Numeric(14, 2), nullable=False),
        sa.Column("inicio", sa.Date(), nullable=False),
        sa.Column("termino", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("secretaria_id", sa.Integer(), nullable=False),
        sa.Column("fornecedor_id", sa.Integer(), nullable=False),
        sa.Column("fiscal_responsavel_id", sa.Integer(), nullable=True),
        sa.Column("gestor_responsavel_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["fiscal_responsavel_id"], ["users.id"], name=op.f("fk_contratos_fiscal_responsavel_id_users")),
        sa.ForeignKeyConstraint(["fornecedor_id"], ["fornecedores.id"], name=op.f("fk_contratos_fornecedor_id_fornecedores")),
        sa.ForeignKeyConstraint(["gestor_responsavel_id"], ["users.id"], name=op.f("fk_contratos_gestor_responsavel_id_users")),
        sa.ForeignKeyConstraint(["secretaria_id"], ["secretarias.id"], name=op.f("fk_contratos_secretaria_id_secretarias")),
        sa.CheckConstraint("valor >= 0", name=op.f("ck_contratos_contrato_valor_nao_negativo")),
        sa.CheckConstraint("termino >= inicio", name=op.f("ck_contratos_contrato_periodo_valido")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contratos")),
        sa.UniqueConstraint("numero", name=op.f("uq_contratos_numero")),
    )
    op.create_index(op.f("ix_contratos_numero"), "contratos", ["numero"], unique=False)
    op.create_index(op.f("ix_contratos_orgao"), "contratos", ["orgao"], unique=False)
    op.create_index(op.f("ix_contratos_termino"), "contratos", ["termino"], unique=False)

    op.create_table(
        "logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("entidade", sa.String(length=120), nullable=False),
        sa.Column("entidade_id", sa.Integer(), nullable=False),
        sa.Column("acao", sa.String(length=80), nullable=False),
        sa.Column("antes", sa.JSON(), nullable=True),
        sa.Column("depois", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_logs_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_logs")),
    )
    op.create_index(op.f("ix_logs_acao"), "logs", ["acao"], unique=False)
    op.create_index(op.f("ix_logs_entidade"), "logs", ["entidade"], unique=False)
    op.create_index(op.f("ix_logs_entidade_id"), "logs", ["entidade_id"], unique=False)

    op.create_table(
        "alertas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contrato_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=60), nullable=False),
        sa.Column("titulo", sa.String(length=180), nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("data_referencia", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("enviado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["contrato_id"], ["contratos.id"], name=op.f("fk_alertas_contrato_id_contratos")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_alertas")),
    )
    op.create_index(op.f("ix_alertas_contrato_id"), "alertas", ["contrato_id"], unique=False)
    op.create_index(op.f("ix_alertas_data_referencia"), "alertas", ["data_referencia"], unique=False)
    op.create_index(op.f("ix_alertas_tipo"), "alertas", ["tipo"], unique=False)

    op.create_table(
        "anexos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contrato_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=40), nullable=False),
        sa.Column("nome_arquivo", sa.String(length=255), nullable=False),
        sa.Column("caminho_storage", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("versao", sa.Integer(), nullable=False),
        sa.Column("texto_ocr", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["contrato_id"], ["contratos.id"], name=op.f("fk_anexos_contrato_id_contratos")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_anexos")),
    )
    op.create_index(op.f("ix_anexos_contrato_id"), "anexos", ["contrato_id"], unique=False)

    op.create_table(
        "ocorrencias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contrato_id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=180), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("data_ocorrencia", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("plano_acao", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["contrato_id"], ["contratos.id"], name=op.f("fk_ocorrencias_contrato_id_contratos")),
        sa.CheckConstraint("latitude IS NULL OR latitude BETWEEN -90 AND 90", name=op.f("ck_ocorrencias_ocorrencia_latitude_valida")),
        sa.CheckConstraint("longitude IS NULL OR longitude BETWEEN -180 AND 180", name=op.f("ck_ocorrencias_ocorrencia_longitude_valida")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ocorrencias")),
    )
    op.create_index(op.f("ix_ocorrencias_contrato_id"), "ocorrencias", ["contrato_id"], unique=False)
    op.create_index(op.f("ix_ocorrencias_data_ocorrencia"), "ocorrencias", ["data_ocorrencia"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ocorrencias_data_ocorrencia"), table_name="ocorrencias")
    op.drop_index(op.f("ix_ocorrencias_contrato_id"), table_name="ocorrencias")
    op.drop_table("ocorrencias")
    op.drop_index(op.f("ix_anexos_contrato_id"), table_name="anexos")
    op.drop_table("anexos")
    op.drop_index(op.f("ix_alertas_tipo"), table_name="alertas")
    op.drop_index(op.f("ix_alertas_data_referencia"), table_name="alertas")
    op.drop_index(op.f("ix_alertas_contrato_id"), table_name="alertas")
    op.drop_table("alertas")
    op.drop_index(op.f("ix_logs_entidade_id"), table_name="logs")
    op.drop_index(op.f("ix_logs_entidade"), table_name="logs")
    op.drop_index(op.f("ix_logs_acao"), table_name="logs")
    op.drop_table("logs")
    op.drop_index(op.f("ix_contratos_termino"), table_name="contratos")
    op.drop_index(op.f("ix_contratos_orgao"), table_name="contratos")
    op.drop_index(op.f("ix_contratos_numero"), table_name="contratos")
    op.drop_table("contratos")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_secretarias_nome"), table_name="secretarias")
    op.drop_table("secretarias")
    op.drop_index(op.f("ix_indicadores_escopo"), table_name="indicadores")
    op.drop_index(op.f("ix_indicadores_competencia"), table_name="indicadores")
    op.drop_index(op.f("ix_indicadores_chave"), table_name="indicadores")
    op.drop_table("indicadores")
    op.drop_index(op.f("ix_fornecedores_razao_social"), table_name="fornecedores")
    op.drop_index(op.f("ix_fornecedores_cnpj"), table_name="fornecedores")
    op.drop_table("fornecedores")
