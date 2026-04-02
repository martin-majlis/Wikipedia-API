"""Non-blocking HTTP client built on httpx.AsyncClient.

Creates a persistent httpx.AsyncClient at construction time and
uses it for all requests. Retry logic is implemented via
tenacity.AsyncRetrying with _RetryAfterWait as wait
strategy and _is_retryable as retry predicate.
"""

import logging
from typing import Any

import httpx
from tenacity import AsyncRetrying
from tenacity import retry_if_exception
from tenacity import stop_after_attempt

from .base_http_client import BaseHTTPClient
from .retry_after_wait import _RetryAfterWait
from .retry_utils import _is_retryable

log = logging.getLogger(__name__)


class AsyncHTTPClient(BaseHTTPClient):
    """
    Non-blocking HTTP client built on ``httpx.AsyncClient``.

    Creates a persistent ``httpx.AsyncClient`` at construction time and
    uses it for all requests.  Retry logic is implemented via
    ``tenacity.AsyncRetrying`` with :class:`_RetryAfterWait` as wait
    strategy and :func:`_is_retryable` as retry predicate.

    All request methods are coroutines and must be ``await``-ed.

    :attr _client: underlying ``httpx.AsyncClient`` instance
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialise the async client.

        Calls :meth:`BaseHTTPClient.__init__` then creates the shared
        ``httpx.AsyncClient`` with the computed headers and timeout.

        :param args: positional arguments forwarded to
            :class:`BaseHTTPClient`
        :param kwargs: keyword arguments forwarded to
            :class:`BaseHTTPClient`
        """
        super().__init__(*args, **kwargs)
        self._client = httpx.AsyncClient(
            headers=self._default_headers,
            **self._client_kwargs,
            transport=httpx.AsyncHTTPTransport(),
        )

    async def _do_get(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a single (non-retried) async GET request.

        Called by :meth:`_get` on each attempt.  Translates
        ``httpx``-specific exceptions into library exceptions so
        tenacity retry loop sees only :class:`~wikipediaapi.WikipediaException`
        subclasses.

        :param url: full API endpoint URL
        :param params: query-string parameters to send
        :return: parsed JSON response dict
        :raises WikiHttpTimeoutError: on ``httpx.TimeoutException``
        :raises WikiConnectionError: on ``httpx.ConnectError``
        :raises WikiRateLimitError: on HTTP 429
        :raises WikiHttpError: on HTTP 5xx or other non-200
        :raises WikiInvalidJsonError: when 200 body is not valid JSON
        """
        try:
            r = await self._client.get(url, params=params)
        except httpx.TimeoutException as err:
            from ..exceptions import WikiHttpTimeoutError

            raise WikiHttpTimeoutError(url) from err
        except httpx.ConnectError as err:
            from ..exceptions import WikiConnectionError

            raise WikiConnectionError(url) from err
        return self._process_response(r, url)

    async def _get(self, language: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Make an async GET request to Wikipedia API with automatic retry logic.

        Constructs endpoint URL from *language*, logs the full
        request URL, then runs :meth:`_do_get` inside a
        ``tenacity.AsyncRetrying`` loop that retries on transient errors
        up to ``_max_retries`` times.

        :param language: two-letter Wikipedia language code; used to
            build endpoint URL
        :param params: fully-merged query-string parameters (produced
            by :meth:`~wikipediaapi.BaseWikipediaResource
            ._construct_params`)
        :return: parsed JSON response dict
        :raises WikiHttpTimeoutError: if all attempts time out
        :raises WikiConnectionError: if connection fails on all attempts
        :raises WikiRateLimitError: if rate-limited on all attempts
        :raises WikiHttpError: if a server error persists after all
            retries, or on a non-retryable 4xx
        :raises WikiInvalidJsonError: if the response body is not JSON
        """
        url = self._build_url(language)
        log.info(
            "Request URL: %s",
            url + "?" + "&".join([k + "=" + str(v) for k, v in params.items()]),
        )
        retryer = AsyncRetrying(
            stop=stop_after_attempt(1 + self._max_retries),
            wait=_RetryAfterWait(self._retry_wait),
            retry=retry_if_exception(_is_retryable),
            reraise=True,
        )
        try:
            return await retryer(self._do_get, url, params)  # type: ignore[return-value]
        except httpx.RequestError as err:
            from ..exceptions import WikiConnectionError

            raise WikiConnectionError(url) from err
