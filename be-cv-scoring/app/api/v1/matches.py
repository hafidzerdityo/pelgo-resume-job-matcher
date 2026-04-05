from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.logger import get_logger, log_flow
from app.schemas.match import MatchBatchRequest, MatchBatchResponse, MatchJobResponse, MatchListResponse
from app.services.match_service import MatchService
from app.services.rate_limiter import RateLimiter

logger = get_logger("handler.matches")

router: APIRouter = APIRouter(prefix="/matches", tags=["matches"])

# 5 requests per 60 seconds for job submissions
submit_limiter = RateLimiter(times=5, seconds=60)
# 10 requests per 60 seconds for retries
retry_limiter = RateLimiter(times=10, seconds=60)


@router.post(
    "",
    response_model=MatchBatchResponse,
    status_code=201,
    summary="Submit a batch of job descriptions for scoring",
    dependencies=[Depends(submit_limiter)]
)
def submit_matches(
    request: MatchBatchRequest,
    db: Session = Depends(get_db),
) -> MatchBatchResponse:
    """Accept a batch of up to 10 job descriptions.

    Enqueue a background scoring job for each.
    Return immediately with a list of job IDs and status pending.
    """
    with log_flow(logger, "handler", "SubmitMatches", candidate_id=str(request.candidate_id)):
        service: MatchService = MatchService(db)
        return service.submit_batch(
            candidate_id=request.candidate_id,
            jobs=request.jobs,
        )


@router.get(
    "/{job_id}",
    response_model=MatchJobResponse,
    summary="Get a single match job result",
)
def get_match(
    job_id: UUID,
    db: Session = Depends(get_db),
) -> MatchJobResponse:
    """Return the current status and result for a single match job."""
    with log_flow(logger, "handler", "GetMatch", job_id=str(job_id)):
        service: MatchService = MatchService(db)
        return service.get_match(job_id)


@router.get(
    "",
    response_model=MatchListResponse,
    summary="List match results for a candidate",
)
def list_matches(
    candidate_id: UUID = Query(..., description="Candidate ID to filter by"),
    status: str | None = Query(None, description="Filter by status: pending, processing, completed, failed"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
) -> MatchListResponse:
    """List match results for the current candidate, filterable by status with pagination."""
    with log_flow(logger, "handler", "ListMatches", candidate_id=str(candidate_id), status=status, limit=limit, offset=offset):
        service: MatchService = MatchService(db)
        return service.list_matches(
            candidate_id=candidate_id,
            status=status,
            limit=limit,
            offset=offset,
        )


@router.post(
    "/{job_id}/retry",
    response_model=MatchJobResponse,
    summary="Manually retry a failed match job",
    dependencies=[Depends(retry_limiter)]
)
def retry_match(
    job_id: UUID,
    db: Session = Depends(get_db),
) -> MatchJobResponse:
    """Retrigger a job that failed or is dead, assuming retry limit not exceeded."""
    with log_flow(logger, "handler", "RetryMatch", job_id=str(job_id)):
        service: MatchService = MatchService(db)
        return service.retry_match(job_id)
