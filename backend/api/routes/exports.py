"""Explicit PDF and Markdown downloads for saved reports."""

from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException

from fastapi.responses import Response
from starlette.concurrency import run_in_threadpool
from backend.memory.memory_manager import MemoryManager
from backend.schemas.models import ExportRequest
from backend.export.pdf_export import get_pdf_bytes
from backend.export.markdown_export import get_markdown_content
from backend.api.downloads import download_header

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/export/pdf")
async def export_pdf_endpoint(request: ExportRequest):
    """Export a research report as a PDF file."""
    manager = MemoryManager()
    session = manager.load_session(request.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        pdf_bytes = await run_in_threadpool(get_pdf_bytes, session)
        query = session.get("user_query", "research")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": download_header(query, "pdf")},
        )
    except Exception as e:
        logger.error(f"PDF export failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"PDF export failed: {str(e)}",
        )


@router.post("/export/markdown")
async def export_markdown_endpoint(request: ExportRequest):
    """Export a research report as a Markdown file."""
    manager = MemoryManager()
    session = manager.load_session(request.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        md_content = get_markdown_content(session)
        query = session.get("user_query", "research")

        return Response(
            content=md_content.encode("utf-8"),
            media_type="text/markdown",
            headers={"Content-Disposition": download_header(query, "md")},
        )
    except Exception as e:
        logger.error(f"Markdown export failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Markdown export failed: {str(e)}",
        )
