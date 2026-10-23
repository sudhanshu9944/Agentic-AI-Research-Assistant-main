"""Choice-first research flow contracts."""

import io
from unittest.mock import AsyncMock, patch
import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.graph import workflow
from backend.config import settings
from backend.agents.planner import planner_node
from backend.agents.analyst import analyst_node
from pypdf import PdfReader


@pytest.mark.asyncio
async def test_recommendations_only_plan_and_do_not_research_or_save(monkeypatch):
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "test")
    generated = {
        "research_plan": {
            "sub_topics": ["Benefits", "Risks", "Benefits"],
            "objectives": ["Compare"],
        }
    }
    with (
        patch("backend.agents.planner.planner_node", AsyncMock(return_value=generated)),
        patch.object(workflow, "run_research", AsyncMock()) as research,
        patch("backend.memory.memory_manager.MemoryManager.save_session") as save,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            result = await client.post("/recommendations", json={"query": "Solar energy"})
        assert result.status_code == 200
        assert result.json()["topics"] == ["Benefits", "Risks"]
        research.assert_not_awaited()
        save.assert_not_called()


@pytest.mark.asyncio
async def test_selected_topics_bound_the_actual_search_plan():
    with patch("backend.agents.planner.invoke_llm_json", AsyncMock()) as model:
        result = await planner_node(
            {
                "user_query": "Solar energy",
                "selected_topics": ["Benefits", "India examples"],
                "excluded_topics": ["Risks"],
            }
        )
    assert result["research_plan"]["sub_topics"] == ["Benefits", "India examples"]
    assert result["research_plan"]["search_queries"] == [
        "Solar energy Benefits",
        "Solar energy India examples",
    ]
    assert not any("Risks" in query for query in result["research_plan"]["search_queries"])
    model.assert_not_awaited()


@pytest.mark.asyncio
async def test_empty_or_excessive_selection_is_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for topics in ([], ["a"], ["Topic"] * 13):
            response = await client.post(
                "/research", json={"query": "Solar energy", "selected_topics": topics}
            )
            assert response.status_code == 422


@pytest.mark.asyncio
async def test_recommendation_failure_is_retryable_error(monkeypatch):
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "test")
    with patch(
        "backend.agents.planner.planner_node",
        AsyncMock(side_effect=RuntimeError("model unavailable")),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/recommendations", json={"query": "Solar energy"})
    assert response.status_code == 502
    assert "retry" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_evidence_gaps_are_not_discarded():
    source = {
        "title": "Evidence",
        "url": "https://example.com",
        "snippet": "Useful evidence",
        "source": "web",
    }
    with (
        patch("backend.agents.analyst.rerank_search_results", AsyncMock(return_value=[source])),
        patch(
            "backend.agents.analyst.invoke_llm_json",
            AsyncMock(
                return_value='{"insights":["Evidence [Source 1]"],"evidence_gaps":["No regional figures"]}'
            ),
        ),
    ):
        result = await analyst_node(
            {
                "user_query": "Solar energy",
                "search_results": [source],
                "research_plan": {"sub_topics": ["India examples"]},
            }
        )
    assert result["evidence_gaps"] == ["No regional figures"]


@pytest.mark.asyncio
async def test_scope_and_gaps_survive_workflow_history_and_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "test")
    source = {
        "title": "Evidence",
        "url": "https://example.com",
        "snippet": "Useful evidence",
        "source": "web",
    }
    with (
        patch("backend.agents.planner.invoke_llm_json", AsyncMock()) as planner,
        patch("backend.agents.researcher.search_all", AsyncMock(return_value=[source])) as search,
        patch("backend.agents.analyst.rerank_search_results", AsyncMock(return_value=[source])),
        patch(
            "backend.agents.analyst.invoke_llm_json",
            AsyncMock(
                return_value='{"insights":["Evidence [Source 1]"],"evidence_gaps":["No regional figures"]}'
            ),
        ),
        patch("backend.agents.summarizer.invoke_llm", AsyncMock(return_value="Reviewable summary")),
        patch(
            "backend.agents.reporter.invoke_llm",
            AsyncMock(return_value="# Selected research\nUseful evidence [Source 1]."),
        ),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/research",
                json={
                    "query": "Solar energy",
                    "selected_topics": ["Benefits"],
                    "excluded_topics": ["Risks"],
                },
            )
            assert response.status_code == 200, response.text
            result = response.json()
            assert result["selected_topics"] == ["Benefits"] and result["excluded_topics"] == [
                "Risks"
            ]
            assert result["evidence_gaps"] == ["No regional figures"]
            assert search.call_args.kwargs["query"] == "Solar energy Benefits"
            planner.assert_not_awaited()
            saved = (await client.get("/report/" + result["session_id"])).json()
            assert (
                saved["evidence_gaps"] == result["evidence_gaps"]
                and saved["selected_topics"] == result["selected_topics"]
            )
            pdf = await client.post("/export/pdf", json={"session_id": result["session_id"]})
            assert pdf.status_code == 200
            assert "[Source 1]" in "".join(
                page.extract_text() for page in PdfReader(io.BytesIO(pdf.content)).pages
            )
