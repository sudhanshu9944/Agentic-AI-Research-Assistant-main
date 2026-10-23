"""
Pydantic models for FastAPI request / response validation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict


# ──────────────────────────────────────────────
# Request Models
# ──────────────────────────────────────────────

TopicText = Annotated[str, Field(min_length=2, max_length=180)]


class ResearchRequest(BaseModel):
    """Body for POST /research."""

    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The research topic to investigate.",
        examples=["Research Agentic AI"],
    )
    model: Optional[str] = Field(
        default=None,
        max_length=160,
        description="OpenRouter model ID override (defaults to config).",
    )
    temperature: float = Field(default=0.3, ge=0, le=1)
    selected_topics: Optional[list[TopicText]] = Field(default=None, min_length=1, max_length=12)
    excluded_topics: list[TopicText] = Field(default_factory=list, max_length=12)


class ExportRequest(BaseModel):
    """Body for POST /export/pdf and POST /export/markdown."""

    session_id: str = Field(
        ..., pattern=r"^[a-zA-Z0-9_-]{1,128}$", description="Session ID of the research to export."
    )


# ──────────────────────────────────────────────
# Response Models
# ──────────────────────────────────────────────


class SourceItem(BaseModel):
    """A single research source."""

    title: str
    url: str
    snippet: str
    source: str  # "duckduckgo" | "wikipedia"


class ResearchPlan(BaseModel):
    """Structured research plan."""

    objectives: list[str] = Field(default_factory=list)
    sub_topics: list[str] = Field(default_factory=list)
    search_queries: list[str] = Field(default_factory=list)


class ResearchResponse(BaseModel):
    """Full response from POST /research."""

    session_id: str
    query: str
    research_plan: dict
    sources: list[dict]
    insights: list[str]
    summary: str
    final_report: str
    logs: list[str]
    created_at: str
    selected_topics: list[str] = Field(default_factory=list)
    excluded_topics: list[str] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)


class HistoryItem(BaseModel):
    """Summary of a past research session."""

    session_id: str
    query: str
    created_at: str
    summary_preview: str = Field(
        default="",
        description="First 200 characters of the summary.",
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    app_name: str = ""
    version: str = "1.0.0"
    research_ready: bool = False
    default_model: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
