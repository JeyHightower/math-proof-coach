import logging
import os
import time
from typing import  Any
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError
from cache import get_cached_response, store_cache_response, enforce_request_pacing
from exceptions import RateLimitError, ServiceUnavailableError, UpstreamAPIError
from rules import system_prompt

load_dotenv()
logger = logging.getLogger(__name__)
client = genai.Client()
# for m in client.models.list():
#     if "generateContent" in m.supported_actions:
#         print(m.name)
sessions: dict[str, dict[str, Any]] = {}

FALLBACK_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest",
]


MODEL_COOLDOWNS: dict[str, float] = {}
COOLD0WN_DURATION_SECONDS = 300.0

def is_model_cooling_down(model_name:str) -> bool:
    """Checks whether a model is currently marked in cooldown."""
    expiration = MODEL_COOLDOWNS.get(model_name, 0.0)
    return time.time() < expiration


def mark_model_cooldown(model_name: str) -> None:
    """Triggers a temporary cooldown for a failed model."""
    MODEL_COOLDOWNS[model_name] = time.time() + COOLD0WN_DURATION_SECONDS
    logger.warning(
        f"Circuit Breaker: Model '{model_name}' placed on {COOLD0WN_DURATION_SECONDS}s cooldown."
    )


def get_ordered_candidate_models(session_id:str) -> list[str]:
    """
    Returns a prioritized list of models to try for the session:
    1. The session's last known working model (if available).
    2. Any healthily operating fallback models (skipping those in cooldown).
    """
    base_order = list(FALLBACK_MODELS)
    current_working_model = sessions.get(session_id, {}).get("model_name")

    if current_working_model and current_working_model in base_order:
        base_order.remove(current_working_model)
        base_order.insert(0, current_working_model)

    healthy_candidates = [m for m in base_order if not is_model_cooling_down(m)]

    return healthy_candidates if healthy_candidates else base_order




def get_or_create_session(session_id: str, model_name: str):
    """
    Retrieves an existing chat session or creates/re-instantiates one
    with the requested model, preserving conversation history if switching models
    """

    config = types.GenerateContentConfig(
        system_instruction=system_prompt, temperature=0.3
    )

    if session_id not in sessions:
        logger.info(f"Creating new session '{session_id}' with model '{model_name}'")
        chat_session = client.chats.create(
            model=model_name,
            config=config,
        )
        sessions[session_id] = {
            "chat": chat_session,
            "model_name": model_name,
        }

        return chat_session

    session_data = sessions[session_id]

    if session_data["model_name"] == model_name:
        return session_data["chat"]

    logger.info(
        f"Switching session '{session_id}' model from '{session_data['model_name']}'"
        f"to fallback model '{model_name}'. Transferring History..."
    )

    old_chat = session_data["chat"]
    history = old_chat.get_history()

    new_chat = client.chats.create(
        model=model_name,
        config=config,
        history=history,
    )

    sessions[session_id] = {
        "chat": new_chat,
        "model_name": model_name,
    }
    return new_chat


def process_student_message(
    session_id: str,
    student_message: str,
    max_retries_per_model: int = 3,
    base_delay: float = 2.0,
) -> str:
    """
    Sends the student's message to their active chat session
     and returns the agent's Socratic response with caching,
     request pacing, automatic retries, and model fallbacks.
    """
    cached_response = get_cached_response(session_id, student_message)
    if cached_response:
        logger.info(
            f"Cache hit for session '{session_id}'.  Returning cached response."
        )
        return cached_response

    enforce_request_pacing()

    last_error = None
    candidate_models = get_ordered_candidate_models(session_id)

    for model_name in candidate_models:
        delay = base_delay

        try:
            chat_session = get_or_create_session(session_id, model_name=model_name)
        except (APIError, ClientError) as e:
            last_error = e
            logger.warning(
                f"Failed to initialize session for model '{model_name}': {e}"
            )
            mark_model_cooldown(model_name)
            continue

        for attempt in range(1, max_retries_per_model + 1):
            try:
                logger.info(
                    f"Sending message to session '{session_id}' using '{model_name}' "
                    f"(Attempt {attempt}/{max_retries_per_model})"
                )
                response = chat_session.send_message(student_message)
                store_cache_response(session_id, student_message, response.text)
                return response.text

            except APIError as e:
                last_error = e
                status_code = getattr(e, "code", None) or getattr(
                    e, "status_code", None
                )

                if status_code in (429, 503):
                    logger.warning(
                        f"Transient API error {status_code} on model '{model_name}'. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    delay *= 2
                elif status_code == 404:
                    logger.warning(
                        f"Model '{model_name}' returned 404 Not Found. Skipping to next fallback model."
                    )
                    break
                else:
                    # Non-transient API error (e.g., 400 Bad Request, safety filter)
                    raise UpstreamAPIError(
                        f"API error ({status_code}): {e.message}"
                    ) from e

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Unexpected network or runtime error on model '{model_name}': {e}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)
                delay *= 2

        mark_model_cooldown(model_name)

    # Evaluate final error status
    status_code = (
        getattr(last_error, "code", None) or getattr(last_error, "status_code", None)
        if last_error
        else None
    )

    if status_code == 429:
        raise RateLimitError(
            "Rate limit reached across all available fallback models."
        ) from last_error
    elif status_code == 503:
        raise ServiceUnavailableError(
            "Google AI services unavailable across all fallback models."
        ) from last_error
    else:
        raise UpstreamAPIError(
            f"All model fallbacks failed: {last_error}"
        ) from last_error
