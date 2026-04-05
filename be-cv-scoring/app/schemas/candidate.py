from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CandidateProfileResponse(BaseModel):
    """Response schema for candidate profile."""

    id: UUID
    name: str
    email: str
    skills: list[str]
    experience_years: int
    location: str
    seniority: str
    resume_text: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
