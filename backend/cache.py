import logging
import time

logger = logging.getLogger(__name__)

RESPONSE_CACHE: dict[tuple[str,str], str] = {}
LAST_REQUEST_TIME: float = 0.0
MIN_REQUEST_INTERVAL: float = 1.0

def get_cached_response(session_id: str, prompt:str) -> str | None:
    """
    Retrieves a cache response if an exact match exist for the session.
    """
    key = (session_id, prompt.strip().lower())
    return RESPONSE_CACHE.get(key)


def store_cache_response(session_id: str, prompt: str, response: str) -> None:
    """
    Save a prompt-response pair to the in-memory chache.
    """
    key = (session_id, prompt.strip().lower())
    RESPONSE_CACHE[key] = response

def enforce_request_pacing() -> None:
    """
    Enforces a minimum interval between outgoing requests to prevent burst in
    rate limits.
    """
    global LAST_REQUEST_TIME
    now = time.time()
    elapsed = now - LAST_REQUEST_TIME

    if elapsed < MIN_REQUEST_INTERVAL:
        sleep_duration = MIN_REQUEST_INTERVAL - elapsed
        logger.info(f"Pacing request. sleeping for {sleep_duration:.2f}s...")
        time.sleep(sleep_duration)

    LAST_REQUEST_TIME = time.time()