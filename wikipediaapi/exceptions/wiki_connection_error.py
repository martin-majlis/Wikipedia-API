"""Connection error for Wikipedia-API requests.

Raised when a network connection to the Wikipedia API cannot be established.
"""

from .wikipedia_exception import WikipediaException


class WikiConnectionError(WikipediaException):
    """
    Raised when a network connection to Wikipedia API cannot be established.

    Corresponds to ``httpx.ConnectError`` or any other
    ``httpx.RequestError`` that is not a timeout.  May be raised after all
    retry attempts are exhausted.

    :attr url: endpoint URL that could not be reached
    """

    def __init__(self, url: str) -> None:
        """
        Initialise the connection error.

        :param url: API endpoint URL that could not be reached
        """
        self.url = url
        super().__init__(url)
