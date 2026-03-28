"""HTTP timeout error for Wikipedia-API requests.

Raised when a request to the Wikipedia API times out after all retry
attempts have been exhausted.
"""

from .wikipedia_exception import WikipediaException


class WikiHttpTimeoutError(WikipediaException):
    """
    Raised when a request to Wikipedia API times out.

    Corresponds to ``httpx.TimeoutException`` from the underlying HTTP
    client.  May be raised after all retry attempts are exhausted.

    :attr url: endpoint URL that timed out
    """

    def __init__(self, url: str) -> None:
        """
        Initialise the timeout error.

        :param url: API endpoint URL that timed out
        """
        self.url = url
        super().__init__(url)
