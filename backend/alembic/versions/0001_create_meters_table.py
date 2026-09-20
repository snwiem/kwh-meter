"""create meters table

Revision ID: 0001
Revises:
Create Date: 2025-09-20

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers used by Alembic
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "meters",
        sa.Column("zaehler_nr", sa.String(), nullable=False),
        sa.Column("street", sa.String(), nullable=False),
        sa.Column("house_number", sa.String(), nullable=False),
        sa.Column("postal_code", sa.String(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("zaehler_nr"),
    )


def downgrade() -> None:
    op.drop_table("meters")
