"""Add scoring_method column to match_jobs table

Revision ID: 002
Revises: 001
Create Date: 2026-04-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add scoring_method column with a default value for existing rows
    op.add_column(
        "match_jobs",
        sa.Column(
            "scoring_method", 
            sa.String(20), 
            nullable=False, 
            server_default="rule-based"
        )
    )


def downgrade() -> None:
    op.drop_column("match_jobs", "scoring_method")
