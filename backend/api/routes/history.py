"""Read persisted research sessions and their scope decisions."""

from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, Path
from typing import Annotated

from backend.memory.memory_manager import MemoryManager
from backend.schemas.models import HistoryItem, ResearchResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/history", response_model=list[HistoryItem])
async def get_history():
    """List all past research sessions."""
    try:
        manager = MemoryManager()
        sessions = manager.list_sessions()
        return [HistoryItem(**s) for s in sessions]
    except Exception as e:
        logger.error("History lookup failed (%s)", type(e).__name__)
        raise HTTPException(status_code=500, detail="Research history could not be loaded.") from e


@router.get("/report/{session_id}")
async def get_report(session_id: Annotated[str, Path(pattern=r"^[a-zA-Z0-9_-]{1,128}$")]):
    """Retrieve a specific research report by session ID."""
    manager = MemoryManager()
    session = manager.load_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return ResearchResponse(
        session_id=session.get("session_id", session_id),
        query=session.get("user_query", ""),
        research_plan=session.get("research_plan", {}),
        sources=session.get("sources", []),
        insights=session.get("insights", []),
        summary=session.get("summary", ""),
        final_report=session.get("final_report", ""),
        selected_topics=session.get("selected_topics", []),
        excluded_topics=session.get("excluded_topics", []),
        evidence_gaps=session.get("evidence_gaps", []),
        logs=session.get("logs", []),
        created_at=session.get("created_at", ""),
    )
