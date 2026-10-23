"""
Planner Agent Node.

Understands the user's research intent and creates a structured
research plan with objectives, sub-topics, and search queries.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from backend.services.llm_service import invoke_llm_json

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """You are an expert research planner who creates highly effective research strategies.
Your plans consistently lead to comprehensive, accurate research outcomes.

Given a research topic, produce a JSON object with exactly these keys:
{
    "objectives": ["list of 3-5 clear, specific, measurable research objectives"],
    "sub_topics": ["list of 4-6 specific sub-topics covering different angles"],
    "search_queries": ["list of 8-12 optimized search queries"]
}

GUIDELINES FOR OBJECTIVES:
- Each objective should answer a specific question (what, why, how, who, when)
- Include at least one objective about current state/facts
- Include at least one objective about challenges or limitations
- Include at least one objective about future direction or trends

GUIDELINES FOR SUB-TOPICS:
- Cover fundamentals/definitions, applications, key players, challenges, and trends
- Each sub-topic should be distinct — no overlapping coverage
- Include both technical and practical/business perspectives

GUIDELINES FOR SEARCH QUERIES:
- Make queries specific and keyword-rich (NOT vague questions)
- Include a mix of:
  * Definitional queries: "what is [topic] definition explained"
  * Current state: "[topic] current state statistics for the current year"
  * Key players: "[topic] leading companies organizations"
  * Applications: "[topic] real-world applications use cases"
  * Challenges: "[topic] challenges problems limitations"
  * Trends: "[topic] future trends predictions outlook"
  * Comparisons: "[topic] vs [alternative] comparison"
  * Expert views: "[topic] expert analysis review"
- Avoid overly broad single-word queries
- Each query should be 3-8 words for optimal search results
"""


async def planner_node(state: dict) -> dict:
    """
    Planner node for the LangGraph workflow.

    Takes the user_query from state, invokes the LLM to create
    a structured research plan.

    Parameters
    ----------
    state : dict
        Current workflow state with 'user_query'.

    Returns
    -------
    dict
        Partial state update with 'research_plan' and 'logs'.
    """
    user_query = state.get("user_query", "")
    model = state.get("model")
    timestamp = datetime.now(timezone.utc).isoformat()

    selected = list(dict.fromkeys(state.get("selected_topics", [])))
    if selected:
        return {
            "research_plan": {
                "objectives": [f"Investigate {topic}" for topic in selected],
                "sub_topics": selected,
                "search_queries": [f"{user_query} {topic}" for topic in selected],
            },
            "logs": [
                f"[{timestamp}] Planner: Using {len(selected)} user-approved topics; unchecked topics excluded from search scope."
            ],
        }

    logger.info(f"[Planner] Starting planning for: '{user_query}'")

    prompt = f"""Create a detailed research plan for the following topic:

TOPIC: {user_query}
CURRENT DATE: {timestamp[:10]}

Produce a structured JSON research plan."""

    try:
        response = await invoke_llm_json(
            prompt=prompt,
            model=model,
            system_prompt=PLANNER_SYSTEM_PROMPT,
            temperature=state.get("temperature", 0.2),
            max_tokens=1024,
        )

        # Parse the JSON response
        # Clean up potential markdown code fences
        cleaned = response.strip()
        if cleaned.startswith("```"):
            # Remove code fence markers
            lines = cleaned.split("\n")
            cleaned = "\n".join(line for line in lines if not line.strip().startswith("```"))

        research_plan = json.loads(cleaned)

        if not isinstance(research_plan, dict):
            raise ValueError("Research plan must be a JSON object")
        # Validate required keys
        for key in ("objectives", "sub_topics", "search_queries"):
            value = research_plan.get(key, [])
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                raise ValueError(f"{key} must be a list of strings")
            research_plan[key] = [item.strip() for item in value if item.strip()][:12]

        logger.info(
            f"[Planner] Plan created: "
            f"{len(research_plan.get('objectives', []))} objectives, "
            f"{len(research_plan.get('sub_topics', []))} sub-topics, "
            f"{len(research_plan.get('search_queries', []))} queries"
        )

        return {
            "research_plan": research_plan,
            "logs": [
                f"[{timestamp}] 📋 Planner: Created research plan with "
                f"{len(research_plan.get('objectives', []))} objectives, "
                f"{len(research_plan.get('sub_topics', []))} sub-topics, "
                f"{len(research_plan.get('search_queries', []))} search queries"
            ],
        }

    except json.JSONDecodeError as e:
        raise RuntimeError(
            "Planner returned invalid JSON. Please retry the topic recommendations."
        ) from e

    except Exception as e:
        raise RuntimeError(
            "Planner failed. Check the configured API key, model, and provider availability."
        ) from e
