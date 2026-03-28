"""HTTP error for Wikipedia-API requests.

Raised when the Wikipedia API returns a non-success HTTP status code.
"""

from .wikipedia_exception import WikipediaException


class WikiHttpError(WikipediaException):
    """
    Raised when Wikipedia API returns a non-success HTTP status code.

    4xx responses that are not 429 are raised immediately (no retry).
    5xx responses are retried up to ``max_retries`` times and then raise
    this exception if they never succeed.

    :attr status_code: HTTP status code that was received
    :attr url: endpoint URL that returned error
    """

    def __init__(self, status_code: int, url: str) -> None:
        """
        Initialise the HTTP error.

        :param status_code: HTTP status code (e.g. 404, 503)
        :param url: API endpoint URL that returned error
        """
        self.status_code = status_code
        self.url = url
        super().__init__(status_code, url)
