"""Multi-provider API client for making LLM requests."""

import httpx
import time
import logging
from typing import List, Dict, Any, Optional
from .config import PROVIDERS

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _get_provider_config(model: str) -> tuple[str, str, dict]:
    """
    Split a model identifier into provider config and model name.

    Args:
        model: Model identifier like "openai/gpt-5.1"

    Returns:
        Tuple of (model_name, provider_key, provider_config)

    Raises:
        ValueError: If provider prefix not found in PROVIDERS
    """
    prefix, model_name = model.split("/", 1)
    config = PROVIDERS.get(prefix)
    if not config:
        raise ValueError(f"Unknown provider prefix: {prefix}")
    return model_name, prefix, config


async def _query_openai_compatible(
    model_name: str,
    messages: List[Dict[str, str]],
    config: dict,
    timeout: float,
) -> Optional[Dict[str, Any]]:
    """Query an OpenAI-compatible endpoint (OpenAI, Google, xAI)."""
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_name,
        "messages": messages,
    }

    # Enable reasoning/thinking for models that support it
    if "gpt-5" in model_name or "reasoner" in model_name or "gemini" in model_name:
        payload["reasoning_effort"] = "high"

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            config["base_url"],
            headers=headers,
            json=payload,
        )
        if response.status_code != 200:
            logger.error(f"[{model_name}] HTTP {response.status_code}: {response.text[:500]}")
        response.raise_for_status()

        data = response.json()
        message = data["choices"][0]["message"]
        content = message.get("content") or message.get("reasoning_content")

        return {
            "content": content,
            "reasoning_details": message.get("reasoning_details") or message.get("reasoning_content"),
        }


async def _query_anthropic(
    model_name: str,
    messages: List[Dict[str, str]],
    config: dict,
    timeout: float,
) -> Optional[Dict[str, Any]]:
    """Query the Anthropic Messages API."""
    headers = {
        "x-api-key": config["api_key"],
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

    # Separate system message from the rest
    system_text = None
    non_system = []
    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        else:
            non_system.append(msg)

    payload = {
        "model": model_name,
        "max_tokens": 16384,
        "messages": non_system,
        "thinking": {
            "type": "enabled",
            "budget_tokens": 10000,
        },
    }
    if system_text:
        payload["system"] = system_text

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            config["base_url"],
            headers=headers,
            json=payload,
        )
        if response.status_code != 200:
            logger.error(f"[{model_name}] HTTP {response.status_code}: {response.text[:500]}")
        response.raise_for_status()

        data = response.json()

        # Anthropic returns content blocks: [{"type": "thinking", ...}, {"type": "text", ...}]
        content = ""
        thinking = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")
            elif block.get("type") == "thinking":
                thinking += block.get("thinking", "")

        return {
            "content": content,
            "reasoning_details": thinking or None,
        }


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 500.0,
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via its native API.

    Args:
        model: Model identifier (e.g., "openai/gpt-5.1")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds

    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    start = time.time()
    try:
        model_name, _prefix, config = _get_provider_config(model)
        logger.info(f"[{model}] Starting request (timeout={timeout}s)")

        if config["format"] == "anthropic":
            result = await _query_anthropic(model_name, messages, config, timeout)
        else:
            result = await _query_openai_compatible(model_name, messages, config, timeout)

        elapsed = time.time() - start
        content_len = len(result.get("content", "")) if result else 0
        logger.info(f"[{model}] Success in {elapsed:.1f}s ({content_len} chars)")
        return result

    except Exception as e:
        elapsed = time.time() - start
        logger.error(f"[{model}] Failed after {elapsed:.1f}s: {type(e).__name__}: {e}")
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]],
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.

    Args:
        models: List of model identifiers
        messages: List of message dicts to send to each model

    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    import asyncio

    tasks = [query_model(model, messages) for model in models]
    responses = await asyncio.gather(*tasks)

    return {model: response for model, response in zip(models, responses)}
