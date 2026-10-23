"""Regression coverage for failures found in the project audit."""

import io
from unittest.mock import AsyncMock, patch

import pytest
from pypdf import PdfReader

from backend.export.pdf_export import _parse_inline_spans, get_pdf_bytes


def test_inline_citations_and_unmatched_markers_are_preserved():
    text = "Evidence [Source 1], [2], and a lone * marker."
    assert "".join(span[1] for span in _parse_inline_spans(text)) == text


def test_consecutive_headings_export_without_width_error():
    content = "# Topic\n## Findings\n### Details\nText [Source 1]."
    data = get_pdf_bytes({"user_query": "Topic", "final_report": content})
    assert "[Source 1]" in "".join(p.extract_text() for p in PdfReader(io.BytesIO(data)).pages)


def test_long_code_wraps_and_paginates():
    code = "\n".join(f"LINE_{i:03d}: " + "x" * 180 for i in range(160))
    data = get_pdf_bytes({"user_query": "Code", "final_report": f"```\n{code}\n```\nEND_MARKER"})
    reader = PdfReader(io.BytesIO(data))
    text = "\n".join(page.extract_text() for page in reader.pages)
    assert "LINE_159" in text and "END_MARKER" in text
    assert len(reader.pages) >= 5


@pytest.mark.asyncio
async def test_analyst_preserves_evidence_snippets():
    from backend.agents.analyst import analyst_node

    source = {
        "title": "Evidence",
        "url": "https://example.com",
        "snippet": "Verified data",
        "source": "web",
    }
    with (
        patch("backend.agents.analyst.rerank_search_results", AsyncMock(return_value=[source])),
        patch(
            "backend.agents.analyst.invoke_llm_json",
            AsyncMock(return_value='{"insights": ["Verified data [Source 1]"]}'),
        ),
    ):
        result = await analyst_node({"user_query": "Topic", "search_results": [source]})
    assert result["sources"][0]["snippet"] == "Verified data"


@pytest.mark.asyncio
async def test_no_search_results_fails_instead_of_fabricating_report():
    from backend.agents.researcher import researcher_node

    with patch("backend.agents.researcher.search_all", AsyncMock(return_value=[])):
        with pytest.raises(RuntimeError, match="No usable"):
            await researcher_node({"user_query": "Topic"})


@pytest.mark.asyncio
async def test_unicode_download_filename():
    from backend.main import app
    from httpx import ASGITransport, AsyncClient

    session = {
        "user_query": "\u0939\u093f\u0902\u0926\u0940 \u0930\u093f\u0938\u0930\u094d\u091a",
        "final_report": "# Report\nEvidence [Source 1].",
    }
    with patch("backend.memory.memory_manager.MemoryManager.load_session", return_value=session):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for fmt in ("pdf", "markdown"):
                response = await client.post(f"/export/{fmt}", json={"session_id": "unicode"})
                assert response.status_code == 200
                assert "filename*=UTF-8''" in response.headers["content-disposition"]


