from fastapi import APIRouter

from app.api.v1.matches import router as matches_router
from app.api.v1.candidates import router as candidates_router

router: APIRouter = APIRouter(prefix="/api/v1")

router.include_router(matches_router)
router.include_router(candidates_router)
