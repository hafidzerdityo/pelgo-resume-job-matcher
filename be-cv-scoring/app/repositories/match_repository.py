import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.match import MatchJob, MatchStatus
from app.logger import get_logger, log_flow

logger = get_logger("repository.match")


class MatchRepository:
    """Data access layer for match jobs."""

    def __init__(self, db: Session) -> None:
        self.db: Session = db

    def create(self, match_job: MatchJob) -> MatchJob:
        """Persist a new match job."""
        with log_flow(logger, "repository", "Create", candidate_id=str(match_job.candidate_id)):
            self.db.add(match_job)
            self.db.commit()
            self.db.refresh(match_job)
            return match_job

    def create_batch(self, match_jobs: list[MatchJob]) -> list[MatchJob]:
        """Persist a batch of match jobs in a single transaction."""
        with log_flow(logger, "repository", "CreateBatch", count=len(match_jobs)):
            self.db.add_all(match_jobs)
            self.db.commit()
            for job in match_jobs:
                self.db.refresh(job)
            return match_jobs

    def get_by_id(self, job_id: uuid.UUID) -> MatchJob | None:
        """Fetch a single match job by ID."""
        with log_flow(logger, "repository", "GetById", job_id=str(job_id)):
            stmt = select(MatchJob).where(MatchJob.id == job_id)
            return self.db.execute(stmt).scalar_one_or_none()

    def list_by_candidate(
        self,
        candidate_id: uuid.UUID,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[MatchJob], int]:
        """List match jobs for a candidate with optional status filter and pagination.

        Returns a tuple of (jobs, total_count).
        """
        with log_flow(logger, "repository", "ListByCandidate", candidate_id=str(candidate_id), status=status, limit=limit, offset=offset):
            base_query = select(MatchJob).where(MatchJob.candidate_id == candidate_id)
            count_query = select(func.count()).select_from(MatchJob).where(
                MatchJob.candidate_id == candidate_id
            )
    
            if status is not None:
                base_query = base_query.where(MatchJob.status == status)
                count_query = count_query.where(MatchJob.status == status)
    
            # Order by newest first
            base_query = base_query.order_by(MatchJob.created_at.desc())
            base_query = base_query.limit(limit).offset(offset)
    
            jobs: list[MatchJob] = list(self.db.execute(base_query).scalars().all())
            total: int = self.db.execute(count_query).scalar_one()
    
            return jobs, total

    def update_status(
        self,
        job_id: uuid.UUID,
        status: MatchStatus,
        error_message: str | None = None,
    ) -> MatchJob | None:
        """Update the status of a match job."""
        with log_flow(logger, "repository", "UpdateStatus", job_id=str(job_id), status=status.value):
            job: MatchJob | None = self.get_by_id(job_id)
            if job is None:
                return None
            job.status = status.value
            if error_message is not None:
                job.error_message = error_message
            self.db.commit()
            self.db.refresh(job)
            return job