@pytest.mark.asyncio
async def test_complete_workflow_history_and_exports(tmp_path, monkeypatch):
    from backend.config import settings
    from backend.main import app
    from httpx import ASGITransport, AsyncClient

    monkeypatch.setattr(settings, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "test-only-key")
    source = {
        "title": "Evidence",
        "url": "https://example.com",
        "snippet": "Verified evidence.",
        "source": "web",
    }
    planner = AsyncMock(
        return_value='{"objectives":["Test"],"sub_topics":["Test"],"search_queries":["Test"]}'
    )
    analyst = AsyncMock(return_value='{"insights":["Verified evidence [Source 1]"]}')
    reporter = AsyncMock(
        return_value="# Research\n## Findings\nVerified evidence [Source 1].\n\n| Metric | Value |\n|---|---|\n| Sources | 1 |"
    )
    with (
        patch("backend.agents.planner.invoke_llm_json", planner),
        patch("backend.agents.researcher.search_all", AsyncMock(return_value=[source])),
        patch("backend.agents.analyst.rerank_search_results", AsyncMock(return_value=[source])),
        patch("backend.agents.analyst.invoke_llm_json", analyst),
        patch("backend.agents.summarizer.invoke_llm", AsyncMock(return_value="Evidence summary.")),
        patch("backend.agents.reporter.invoke_llm", reporter),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/research", json={"query": "  Research test  ", "temperature": 0.6}
            )
            assert response.status_code == 200, response.text
            result = response.json()
            assert result["query"] == "Research test"
            assert result["sources"][0]["snippet"] == source["snippet"]
            assert len(result["logs"]) == 7
            assert reporter.call_args.kwargs["temperature"] == 0.6
            session_id = result["session_id"]
            history = (await client.get("/history")).json()
            assert history[0]["session_id"] == session_id
            saved = (await client.get(f"/report/{session_id}")).json()
            assert saved["final_report"] == result["final_report"]
            assert saved["logs"] == result["logs"]
            for fmt in ("pdf", "markdown"):
                response = await client.post(f"/export/{fmt}", json={"session_id": session_id})
                assert response.status_code == 200
                if fmt == "pdf":
                    text = "".join(
                        p.extract_text() for p in PdfReader(io.BytesIO(response.content)).pages
                    )
                    assert "[Source 1]" in text and "Verified evidence." in text
                else:
                    assert "[Source 1]" in response.text


@pytest.mark.asyncio
async def test_missing_key_is_503(monkeypatch):
    from backend.config import settings
    from backend.main import app
    from httpx import ASGITransport, AsyncClient

    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/research", json={"query": "Research topic"})
        assert response.status_code == 503
        assert "OPENROUTER_API_KEY" in response.json()["detail"]


@pytest.mark.asyncio
async def test_llm_error_does_not_become_report():
    from backend.agents.reporter import reporter_node

    with patch(
        "backend.agents.reporter.invoke_llm", AsyncMock(side_effect=RuntimeError("model_not_found"))
    ):
        with pytest.raises(RuntimeError, match="Reporter failed"):
            await reporter_node({"user_query": "Topic"})


@pytest.mark.asyncio
async def test_reranking_is_one_call_and_rejects_invalid_scores():
    from backend.services.reranker_service import rerank_documents

    docs = [{"title": "A"}, {"title": "B"}]
    mock = AsyncMock(return_value='{"scores":[0.2,0.9]}')
    with patch("backend.services.llm_service.invoke_llm_json", mock):
        result = await rerank_documents("topic", docs)
        assert result[0]["title"] == "B"
        assert mock.await_count == 1
    with patch(
        "backend.services.llm_service.invoke_llm_json", AsyncMock(return_value='{"scores":[-5,99]}')
    ):
        result = await rerank_documents("topic", docs)
        assert [doc["title"] for doc in result] == ["A", "B"]
        assert all(doc["relevance_score"] == 0.5 for doc in result)


def test_wikipedia_uses_https_timeout_and_preserves_extract():
    from backend.tools.search_tools import _search_wikipedia_sync
    from unittest.mock import MagicMock

    response = MagicMock()
    response.json.return_value = {
        "query": {
            "pages": {
                "1": {
                    "title": "Topic",
                    "fullurl": "https://en.wikipedia.org/wiki/Topic",
                    "extract": "Verified extract",
                    "index": 1,
                }
            }
        }
    }
    with patch("backend.tools.search_tools.httpx.Client") as mock_client:
        client = mock_client.return_value.__enter__.return_value
        client.get.return_value = response
        result = _search_wikipedia_sync("topic")
        assert result[0]["snippet"] == "Verified extract"
        assert client.get.call_args.args[0].startswith("https://")
        assert mock_client.call_args.kwargs["timeout"] == 15


def test_long_title_and_quote_export():
    data = get_pdf_bytes(
        {
            "user_query": "A detailed research topic " * 20,
            "final_report": "> " + "Long quotation with evidence. " * 700 + "\n\nEND_OF_REPORT",
        }
    )
    reader = PdfReader(io.BytesIO(data))
    assert "END_OF_REPORT" in "".join(p.extract_text() for p in reader.pages)


