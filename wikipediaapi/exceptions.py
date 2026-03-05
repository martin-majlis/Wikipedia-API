class WikipediaException(Exception):
    """Base exception for Wikipedia-API."""


class WikiHttpTimeoutError(WikipediaException):
    """Request to Wikipedia API timed out."""

    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(url)


class WikiHttpError(WikipediaException):
    """Non-success HTTP status from Wikipedia API."""

    def __init__(self, status_code: int, url: str) -> None:
        self.status_code = status_code
        self.url = url
        super().__init__(status_code, url)


class WikiRateLimitError(WikiHttpError):
    """HTTP 429 - Too Many Requests."""

    def __init__(self, url: str, retry_after: int | None = None) -> None:  # noqa: B042
        self.retry_after = retry_after
        super().__init__(429, url)


class WikiInvalidJsonError(WikipediaException):
    """Response body was not valid JSON."""

    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(url)


class WikiConnectionError(WikipediaException):
    """Could not connect to Wikipedia API."""

    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(url)
