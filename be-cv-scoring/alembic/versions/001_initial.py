"""Initial migration: create candidate_profiles and match_jobs tables

Revision ID: 001
Revises:
Create Date: 2026-04-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Candidate profiles
    op.create_table(
        "candidate_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("skills", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("experience_years", sa.Integer, nullable=False, server_default="0"),
        sa.Column("location", sa.String(255), nullable=False, server_default=""),
        sa.Column("seniority", sa.String(50), nullable=False, server_default="mid"),
        sa.Column("resume_text", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Match jobs
    op.create_table(
        "match_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("job_description", sa.Text, nullable=False),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("overall_score", sa.Float, nullable=True),
        sa.Column("skill_score", sa.Float, nullable=True),
        sa.Column("experience_score", sa.Float, nullable=True),
        sa.Column("location_score", sa.Float, nullable=True),
        sa.Column("matched_skills", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("missing_skills", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("recommendation", sa.Text, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("retry_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Index for faster lookups by candidate and status
    op.create_index(
        "ix_match_jobs_candidate_status",
        "match_jobs",
        ["candidate_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_match_jobs_candidate_status", table_name="match_jobs")
    op.drop_table("match_jobs")
    op.drop_table("candidate_profiles")
