from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.candidate_repository import CandidateRepository
from app.schemas.candidate import CandidateProfileResponse

from app.logger import get_logger, log_flow

logger = get_logger("handler.candidates")
router: APIRouter = APIRouter(prefix="/candidates", tags=["candidates"])

@router.get(
    "",
    response_model=list[CandidateProfileResponse],
    summary="List all candidate profiles",
)
def list_candidates(
    db: Session = Depends(get_db),
) -> list[CandidateProfileResponse]:
    """List all candidate profiles. Useful for the frontend to pick a candidate."""
    with log_flow(logger, "handler", "ListCandidates"):
        repo: CandidateRepository = CandidateRepository(db)
        candidates = repo.list_all()
        return [CandidateProfileResponse.model_validate(c) for c in candidates]
