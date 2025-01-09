"""create facility table

Revision ID: 7f4287f670c8
Revises: 
Create Date: 2025-01-07 12:37:22.194022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f4287f670c8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "facility",
        sa.Column("uid", sa.Text, primary_key=True, index=True),
        sa.Column("segment", sa.Text, index=True),
        sa.Column("company", sa.Text),
        sa.Column("technology", sa.Text, index=True),
        sa.Column("investment_status", sa.Text),
        sa.Column("latitude", sa.Float),
        sa.Column("longitude", sa.Float),
        sa.Column("estimated_investment", sa.Integer, nullable=True, default=None),
        sa.Column("announcement_date", sa.Date, index=True),
)


def downgrade() -> None:
    op.drop_table("facility")
