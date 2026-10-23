"""Service liveness and non-secret configuration readiness."""

from datetime import datetime, timezone
from fastapi import APIRouter
from backend.config import settings
from backend.schemas.models import HealthResponse

router = APIRouter()


@router.get("/")
async def root_endpoint():
    """Welcome root endpoint."""
    return {
        "message": "Welcome to the Agentic AI Research Assistant API",
        "health": "/health",
        "docs": "/docs",
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version="1.0.0",
        research_ready=bool(settings.OPENROUTER_API_KEY),
        default_model=settings.DEFAULT_MODEL,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
