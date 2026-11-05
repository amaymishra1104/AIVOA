"""One helper for structured Groq calls, with a short retry on schema failures."""

from __future__ import annotations

import logging

from typing import TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel

from app.config import get_settings
from app.errors import LLMFailed, LLMNotConfigured

log = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

_METHODS = ("json_schema", "function_calling", "json_mode")
_RESOLVED_MODEL: str | None = None


def get_effective_model(settings) -> str:
    global _RESOLVED_MODEL
    if _RESOLVED_MODEL:
        return _RESOLVED_MODEL
    target = settings.groq_model
    try:
        import groq

        client = groq.Groq(api_key=settings.groq_api_key)
        try:
            available = {m.id for m in client.models.list().data}
        except Exception:
            available = set()
        if not available or target in available:
            _RESOLVED_MODEL = target
            return _RESOLVED_MODEL
        for candidate in ("openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"):
            if candidate in available:
                log.info("Configured model '%s' unavailable, using active '%s'", target, candidate)
                _RESOLVED_MODEL = candidate
                return _RESOLVED_MODEL
    except Exception as exc:
        log.warning("Could not probe Groq models: %s", exc)
    _RESOLVED_MODEL = target
    return _RESOLVED_MODEL


def complete_structured(
    schema: type[T],
    system: str,
    human: str,
    *,
    node: str,
    temperature: float = 0.1,
) -> T:
    settings = get_settings()
    if not settings.llm_configured:
        raise LLMNotConfigured()

    effective_model = get_effective_model(settings)
    messages = [SystemMessage(content=system), HumanMessage(content=human)]
    last_error = "The model returned no usable object."
    for attempt in range(3):
        method = _METHODS[min(attempt, len(_METHODS) - 1)]
        prompt = list(messages)
        if method == "json_mode":
            prompt.append(HumanMessage(content="Return a single JSON object matching the requested schema."))
        try:
            model = ChatGroq(
                model_name=effective_model,
                groq_api_key=settings.groq_api_key,
                temperature=temperature,
                max_tokens=4096,
                max_retries=1,
                request_timeout=90,
            )
            runnable = model.with_structured_output(schema, method=method)
            raw = runnable.invoke(prompt)
            return _coerce(schema, raw)
        except LLMNotConfigured:
            raise
        except Exception as exc:
            last_error = _redact(exc, settings.groq_api_key)
            log.warning("structured output failed node=%s attempt=%s method=%s", node, attempt + 1, method)
            messages = [
                SystemMessage(content=system),
                HumanMessage(content=human),
                HumanMessage(
                    content=(
                        "The previous response failed validation "
                        f"({last_error[:700]}). "
                        "Return only data that matches the schema. Use empty strings instead of null. "
                        "Do not invent facts that are not in the source."
                    )
                ),
            ]
    raise LLMFailed(node, last_error[:500])


def _coerce(schema: type[T], raw: object) -> T:
    if isinstance(raw, schema):
        return raw
    if isinstance(raw, BaseModel):
        return schema.model_validate(raw.model_dump())
    if isinstance(raw, dict):
        return schema.model_validate(raw)
    raise TypeError(f"Expected {schema.__name__}, got {type(raw).__name__}")


def _redact(exc: Exception, secret: str) -> str:
    text = f"{type(exc).__name__}: {exc}"
    if secret:
        text = text.replace(secret, "[redacted]")
    return text
