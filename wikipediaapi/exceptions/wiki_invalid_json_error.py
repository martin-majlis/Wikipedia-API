"""Invalid JSON error for Wikipedia-API responses.

Raised when the Wikipedia API returns a 200 response with invalid JSON.
"""

from .wikipedia_exception import WikipediaException


class WikiInvalidJsonError(WikipediaException):
    """
    Raised when Wikipedia API returns a 200 response with invalid JSON.

    This should not normally occur; if it does it may indicate a temporary
    server-side issue or a network proxy mangling the response body.

    :attr url: endpoint URL whose response could not be decoded
    """

    def __init__(self, url: str) -> None:
        """
        Initialise the invalid-JSON error.

        :param url: API endpoint URL that returned malformed JSON
        """
        self.url = url
        super().__init__(url)