def test_mixed_hindi_english_citations_survive_font_fallback():
    text = "\u092f\u0939 \u0939\u093f\u0902\u0926\u0940 \u092a\u0930\u0940\u0915\u094d\u0937\u0923 \u0939\u0948\u0964 Evidence [Source 1] remains intact."
    data = get_pdf_bytes({"user_query": "Hindi text", "final_report": text})
    result = "".join(p.extract_text() for p in PdfReader(io.BytesIO(data)).pages)
    assert "Evidence [Source 1] remains intact." in result


def test_table_cell_longer_than_a_page_keeps_all_content():
    table = (
        "| Field | Evidence |\n|---|---|\n| Long entry | "
        + "Evidence detail. " * 1000
        + "LAST_CELL_MARKER |"
    )
    data = get_pdf_bytes({"user_query": "Long table", "final_report": table})
    result = "".join(p.extract_text() for p in PdfReader(io.BytesIO(data)).pages)
    assert "LAST_CELL_MARKER" in result


@pytest.mark.asyncio
async def test_invalid_analysis_json_is_not_reported_as_insights():
    from backend.agents.analyst import analyst_node

    source = {
        "title": "Evidence",
        "url": "https://example.com",
        "snippet": "Evidence",
        "source": "web",
    }
    with (
        patch("backend.agents.analyst.rerank_search_results", AsyncMock(return_value=[source])),
        patch(
            "backend.agents.analyst.invoke_llm_json",
            AsyncMock(return_value="Unstructured model error response"),
        ),
    ):
        with pytest.raises(RuntimeError, match="invalid JSON"):
            await analyst_node({"user_query": "Topic", "search_results": [source]})


def test_english_pdf_preserves_original_typefaces():
    data = get_pdf_bytes(
        {"user_query": "Original style", "final_report": "# Report\nBody text.\n```\nprint(1)\n```"}
    )
    reader = PdfReader(io.BytesIO(data))
    fonts = {
        str(font.get_object().get("/BaseFont"))
        for page in reader.pages
        for font in page["/Resources"]["/Font"].values()
    }
    assert "/Helvetica" in fonts
    assert "/Courier" in fonts


def test_groq_free_models_accept_slash_ids(monkeypatch):
    from backend.config import settings
    from backend.services.llm_service import get_llm

    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(settings, "OPENROUTER_BASE_URL", "https://api.groq.com/openai/v1")
    model = get_llm("openai/gpt-oss-120b")
    assert model.model_name == "openai/gpt-oss-120b"
    assert model.reasoning_effort == "low"


def test_free_api_retry_respects_cooldown():
    from backend.services.llm_service import _retry_wait
    from types import SimpleNamespace

    error = SimpleNamespace(response=SimpleNamespace(headers={"retry-after": "22"}))
    state = SimpleNamespace(attempt_number=1, outcome=SimpleNamespace(exception=lambda: error))
    assert _retry_wait(state) == 22.5


def test_free_request_reserves_completion_space(monkeypatch):
    import sys
    from types import SimpleNamespace
    from backend.config import settings
    from backend.services.llm_service import _fit_free_token_budget

    monkeypatch.setattr(settings, "OPENROUTER_BASE_URL", "https://api.groq.com/openai/v1")
    monkeypatch.setattr(settings, "GROQ_TOKEN_BUDGET", 8000)
    monkeypatch.setitem(
        sys.modules,
        "tiktoken",
        SimpleNamespace(get_encoding=lambda name: SimpleNamespace(encode=lambda text: [1] * 5000)),
    )
    assert _fit_free_token_budget("Context", None, 4096) == 2644


def test_model_citation_brackets_and_bold_quotes_survive_pdf():
    data = get_pdf_bytes(
        {
            "user_query": "Citations",
            "final_report": "> **Evidence** supported by source\u30104\u3011.\n\nBody evidence\u30101\u3011.",
        }
    )
    text = "".join(p.extract_text() for p in PdfReader(io.BytesIO(data)).pages)
    assert "[4]" in text and "[1]" in text
    assert "**Evidence**" not in text
