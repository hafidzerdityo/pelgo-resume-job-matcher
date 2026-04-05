import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate import CandidateProfile
from app.logger import get_logger, log_flow

logger = get_logger("repository.candidate")


class CandidateRepository:
    """Data access layer for candidate profiles."""

    def __init__(self, db: Session) -> None:
        self.db: Session = db

    def get_by_id(self, candidate_id: uuid.UUID) -> CandidateProfile | None:
        """Fetch a candidate profile by ID."""
        with log_flow(logger, "repository", "GetById", candidate_id=str(candidate_id)):
            stmt = select(CandidateProfile).where(CandidateProfile.id == candidate_id)
            return self.db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> CandidateProfile | None:
        """Fetch a candidate profile by email."""
        with log_flow(logger, "repository", "GetByEmail", email=email):
            stmt = select(CandidateProfile).where(CandidateProfile.email == email)
            return self.db.execute(stmt).scalar_one_or_none()

    def create(self, profile: CandidateProfile) -> CandidateProfile:
        """Create a new candidate profile."""
        with log_flow(logger, "repository", "Create", email=profile.email):
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            return profile

    def list_all(self, limit: int = 20, offset: int = 0) -> list[CandidateProfile]:
        """List all candidate profiles."""
        with log_flow(logger, "repository", "ListAll", limit=limit, offset=offset):
            stmt = (
                select(CandidateProfile)
                .order_by(CandidateProfile.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return list(self.db.execute(stmt).scalars().all())
