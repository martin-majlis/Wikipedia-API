"""Asynchronous Wikipedia API client.

This module defines the AsyncWikipedia class which provides an asynchronous
interface for accessing Wikipedia content. It combines async resource management
with async HTTP client functionality to enable high-performance Wikipedia API
interactions.
"""

from ._http_client import AsyncHTTPClient
from ._resources import AsyncWikipediaResource


class AsyncWikipedia(AsyncWikipediaResource, AsyncHTTPClient):
    """
    Asynchronous client for the Wikipedia API.

    Combines :class:`~wikipediaapi._resources.AsyncWikipediaResource`
    (public async API methods) and
    :class:`~wikipediaapi._http_client.AsyncHTTPClient` (non-blocking
    ``httpx`` transport with ``tenacity`` retry logic) via multiple
    inheritance.

    All constructor parameters are forwarded to
    :class:`~wikipediaapi._http_client.BaseHTTPClient`.

    Unlike :class:`~wikipediaapi.Wikipedia`, the page object returned by
    :meth:`page` is an :class:`~wikipediaapi.AsyncWikipediaPage` whose
    data-fetching methods are coroutines and must be ``await``-ed.

    Example usage::

        import asyncio
        import wikipediaapi

        async def main():
            wiki = wikipediaapi.AsyncWikipedia(
                user_agent='MyProject/1.0 (contact@example.com)',
                language='en',
            )
            page = wiki.page('Python_(programming_language)')
            print(await page.summary)

        asyncio.run(main())

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
        ``httpx.AsyncClient`` (e.g. ``timeout=30.0``).
    """

    pass
