"""contract notifications

Revision ID: 20260526_0005
Revises: 20260525_0004
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa

revision = "20260526_0005"
down_revision = "20260525_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contract_id", sa.Uuid(), nullable=False),
        sa.Column("tipo", sa.String(length=60), nullable=False),
        sa.Column("titulo", sa.String(length=180), nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("dias_para_vencimento", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], name=op.f("fk_notifications_contract_id_contracts")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
    )
    op.create_index(op.f("ix_notifications_contract_id"), "notifications", ["contract_id"], unique=False)
    op.create_index(op.f("ix_notifications_dias_para_vencimento"), "notifications", ["dias_para_vencimento"], unique=False)
    op.create_index(op.f("ix_notifications_tipo"), "notifications", ["tipo"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notifications_tipo"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_dias_para_vencimento"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_contract_id"), table_name="notifications")
    op.drop_table("notifications")
