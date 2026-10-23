"""
Search tools for gathering information from DuckDuckGo and Wikipedia.

Provides standardized search result format across all sources
with error handling and graceful fallbacks.
"""

from __future__ import annotations

import logging

import httpx
from ddgs import DDGS

logger = logging.getLogger(__name__)


def _search_duckduckgo_sync(
    query: str,
    max_results: int = 10,
) -> list[dict]:
    try:
        results = []
        search_results = DDGS(timeout=15).text(
            query,
            max_results=max_results,
            safesearch="moderate",
            backend="duckduckgo,brave,google",
        )
        for r in search_results:
            results.append(
                {
                    "title": r.get("title", "Untitled"),
                    "url": r.get("href", r.get("link", "")),
                    "snippet": r.get("body", r.get("snippet", "")),
                    "source": "web",
                }
            )

        logger.info(f"DuckDuckGo returned {len(results)} results for '{query}'")
        return results

    except Exception as e:
        logger.error(f"DuckDuckGo search failed for '{query}': {e}")
        return []


async def search_duckduckgo(
    query: str,
    max_results: int = 10,
) -> list[dict]:
    """
    Search DuckDuckGo for the given query (run in a worker thread).
    """
    import asyncio

    return await asyncio.to_thread(_search_duckduckgo_sync, query, max_results)


def _search_wikipedia_sync(
    query: str,
    max_results: int = 5,
    sentences: int = 10,
) -> list[dict]:
    if max_results <= 0:
        return []
    try:
        # One bounded HTTPS request replaces the legacy library's unbounded HTTP calls.
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            response = client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "format": "json",
                    "generator": "search",
                    "gsrsearch": query,
                    "gsrlimit": min(max_results, 10),
                    "prop": "extracts|info",
                    "exintro": 1,
                    "explaintext": 1,
                    "exsentences": min(max(sentences, 1), 10),
                    "exlimit": "max",
                    "inprop": "url",
                },
                headers={"User-Agent": "AIResearchAssistant/1.0 (research source lookup)"},
            )
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise ValueError(f"Wikipedia API error: {data['error'].get('code', 'unknown')}")
        pages = sorted(
            data.get("query", {}).get("pages", {}).values(), key=lambda page: page.get("index", 0)
        )
        return [
            {
                "title": page["title"],
                "url": page["fullurl"],
                "snippet": page.get("extract", ""),
                "source": "wikipedia",
            }
            for page in pages
            if page.get("fullurl") and page.get("extract")
        ]
    except Exception as exc:
        logger.warning("Wikipedia search unavailable for %r: %s", query, exc)
        return []


async def search_wikipedia(
    query: str,
    max_results: int = 5,
    sentences: int = 10,
) -> list[dict]:
    """
    Search Wikipedia for the given query (run in a worker thread).
    """
    import asyncio

    return await asyncio.to_thread(_search_wikipedia_sync, query, max_results, sentences)


async def search_all(
    query: str,
    ddg_max: int = 10,
    wiki_max: int = 5,
) -> list[dict]:
    """
    Execute searches across all sources and combine results.

    Parameters
    ----------
    query : str
        Search query.
    ddg_max : int
        Max DuckDuckGo results.
    wiki_max : int
        Max Wikipedia results.

    Returns
    -------
    list[dict]
        Combined and deduplicated results from all sources.
    """
    import asyncio

    # Run both searches concurrently
    ddg_task = asyncio.create_task(search_duckduckgo(query, ddg_max))
    wiki_task = asyncio.create_task(search_wikipedia(query, wiki_max))

    ddg_results, wiki_results = await asyncio.gather(ddg_task, wiki_task, return_exceptions=True)

    combined = []

    if isinstance(ddg_results, list):
        combined.extend(ddg_results)
    else:
        logger.error(f"DuckDuckGo search raised: {ddg_results}")

    if isinstance(wiki_results, list):
        combined.extend(wiki_results)
    else:
        logger.error(f"Wikipedia search raised: {wiki_results}")

    # Deduplicate by URL
    seen_urls: set[str] = set()
    deduped: list[dict] = []
    for result in combined:
        url = result.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            deduped.append(result)
        elif not url:
            deduped.append(result)

    logger.info(
        f"Combined search: {len(deduped)} unique results ({len(combined)} total before dedup)"
    )
    return deduped
