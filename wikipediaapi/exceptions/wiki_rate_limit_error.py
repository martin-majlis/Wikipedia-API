"""Rate limit error for Wikipedia-API requests.

Raised when the Wikipedia API returns HTTP 429 (Too Many Requests).
"""

from .wiki_http_error import WikiHttpError


class WikiRateLimitError(WikiHttpError):
    """
    Raised when Wikipedia API returns HTTP 429 (Too Many Requests).

    Subclass of :class:`WikiHttpError` with ``status_code`` always equal
    to ``429``.  The ``retry_after`` attribute is populated from
    ``Retry-After`` response header when present; retry logic in
    :class:`~wikipediaapi._http_client.BaseHTTPClient` honours this value
    as wait time before the next attempt.

    :attr retry_after: seconds to wait before retrying, or ``None`` if
        ``Retry-After`` header was absent or non-numeric
    :attr url: endpoint URL that was rate-limited
    """

    def __init__(self, url: str, retry_after: int | None = None) -> None:  # noqa: B042
        """
        Initialise the rate-limit error.

        :param url: API endpoint URL that returned 429
        :param retry_after: value from ``Retry-After`` header
            (integer seconds), or ``None`` if header was absent
        """
        self.retry_after = retry_after
        super().__init__(429, url)
