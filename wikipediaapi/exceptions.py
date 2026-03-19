"""Exception classes for Wikipedia-API errors.

This module defines the exception hierarchy used throughout the Wikipedia-API
library. All library-specific exceptions inherit from WikipediaException,
making it easy to catch all Wikipedia-related errors with a single except
clause while still allowing for more specific error handling when needed.
"""


class WikipediaException(Exception):
    """
    Base exception for all Wikipedia-API errors.

    All library-specific exceptions inherit from this class, so callers
    can catch every possible error with a single ``except`` clause::

        try:
            page = wiki.page("Python")
            print(page.summary)
        except wikipediaapi.WikipediaException as e:
            print(f"Wikipedia error: {e}")
    """


class WikiHttpTimeoutError(WikipediaException):
    """
    Raised when a request to the Wikipedia API times out.

    Corresponds to ``httpx.TimeoutException`` from the underlying HTTP
    client.  May be raised after all retry attempts are exhausted.

    :attr url: the endpoint URL that timed out
    """

    def __init__(self, url: str) -> None:
        """
        Initialise the timeout error.

        :param url: the API endpoint URL that timed out
        """
        self.url = url
        super().__init__(url)


class WikiHttpError(WikipediaException):
    """
    Raised when the Wikipedia API returns a non-success HTTP status code.

    4xx responses that are not 429 are raised immediately (no retry).
    5xx responses are retried up to ``max_retries`` times and then raise
    this exception if they never succeed.

    :attr status_code: the HTTP status code that was received
    :attr url: the endpoint URL that returned the error
    """

    def __init__(self, status_code: int, url: str) -> None:
        """
        Initialise the HTTP error.

        :param status_code: HTTP status code (e.g. 404, 503)
        :param url: the API endpoint URL that returned the error
        """
        self.status_code = status_code
        self.url = url
        super().__init__(status_code, url)


class WikiRateLimitError(WikiHttpError):
    """
    Raised when the Wikipedia API returns HTTP 429 (Too Many Requests).

    Subclass of :class:`WikiHttpError` with ``status_code`` always equal
    to ``429``.  The ``retry_after`` attribute is populated from the
    ``Retry-After`` response header when present; the retry logic in
    :class:`~wikipediaapi._http_client.BaseHTTPClient` honours this value
    as the wait time before the next attempt.

    :attr retry_after: seconds to wait before retrying, or ``None`` if
        the ``Retry-After`` header was absent or non-numeric
    :attr url: the endpoint URL that was rate-limited
    """

    def __init__(self, url: str, retry_after: int | None = None) -> None:  # noqa: B042
        """
        Initialise the rate-limit error.

        :param url: the API endpoint URL that returned 429
        :param retry_after: value from the ``Retry-After`` header
            (integer seconds), or ``None`` if the header was absent
        """
        self.retry_after = retry_after
        super().__init__(429, url)


class WikiInvalidJsonError(WikipediaException):
    """
    Raised when the Wikipedia API returns a 200 response with invalid JSON.

    This should not normally occur; if it does it may indicate a temporary
    server-side issue or a network proxy mangling the response body.

    :attr url: the endpoint URL whose response could not be decoded
    """

    def __init__(self, url: str) -> None:
        """
        Initialise the invalid-JSON error.

        :param url: the API endpoint URL that returned malformed JSON
        """
        self.url = url
        super().__init__(url)


class WikiConnectionError(WikipediaException):
    """
    Raised when a network connection to the Wikipedia API cannot be established.

    Corresponds to ``httpx.ConnectError`` or any other
    ``httpx.RequestError`` that is not a timeout.  May be raised after all
    retry attempts are exhausted.

    :attr url: the endpoint URL that could not be reached
    """

    def __init__(self, url: str) -> None:
        """
        Initialise the connection error.

        :param url: the API endpoint URL that could not be reached
        """
        self.url = url
        super().__init__(url)
