class UpstreamAPIError(Exception):
    """
    Base exception for all upstream AI service failures.
    """
    


class RateLimitError(UpstreamAPIError):
    """
    Raised when quota/rate limits(HTTP 429) are exhausted across all 
    fallback models.
    """
    

class ServiceUnavailableError(UpstreamAPIError):
    """
    Raised when google servers return temporary outages or
    unavailable (HTTP 503). 
    """
    