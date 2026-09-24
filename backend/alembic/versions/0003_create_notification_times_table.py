"""create notification_times table

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-24

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers used by Alembic
revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "notification_times",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("time", sa.Time(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("time"),
    )


def downgrade() -> None:
    op.drop_table("notification_times")
