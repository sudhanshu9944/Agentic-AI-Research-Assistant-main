"""Security boundaries for local browsing, report content and error disclosure."""

import io
import logging
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from pypdf import PdfReader

from backend.config import settings
from backend.main import app
from backend.security import RedactingFormatter, safe_external_url


@pytest.mark.asyncio
async def test_unapproved_browser_cannot_read_history_or_start_ai():
    with patch("backend.agents.planner.planner_node", AsyncMock()) as planner:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for method, path in [("GET", "/history"), ("POST", "/recommendations")]:
                response = await client.request(
                    method,
                    path,
                    headers={"Origin": "https://unrelated.example"},
                    json={"query": "Solar energy"},
                )
                assert response.status_code == 403
            planner.assert_not_awaited()
            allowed = await client.get("/health", headers={"Origin": settings.ALLOWED_ORIGINS[0]})
            assert allowed.status_code == 200
            assert allowed.headers["access-control-allow-origin"] == settings.ALLOWED_ORIGINS[0]
            assert allowed.headers["cache-control"] == "no-store"
            assert allowed.headers["x-content-type-options"] == "nosniff"


@pytest.mark.asyncio
async def test_streamed_large_body_rejected_before_ai():
    async def body():
        yield b'{"query":"'
        yield b"x" * 32768
        yield b'"}'

    with patch("backend.agents.planner.planner_node", AsyncMock()) as planner:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/recommendations", content=body(), headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 413
        planner.assert_not_awaited()


@pytest.mark.asyncio
async def test_internal_error_details_never_returned(monkeypatch):
    from backend.graph import workflow

    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "test-only-key")
    secret_detail = "private-file-and-provider-secret"
    with patch.object(workflow, "run_research", AsyncMock(side_effect=RuntimeError(secret_detail))):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/research", json={"query": "Solar energy"})
            assert response.status_code == 500
            assert secret_detail not in response.text
    with patch(
        "backend.memory.memory_manager.MemoryManager.list_sessions",
        side_effect=OSError(secret_detail),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/history")
            assert response.status_code == 500
            assert secret_detail not in response.text


@pytest.mark.asyncio
async def test_export_rejects_path_aliases_before_storage():
    with patch("backend.memory.memory_manager.MemoryManager.load_session") as load:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for session_id in ["../private", "a/b", "x" * 129]:
                response = await client.post("/export/pdf", json={"session_id": session_id})
                assert response.status_code == 422
        load.assert_not_called()


def test_exported_pdf_links_only_allow_web_schemes():
    from backend.export.pdf_export import get_pdf_bytes

    assert safe_external_url("https://example.com/evidence")
    for url in [
        "javascript:alert",
        "file:///private.txt",
        "https://user:pass@example.com",
        "https://example.com\n.evil",
    ]:
        assert safe_external_url(url) is None
    pdf = PdfReader(
        io.BytesIO(
            get_pdf_bytes(
                {
                    "user_query": "Link safety",
                    "final_report": "[unsafe](javascript:alert) [safe](https://example.com)",
                    "sources": [{"title": "Unsafe", "url": "file:///private.txt"}],
                }
            )
        )
    )
    links = []
    for page in pdf.pages:
        for annotation in page.get("/Annots", []):
            action = annotation.get_object().get("/A", {})
            if "/URI" in action:
                links.append(str(action["/URI"]))
    assert "https://example.com" in links
    assert all(safe_external_url(link) for link in links)


def test_logs_redact_configured_and_provider_credentials(monkeypatch):
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "configured-test-secret")
    provider_key = "gsk_" + "x" * 24
    record = logging.LogRecord(
        "test",
        logging.ERROR,
        "",
        0,
        "Failure %s %s",
        (settings.OPENROUTER_API_KEY, provider_key),
        None,
    )
    formatted = RedactingFormatter("%(message)s").format(record)
    assert settings.OPENROUTER_API_KEY not in formatted
    assert provider_key not in formatted
    assert formatted.count("[REDACTED]") == 2
