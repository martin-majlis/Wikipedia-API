"""Tenacity wait strategy that honours the Retry-After response header.

When the last exception is a WikiRateLimitError with a non-None
retry_after value, that value (in seconds) is returned as the wait duration.
For all other retryable errors, the strategy falls back to exponential backoff.
"""

from typing import Any

from ..exceptions import WikiRateLimitError


class _RetryAfterWait:
    """
    Tenacity wait strategy that honours the ``Retry-After`` response header.

    When the last exception is a :class:`~wikipediaapi.WikiRateLimitError`
    with a non-``None`` ``retry_after`` value, that value (in seconds) is
    returned as wait duration.  For all other retryable errors
    the strategy falls back to exponential backoff::

        wait = retry_wait * 2 ** (attempt_number - 1)

    :attr _retry_wait: base wait time in seconds supplied at construction
    """

    def __init__(self, retry_wait: float) -> None:
        """
        Initialise the wait strategy.

        :param retry_wait: base wait time in seconds; used as
            multiplier for exponential backoff when ``Retry-After`` is
            absent
        """
        self._retry_wait = retry_wait

    def __call__(self, retry_state: Any) -> float:
        """
        Compute the wait time for a given tenacity retry state.

        :param retry_state: tenacity ``RetryCallState`` object; its
            ``outcome`` attribute holds the last exception
        :return: seconds to wait before the next attempt
        """
        exc = retry_state.outcome.exception()
        if isinstance(exc, WikiRateLimitError) and exc.retry_after is not None:
            return float(exc.retry_after)
        return float(self._retry_wait * (2 ** (retry_state.attempt_number - 1)))
