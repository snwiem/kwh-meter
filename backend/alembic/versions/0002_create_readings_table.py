"""create readings table

Revision ID: 0002
Revises: 0001
Create Date: 2025-09-20

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers used by Alembic
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "readings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("zaehler_nr", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value_kwh", sa.Numeric(10, 1), nullable=False),
        sa.Column("comment", sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(["zaehler_nr"], ["meters.zaehler_nr"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_readings_zaehler_nr_timestamp",
        "readings",
        ["zaehler_nr", "timestamp"],
    )


def downgrade() -> None:
    op.drop_index("ix_readings_zaehler_nr_timestamp", table_name="readings")
    op.drop_table("readings")
