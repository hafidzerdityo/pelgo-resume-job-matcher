from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class JobDescriptionInput(BaseModel):
    """A single job description input — either plain text or a URL."""

    text: str | None = Field(None, description="Plain text job description")
    url: str | None = Field(None, description="URL to a job posting")

    @field_validator("text", "url", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            return v.strip()
        return v

    def model_post_init(self, __context: object) -> None:
        if not self.text and not self.url:
            raise ValueError("Either 'text' or 'url' must be provided")


class MatchBatchRequest(BaseModel):
    """Request body for submitting a batch of job descriptions."""

    candidate_id: UUID
    jobs: list[JobDescriptionInput] = Field(
        ..., min_length=1, max_length=10, description="1-10 job descriptions"
    )


class MatchJobResponse(BaseModel):
    """Response for a single match job."""

    id: UUID
    candidate_id: UUID
    job_description: str
    source_url: str | None = None
    status: str

    # Scoring results
    overall_score: float | None = None
    skill_score: float | None = None
    experience_score: float | None = None
    location_score: float | None = None
    matched_skills: list[str] | None = None
    missing_skills: list[str] | None = None
    recommendation: str | None = None

    # Error info
    error_message: str | None = None
    retry_count: int = 0

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MatchBatchResponse(BaseModel):
    """Response after submitting a batch — returns created job IDs with pending status."""

    jobs: list[MatchJobResponse]
    total: int


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""

    total: int
    limit: int
    offset: int
    has_more: bool


class MatchListResponse(BaseModel):
    """Paginated list of match jobs."""

    data: list[MatchJobResponse]
    pagination: PaginationMeta
