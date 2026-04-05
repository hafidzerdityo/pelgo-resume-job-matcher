from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.v1.router import router as v1_router
from app.config import settings
from app.logger import setup_logging


def create_app() -> FastAPI:
    """Application factory for the FastAPI app."""
    setup_logging()
    
    from app.logger import get_logger
    sys_logger = get_logger("http.middleware")
    
    app: FastAPI = FastAPI(
        title="Pelgo CV Scoring API",
        description="Async match pipeline for scoring job descriptions against candidate profiles",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    import time
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class ReqResLogger(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            if "/health" in request.url.path:
                return await call_next(request)
            
            sys_logger.info(f"==================== START REQUEST: {request.method} {request.url.path} ====================")
            start_time = time.time()
            try:
                response = await call_next(request)
                duration = int((time.time() - start_time) * 1000)
                sys_logger.info(f"<<< RESPONSE DATA", status_code=response.status_code)
                sys_logger.info(f"==================== END REQUEST: {request.method} {request.url.path} ({duration}ms) ====================")
                return response
            except Exception as exc:
                duration = int((time.time() - start_time) * 1000)
                sys_logger.error(f"<<< RESPONSE (ERROR)", error=str(exc))
                sys_logger.info(f"==================== END REQUEST: {request.method} {request.url.path} ({duration}ms) ====================")
                raise exc

    app.add_middleware(ReqResLogger)

    # Global validation error handler — returns structured error shapes
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        errors: list[dict[str, object]] = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Request validation failed",
                "details": errors,
            },
        )

    # Health check
    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {"status": "ok", "environment": settings.APP_ENV}

    # Register v1 routes
    app.include_router(v1_router)

    return app


app: FastAPI = create_app()
