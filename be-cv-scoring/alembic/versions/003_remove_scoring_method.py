"""Remove scoring_method column from match_jobs table

Revision ID: 003
Revises: 002
Create Date: 2026-04-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("match_jobs", "scoring_method")


def downgrade() -> None:
    op.add_column(
        "match_jobs",
        sa.Column(
            "scoring_method", 
            sa.String(20), 
            nullable=False, 
            server_default="llm"
        )
    )
