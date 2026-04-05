import uuid
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.match import MatchJob, MatchStatus
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.match_repository import MatchRepository
from app.schemas.match import (
    JobDescriptionInput,
    MatchBatchResponse,
    MatchJobResponse,
    MatchListResponse,
    PaginationMeta,
)
from app.logger import get_logger, log_flow

logger = get_logger("match_service")

class MatchService:
    """Business logic for match job operations."""

    # Valid status values for filtering
    VALID_STATUSES: set[str] = {s.value for s in MatchStatus}

    def __init__(self, db: Session) -> None:
        self.db: Session = db
        self.match_repo: MatchRepository = MatchRepository(db)
        self.candidate_repo: CandidateRepository = CandidateRepository(db)

    def submit_batch(
        self, candidate_id: uuid.UUID, jobs: list[JobDescriptionInput]
    ) -> MatchBatchResponse:
        """Submit a batch of job descriptions for scoring.

        Validates the candidate exists, creates match jobs with status=pending,
        and returns them immediately.
        """
        with log_flow(logger, "service", "SubmitBatch", candidate_id=str(candidate_id), jobs_count=len(jobs)):
            # Validate candidate exists
            candidate = self.candidate_repo.get_by_id(candidate_id)
            if candidate is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "candidate_not_found",
                        "message": f"Candidate with ID {candidate_id} does not exist",
                    },
                )
    
            # Create match jobs
            match_jobs: list[MatchJob] = []
            for job_input in jobs:
                description: str = job_input.text or f"[URL] {job_input.url}"
                source_url: str | None = job_input.url
    
                match_job: MatchJob = MatchJob(
                    candidate_id=candidate_id,
                    job_description=description,
                    source_url=source_url,
                    status=MatchStatus.PENDING.value,
                )
                match_jobs.append(match_job)
    
            created_jobs: list[MatchJob] = self.match_repo.create_batch(match_jobs)
    
            # Enqueue the background jobs to the celery queue workers
            from app.worker import score_match_job
            for job in created_jobs:
                score_match_job.delay(str(job.id))
    
            return MatchBatchResponse(
                jobs=[MatchJobResponse.model_validate(j) for j in created_jobs],
                total=len(created_jobs),
            )

    def get_match(self, job_id: uuid.UUID) -> MatchJobResponse:
        """Get a single match job by ID."""
        with log_flow(logger, "service", "GetMatch", job_id=str(job_id)):
            job: MatchJob | None = self.match_repo.get_by_id(job_id)
            if job is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "match_not_found",
                        "message": f"Match job with ID {job_id} does not exist",
                    },
                )
            return MatchJobResponse.model_validate(job)

    def list_matches(
        self,
        candidate_id: uuid.UUID,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> MatchListResponse:
        """List match jobs for a candidate with optional filtering and pagination."""
        with log_flow(logger, "service", "ListMatches", candidate_id=str(candidate_id), status=status, limit=limit, offset=offset):
            # Validate candidate exists
            candidate = self.candidate_repo.get_by_id(candidate_id)
            if candidate is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "candidate_not_found",
                        "message": f"Candidate with ID {candidate_id} does not exist",
                    },
                )
    
            # Validate status if provided
            if status is not None and status not in self.VALID_STATUSES:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "invalid_status",
                        "message": f"Invalid status '{status}'. Must be one of: {', '.join(sorted(self.VALID_STATUSES))}",
                    },
                )
    
            # Clamp pagination
            limit = max(1, min(limit, 100))
            offset = max(0, offset)
    
            jobs: list[MatchJob]
            total: int
            jobs, total = self.match_repo.list_by_candidate(
                candidate_id=candidate_id,
                status=status,
                limit=limit,
                offset=offset,
            )
    
            return MatchListResponse(
                data=[MatchJobResponse.model_validate(j) for j in jobs],
                pagination=PaginationMeta(
                    total=total,
                    limit=limit,
                    offset=offset,
                    has_more=(offset + limit) < total,
                ),
            )

    def retry_match(self, job_id: uuid.UUID) -> MatchJobResponse:
        """Manually retry a failed match job."""
        with log_flow(logger, "service", "RetryMatch", job_id=str(job_id)):
            job: MatchJob | None = self.match_repo.get_by_id(job_id)
            if job is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "match_not_found",
                        "message": f"Match job with ID {job_id} does not exist",
                    },
                )

            if job.status == MatchStatus.COMPLETED.value:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "already_completed",
                        "message": "Cannot retry a completed job",
                    },
                )

            if job.status == MatchStatus.DEAD.value:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "job_is_dead",
                        "message": "Job has reached maximum retries and is dead",
                    },
                )

            # Reset status and retry count
            job.status = MatchStatus.PENDING.value
            job.retry_count = 0
            job.error_message = None
            self.db.commit()

            # Enqueue the background job
            from app.worker import score_match_job
            score_match_job.delay(str(job.id))

            return MatchJobResponse.model_validate(job)
