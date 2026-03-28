"""Exception classes for Wikipedia-API errors.

This module defines the exception hierarchy used throughout the Wikipedia-API
library. All library-specific exceptions inherit from WikipediaException,
making it easy to catch all Wikipedia-related errors with a single except
clause while still allowing for more specific error handling when needed.
"""

from .wiki_connection_error import WikiConnectionError
from .wiki_http_error import WikiHttpError
from .wiki_http_timeout_error import WikiHttpTimeoutError
from .wiki_invalid_json_error import WikiInvalidJsonError
from .wiki_rate_limit_error import WikiRateLimitError
from .wikipedia_exception import WikipediaException

__all__ = [
    "WikipediaException",
    "WikiHttpTimeoutError",
    "WikiHttpError",
    "WikiRateLimitError",
    "WikiInvalidJsonError",
    "WikiConnectionError",
]
