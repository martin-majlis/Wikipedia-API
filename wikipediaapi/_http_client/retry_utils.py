"""Utility functions for HTTP client retry logic.

Provides functions to determine which exceptions should trigger retry attempts.
"""

from ..exceptions import WikiConnectionError
from ..exceptions import WikiHttpError
from ..exceptions import WikiHttpTimeoutError
from ..exceptions import WikiRateLimitError


def _is_retryable(exc: BaseException) -> bool:
    """
    Return ``True`` for exceptions that should trigger a retry attempt.

    The following exception types are considered retryable:

    * :class:`~wikipediaapi.WikiRateLimitError` (HTTP 429)
    * :class:`~wikipediaapi.WikiHttpError` with ``status_code >= 500``
    * :class:`~wikipediaapi.WikiHttpTimeoutError`
    * :class:`~wikipediaapi.WikiConnectionError`

    :param exc: exception raised by a previous attempt
    :return: ``True`` if request should be retried, ``False`` otherwise
    """
    if isinstance(exc, WikiRateLimitError):
        return True
    if isinstance(exc, WikiHttpError) and exc.status_code >= 500:
        return True
    return isinstance(exc, (WikiHttpTimeoutError, WikiConnectionError))
