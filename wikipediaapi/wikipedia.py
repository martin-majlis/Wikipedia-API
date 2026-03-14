from ._http_client import SyncHTTPClient
from ._http_client import USER_AGENT  # noqa: F401
from ._resources import WikipediaResource


class Wikipedia(WikipediaResource, SyncHTTPClient):
    """Wikipedia is wrapper for Wikipedia API."""

    pass
