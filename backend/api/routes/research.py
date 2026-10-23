"""AI topic suggestions and selected-scope research requests."""

from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException

from datetime import datetime, timezone
from backend.config import settings
from backend.schemas.models import ResearchRequest, ResearchResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/recommendations")
async def recommend_topics(request: ResearchRequest):
    """Suggest an outline only; do not search, save, or generate a report."""
    try:
        settings.validate()
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    from backend.agents.planner import planner_node

    try:
        result = await planner_node(
            {
                "user_query": request.query,
                "model": request.model,
                "temperature": request.temperature,
            }
        )
        plan = result["research_plan"]
        topics = list(dict.fromkeys(t.strip() for t in plan.get("sub_topics", []) if t.strip()))[
            :12
        ]
        if not topics or any(len(topic) > 180 for topic in topics):
            raise ValueError("No valid topic suggestions returned")
        return {"query": request.query, "topics": topics, "objectives": plan.get("objectives", [])}
    except Exception as exc:
        logger.error("Topic recommendations failed: %s", exc)
        raise HTTPException(
            status_code=502, detail="AI recommendations could not be generated. Please retry."
        ) from exc


@router.post("/research", response_model=ResearchResponse)
async def run_research_endpoint(request: ResearchRequest):
    """
    Execute the full research workflow for a given topic.

    Runs the LangGraph pipeline:
    Planner → Researcher → Analyst → Summarizer → Reporter → Memory
    """
    logger.info(f"Research request received: '{request.query}'")

    try:
        settings.validate()
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        # Import here to avoid circular imports at module level
        from backend.graph.workflow import run_research

        result = await run_research(
            query=request.query,
            model=request.model,
            temperature=request.temperature,
            selected_topics=request.selected_topics,
            excluded_topics=[
                t for t in request.excluded_topics if t not in (request.selected_topics or [])
            ],
        )

        return ResearchResponse(
            session_id=result.get("session_id", "unknown"),
            query=result.get("user_query", request.query),
            research_plan=result.get("research_plan", {}),
            sources=result.get("sources", []),
            insights=result.get("insights", []),
            summary=result.get("summary", ""),
            final_report=result.get("final_report", ""),
            selected_topics=result.get("selected_topics", []),
            excluded_topics=result.get("excluded_topics", []),
            evidence_gaps=result.get("evidence_gaps", []),
            logs=result.get("logs", []),
            created_at=result.get("memory", {}).get(
                "saved_at", datetime.now(timezone.utc).isoformat()
            ),
        )

    except Exception as e:
        logger.error(f"Research pipeline failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Research pipeline failed: {str(e)}",
        )
