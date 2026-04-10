"""Synchronous Wikipedia API client.

This module defines the Wikipedia class which provides a synchronous
interface for accessing Wikipedia content. It combines resource management
with HTTP client functionality to enable straightforward Wikipedia API
interactions.
"""

from .._http_client import USER_AGENT  # noqa: F401
from .._http_client import SyncHTTPClient
from .._resources import WikipediaResource


class Wikipedia(WikipediaResource, SyncHTTPClient):
    """
    Synchronous client for the Wikipedia API.

    Combines :class:`~wikipediaapi.WikipediaResource` (public
    API methods) and :class:`~wikipediaapi._http_client.SyncHTTPClient`
    (blocking ``httpx`` transport with ``tenacity`` retry logic) via
    multiple inheritance.

    All constructor parameters are forwarded to
    :class:`~wikipediaapi._http_client.BaseHTTPClient`.

    Example usage::

        import wikipediaapi

        wiki = wikipediaapi.Wikipedia(
            user_agent='MyProject/1.0 (contact@example.com)',
            language='en',
        )
        page = wiki.page('Python_(programming_language)')
        print(page.summary[:200])

    :param user_agent: HTTP ``User-Agent`` string identifying your
        project.  Must be at least 5 characters long.  See
        https://meta.wikimedia.org/wiki/User-Agent_policy.
    :param language: two-letter (or short) Wikipedia language code,
        e.g. ``"en"``, ``"de"``, ``"fr"``.
        See http://meta.wikimedia.org/wiki/List_of_Wikipedias.
    :param variant: optional language variant for automatic conversion,
        e.g. ``"zh-tw"``; ``None`` disables conversion.
    :param extract_format: controls markup format of extracted text;
        defaults to :attr:`~wikipediaapi.ExtractFormat.WIKI`.
    :param headers: extra HTTP request headers merged with the
        auto-generated ``User-Agent``.
    :param extra_api_params: extra query-string parameters appended to
        every API call (e.g. ``{"converttitles": 1}``).
    :param max_retries: maximum number of retry attempts for transient
        errors (HTTP 429, 5xx, timeouts, connection errors).  Set to
        ``0`` to disable retries entirely.  Defaults to ``3``.
    :param retry_wait: base wait time in seconds between retries;
        actual wait uses exponential backoff
        (``retry_wait * 2 ** attempt``).  For HTTP 429 the
        ``Retry-After`` header value is used instead.  Defaults to
        ``1.0``.
    :param kwargs: additional keyword arguments forwarded to
        ``httpx.Client`` (e.g. ``timeout=30.0``, ``proxies={…}``,
        ``verify=False``).  **Advanced Usage**: These provide direct
        access to httpx capabilities.  For most use cases, prefer the
        standard parameters above.  Use httpx parameters only for specific
        requirements like custom proxies, SSL configuration, or connection pooling.
    """

    pass
