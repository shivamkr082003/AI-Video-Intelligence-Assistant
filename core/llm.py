import os
import time

from langchain_core.output_parsers import StrOutputParser
from langchain_mistralai import ChatMistralAI


DEFAULT_MODEL = "mistral-small-latest"
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_SECONDS = 2.0


def _parse_fallback_models() -> list[str]:
    raw = os.getenv("MISTRAL_FALLBACK_MODELS", "")
    return [model.strip() for model in raw.split(",") if model.strip()]


def configured_models() -> list[str]:
    primary = os.getenv("MISTRAL_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    models = [primary, *_parse_fallback_models()]

    unique_models = []
    seen = set()
    for model in models:
        if model not in seen:
            unique_models.append(model)
            seen.add(model)
    return unique_models


def create_llm(model: str, temperature: float) -> ChatMistralAI:
    return ChatMistralAI(
        model=model,
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=temperature,
    )


def _is_retryable_capacity_error(exc: Exception) -> bool:
    message = str(exc).lower()
    retry_markers = (
        "429",
        "service_tier_capacity_exceeded",
        "capacity exceeded",
        "rate limit",
        "too many requests",
    )
    return any(marker in message for marker in retry_markers)


def _friendly_capacity_error(last_error: Exception) -> RuntimeError:
    models = ", ".join(configured_models())
    return RuntimeError(
        "Mistral is temporarily unavailable for the configured model(s): "
        f"{models}. Update `MISTRAL_MODEL` or `MISTRAL_FALLBACK_MODELS` in your "
        "environment, or wait a moment and try again.\n\n"
        f"Last error: {last_error}"
    )


def invoke_with_fallback(prompt, payload: dict, temperature: float = 0.3) -> str:
    parser = StrOutputParser()
    models = configured_models()
    retries = int(os.getenv("MISTRAL_MAX_RETRIES", DEFAULT_RETRIES))
    base_delay = float(os.getenv("MISTRAL_RETRY_BACKOFF_SECONDS", DEFAULT_BACKOFF_SECONDS))
    last_error: Exception | None = None

    for model_index, model in enumerate(models):
        for attempt in range(1, retries + 1):
            try:
                llm = create_llm(model, temperature)
                chain = prompt | llm | parser
                return chain.invoke(payload)
            except Exception as exc:
                last_error = exc
                is_retryable = _is_retryable_capacity_error(exc)
                is_last_attempt = attempt == retries
                is_last_model = model_index == len(models) - 1

                if not is_retryable:
                    raise

                if is_last_attempt and is_last_model:
                    raise _friendly_capacity_error(exc) from exc

                if not is_last_attempt:
                    time.sleep(base_delay * attempt)
                    continue

                break

    if last_error is not None:
        raise _friendly_capacity_error(last_error) from last_error

    raise RuntimeError("No Mistral models were configured.")
