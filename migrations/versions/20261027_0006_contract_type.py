"""Classify existing records without deleting or renumbering them."""

import sqlalchemy as sa
from alembic import op

revision = "20261027_0006"
down_revision = "20260526_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "contracts", sa.Column("tipo", sa.String(20), nullable=False, server_default="contrato")
    )
    op.execute("UPDATE contracts SET tipo = 'ata' WHERE upper(trim(numero_contrato)) LIKE 'ATA %'")
    op.create_index("ix_contracts_tipo", "contracts", ["tipo"])


def downgrade() -> None:
    op.drop_index("ix_contracts_tipo", table_name="contracts")
    op.drop_column("contracts", "tipo")
