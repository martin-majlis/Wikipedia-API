from ._http_client import AsyncHTTPClient
from ._resources import AsyncWikipediaResource


class AsyncWikipedia(AsyncWikipediaResource, AsyncHTTPClient):
    """AsyncWikipedia is an async wrapper for the Wikipedia API."""

    pass
