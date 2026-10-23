"""
OpenRouter LLM Service.

Wraps langchain-openai's ChatOpenAI to point at the OpenRouter API.
Provides retry logic, model selection, and both sync/async invocation.
"""

from __future__ import annotations

import logging
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from typing import Optional

from langchain_openai import ChatOpenAI
from openai import APIConnectionError, APITimeoutError, RateLimitError, InternalServerError
from tenacity import (
    retry,
    stop_after_attempt,
    retry_if_exception_type,
    before_sleep_log,
)

from backend.config import settings

logger = logging.getLogger(__name__)


def _retry_wait(retry_state) -> float:
    """Respect the free provider's cooldown instead of retrying into the same limit."""
    delay = min(2**retry_state.attempt_number, 10)
    exception = retry_state.outcome.exception()
    response = getattr(exception, "response", None)
    retry_after = response.headers.get("retry-after") if response is not None else None
    if retry_after:
        try:
            delay = max(delay, float(retry_after) + 0.5)
        except ValueError:
            try:
                delay = max(
                    delay,
                    (
                        parsedate_to_datetime(retry_after) - datetime.now(timezone.utc)
                    ).total_seconds()
                    + 0.5,
                )
            except (TypeError, ValueError):
                pass
    return min(max(delay, 0), 90)


def _fit_free_token_budget(prompt: str, system_prompt: str | None, requested: int) -> int:
    if "groq.com" not in settings.OPENROUTER_BASE_URL.lower():
        return requested
    import tiktoken

    encoding = tiktoken.get_encoding("o200k_base")
    estimated_input = len(encoding.encode((system_prompt or "") + "\n" + prompt)) + 100
    available = settings.GROQ_TOKEN_BUDGET - estimated_input - 256
    if available < 512:
        raise ValueError(
            "Research context exceeds the configured free API token budget. Try a narrower topic."
        )
    return min(requested, available)


def get_llm(
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 4096,
    streaming: bool = False,
) -> ChatOpenAI:
    """
    Create a ChatOpenAI instance configured for OpenRouter.

    Parameters
    ----------
    model : str, optional
        OpenRouter model ID. Defaults to settings.DEFAULT_MODEL.
    temperature : float
        Sampling temperature (0.0 - 1.0).
    max_tokens : int
        Maximum tokens in the response.
    streaming : bool
        Whether to enable streaming responses.

    Returns
    -------
    ChatOpenAI
        Configured LLM client.
    """
    settings.validate()

    target_model = model or settings.DEFAULT_MODEL

    # Old UI versions sent Groq-only aliases even when OpenRouter was configured.
    if "openrouter.ai" in settings.OPENROUTER_BASE_URL.lower():
        aliases = {
            "llama-3.3-70b-versatile": "meta-llama/llama-3.3-70b-instruct",
            "llama-3.1-8b-instant": "meta-llama/llama-3.1-8b-instruct",
        }
        if target_model == "mixtral-8x7b-32768":
            raise ValueError(
                "This legacy model is no longer a supported preset. Choose the server default or a provider model ID."
            )
        target_model = aliases.get(target_model, target_model)
    elif "groq.com" in settings.OPENROUTER_BASE_URL.lower():
        legacy_models = {"llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"}
        if target_model in legacy_models:
            logger.warning(
                "Legacy model %s replaced with configured free model %s",
                target_model,
                settings.DEFAULT_MODEL,
            )
            target_model = settings.DEFAULT_MODEL

    model_options = {}
    if "groq.com" in settings.OPENROUTER_BASE_URL.lower() and target_model.startswith(
        "openai/gpt-oss-"
    ):
        model_options["reasoning_effort"] = "low"

    return ChatOpenAI(
        model=target_model,
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        temperature=temperature,
        max_tokens=max_tokens,
        streaming=streaming,
        timeout=60,
        max_retries=0,
        **model_options,
        default_headers={
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": settings.APP_NAME,
        },
    )


@retry(
    stop=stop_after_attempt(3),
    wait=_retry_wait,
    retry=retry_if_exception_type(
        (APIConnectionError, APITimeoutError, RateLimitError, InternalServerError)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
async def invoke_llm(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 4096,
    system_prompt: Optional[str] = None,
) -> str:
    """
    Invoke the LLM with retry logic.

    Parameters
    ----------
    prompt : str
        The user/human prompt to send.
    model : str, optional
        Model override.
    temperature : float
        Sampling temperature.
    max_tokens : int
        Max response tokens.
    system_prompt : str, optional
        System message to prepend.

    Returns
    -------
    str
        The LLM's text response.
    """
    from langchain_core.messages import HumanMessage, SystemMessage

    max_tokens = _fit_free_token_budget(prompt, system_prompt, max_tokens)
    llm = get_llm(model=model, temperature=temperature, max_tokens=max_tokens)

    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    messages.append(HumanMessage(content=prompt))

    target_model = model or settings.DEFAULT_MODEL
    logger.info(f"Invoking LLM [{target_model}] ...")

    try:
        response = await llm.ainvoke(messages)
        logger.info("LLM response received.")
        return response.content
    except Exception as e:
        logger.error(f"LLM call failed [{target_model}]: {type(e).__name__}: {e}")
        raise


async def invoke_llm_json(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 4096,
    system_prompt: Optional[str] = None,
) -> str:
    """
    Invoke the LLM expecting a JSON response.

    Adds explicit instruction for JSON output format.
    Returns raw string (caller is responsible for parsing).
    """
    json_instruction = (
        "\n\nIMPORTANT: Respond ONLY with valid JSON. "
        "No markdown code fences, no explanation text outside the JSON."
    )
    full_prompt = prompt + json_instruction

    return await invoke_llm(
        prompt=full_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
    )
