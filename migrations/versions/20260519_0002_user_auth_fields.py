"""user auth fields

Revision ID: 20260519_0002
Revises: 20260519_0001
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa

revision = "20260519_0002"
down_revision = "20260519_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("secretaria_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("fk_users_secretaria_id_secretarias"),
        "users",
        "secretarias",
        ["secretaria_id"],
        ["id"],
    )
    op.add_column("users", sa.Column("hashed_password", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_constraint(op.f("fk_users_secretaria_id_secretarias"), "users", type_="foreignkey")
    op.drop_column("users", "secretaria_id")
    op.drop_column("users", "hashed_password")
