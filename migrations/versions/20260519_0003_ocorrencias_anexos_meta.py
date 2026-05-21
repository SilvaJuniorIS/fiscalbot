"""ocorrencias and anexos metadata

Revision ID: 20260519_0003
Revises: 20260519_0002
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa

revision = "20260519_0003"
down_revision = "20260519_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ocorrencias", sa.Column("fiscal_id", sa.Integer(), nullable=True))
    op.add_column("ocorrencias", sa.Column("tipo", sa.String(length=60), nullable=True))
    op.create_foreign_key(
        op.f("fk_ocorrencias_fiscal_id_users"),
        "ocorrencias",
        "users",
        ["fiscal_id"],
        ["id"],
    )
    op.add_column("anexos", sa.Column("uploaded_by_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("fk_anexos_uploaded_by_id_users"),
        "anexos",
        "users",
        ["uploaded_by_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(op.f("fk_anexos_uploaded_by_id_users"), "anexos", type_="foreignkey")
    op.drop_column("anexos", "uploaded_by_id")
    op.drop_constraint(op.f("fk_ocorrencias_fiscal_id_users"), "ocorrencias", type_="foreignkey")
    op.drop_column("ocorrencias", "tipo")
    op.drop_column("ocorrencias", "fiscal_id")
