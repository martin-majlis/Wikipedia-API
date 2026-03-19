from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
import logging
from typing import Any

import httpx
from tenacity import AsyncRetrying
from tenacity import retry_if_exception
from tenacity import Retrying
from tenacity import stop_after_attempt

from ._version import __version_str__
from .exceptions import WikiConnectionError
from .exceptions import WikiHttpError
from .exceptions import WikiHttpTimeoutError
from .exceptions import WikiInvalidJsonError
from .exceptions import WikiRateLimitError
from .extract_format import ExtractFormat

USER_AGENT = (
    "Wikipedia-API/" + __version_str__ + "; https://github.com/martin-majlis/Wikipedia-API/"
)

MIN_USER_AGENT_LEN = 5
MAX_LANG_LEN = 5

log = logging.getLogger(__name__)


class _RetryAfterWait:
    """
    Tenacity wait strategy that honours the ``Retry-After`` response header.

    When the last exception is a :class:`~wikipediaapi.WikiRateLimitError`
    with a non-``None`` ``retry_after`` value, that value (in seconds) is
    returned as the wait duration.  For all other retryable errors the
    strategy falls back to exponential backoff::

        wait = retry_wait * 2 ** (attempt_number - 1)

    :attr _retry_wait: base wait time in seconds supplied at construction
    """

    def __init__(self, retry_wait: float) -> None:
        """
        Initialise the wait strategy.

        :param retry_wait: base wait time in seconds; used as the
            multiplier for exponential backoff when ``Retry-After`` is
            absent
        """
        self._retry_wait = retry_wait

    def __call__(self, retry_state: Any) -> float:
        """
        Compute the wait time for a given tenacity retry state.

        :param retry_state: tenacity ``RetryCallState`` object; its
            ``outcome`` attribute holds the last exception
        :return: seconds to wait before the next attempt
        """
        exc = retry_state.outcome.exception()
        if isinstance(exc, WikiRateLimitError) and exc.retry_after is not None:
            return float(exc.retry_after)
        return float(self._retry_wait * (2 ** (retry_state.attempt_number - 1)))


def _is_retryable(exc: BaseException) -> bool:
    """
    Return ``True`` for exceptions that should trigger a retry attempt.

    The following exception types are considered retryable:

    * :class:`~wikipediaapi.WikiRateLimitError` (HTTP 429)
    * :class:`~wikipediaapi.WikiHttpError` with ``status_code >= 500``
    * :class:`~wikipediaapi.WikiHttpTimeoutError`
    * :class:`~wikipediaapi.WikiConnectionError`

    :param exc: exception raised by a previous attempt
    :return: ``True`` if the request should be retried, ``False`` otherwise
    """
    if isinstance(exc, WikiRateLimitError):
        return True
    if isinstance(exc, WikiHttpError) and exc.status_code >= 500:
        return True
    return isinstance(exc, (WikiHttpTimeoutError, WikiConnectionError))


class BaseHTTPClient(ABC):
    """
    Abstract base for synchronous and asynchronous HTTP clients.

    Provides shared constructor logic (parameter validation, header
    construction, configuration storage) and stateless helpers used by
    both :class:`SyncHTTPClient` and :class:`AsyncHTTPClient`.

    Subclasses must implement ``_get(language, params)`` (sync or async)
    that issues the actual HTTP request.

    Instance attributes set by :meth:`__init__`:

    :attr language: normalised Wikipedia language code (e.g. ``"en"``)
    :attr variant: normalised language variant, or ``None``
    :attr extract_format: :class:`~wikipediaapi.ExtractFormat` used for
        text extraction
    """

    def __init__(
        self,
        user_agent: str,
        language: str = "en",
        variant: str | None = None,
        extract_format: ExtractFormat = ExtractFormat.WIKI,
        headers: dict[str, Any] | None = None,
        extra_api_params: dict[str, Any] | None = None,
        max_retries: int = 3,
        retry_wait: float = 1.0,
        **kwargs: Any,
    ) -> None:
        """
        Initialise shared HTTP client configuration.

        Validates *user_agent* and *language*, normalises both values,
        builds the composite ``User-Agent`` header
        (``"<user_agent> (<library_ua>)"``), and stores all settings for
        use by subclass transport implementations.

        :param user_agent: caller-supplied ``User-Agent`` string;
            must be at least 5 characters long
        :param language: Wikipedia language code (e.g. ``"en"``);
            strip-and-lowercased automatically
        :param variant: language variant (e.g. ``"zh-tw"``) or ``None``
        :param extract_format: markup format for text extraction;
            defaults to :attr:`~wikipediaapi.ExtractFormat.WIKI`
        :param headers: extra HTTP headers to send with every request;
            the ``User-Agent`` key is set from *user_agent* if absent
        :param extra_api_params: extra query-string parameters appended
            to every MediaWiki API call
        :param max_retries: number of retry attempts for transient
            errors; ``0`` disables retries
        :param retry_wait: base wait time in seconds between retries
            (exponential backoff); overridden by ``Retry-After`` for 429
        :param kwargs: forwarded to the ``httpx`` client constructor
            (e.g. ``timeout=30.0``); ``timeout`` defaults to ``10.0``
        :raises AssertionError: if *user_agent* is too short or
            *language* is empty
        """
        kwargs.setdefault("timeout", 10.0)

        default_headers: dict[str, Any] = {} if headers is None else dict(headers)
        if user_agent is not None:
            default_headers.setdefault("User-Agent", user_agent)

        used_language, used_variant, used_user_agent = self._check_and_correct_params(
            language,
            variant,
            default_headers.get("User-Agent"),
        )

        default_headers["User-Agent"] = used_user_agent + " (" + USER_AGENT + ")"

        self.language = used_language
        self.variant = used_variant
        self.extract_format = extract_format

        log.info(
            "Wikipedia: language=%s, user_agent: %s, extract_format=%s",
            self.language,
            default_headers["User-Agent"],
            self.extract_format,
        )

        self._extra_api_params = extra_api_params
        self._max_retries = max_retries
        self._retry_wait = retry_wait
        self._default_headers = default_headers
        self._client_kwargs = kwargs

    @abstractmethod
    def _get(self, language: str, params: dict[str, Any]) -> Any:
        """
        Issue a GET request to the MediaWiki API and return parsed JSON response.

        Implemented as a blocking def returning dict[str, Any]

                Implemented as a blocking ``def`` returning ``dict[str, Any]``
                by :class:`SyncHTTPClient`, and as an ``async def`` coroutine
                (returning ``dict[str, Any]`` when awaited) by
                :class:`AsyncHTTPClient`.  The return type is ``Any`` here to
                accommodate both.

                :param language: two-letter Wikipedia language code; used to
                    build the endpoint URL
                :param params: fully-merged query-string parameters
                :return: parsed JSON response dict (sync) or an awaitable
                    thereof (async)
        """

    @staticmethod
    def _build_url(language: str) -> str:
        """
        Build the MediaWiki API endpoint URL for the given language.

        :param language: two-letter (or short) Wikipedia language code
        :return: full HTTPS URL, e.g.
            ``"https://en.wikipedia.org/w/api.php"``
        """
        return f"https://{language}.wikipedia.org/w/api.php"

    def _process_response(self, r: Any, url: str) -> dict[str, Any]:
        """
        Convert an ``httpx`` response object to a parsed JSON dict.

        Inspects the HTTP status code and raises a typed exception for
        every non-success case:

        * ``429`` → :class:`~wikipediaapi.WikiRateLimitError`
          (with ``retry_after`` from the ``Retry-After`` header)
        * ``>= 500`` → :class:`~wikipediaapi.WikiHttpError`
        * other non-200 → :class:`~wikipediaapi.WikiHttpError`
        * ``200`` with invalid JSON →
          :class:`~wikipediaapi.WikiInvalidJsonError`

        :param r: ``httpx.Response`` object
        :param url: request URL, embedded in raised exceptions
        :return: parsed JSON response body as a ``dict``
        :raises WikiRateLimitError: on HTTP 429
        :raises WikiHttpError: on HTTP 5xx or other non-200 status
        :raises WikiInvalidJsonError: when the 200 body is not valid JSON
        """
        if r.status_code == 429:
            retry_after = r.headers.get("Retry-After")
            raise WikiRateLimitError(
                url,
                int(retry_after) if retry_after and retry_after.isdigit() else None,
            )
        if r.status_code >= 500:
            raise WikiHttpError(r.status_code, url)
        if r.status_code != 200:
            raise WikiHttpError(r.status_code, url)
        try:
            return r.json()  # type: ignore[no-any-return]
        except ValueError:
            raise WikiInvalidJsonError(url)

    @staticmethod
    def _check_and_correct_params(
        language: str | None, variant: str | None, user_agent: str | None
    ) -> tuple[str, str | None, str]:
        """
        Validate and normalise constructor parameters.

        Raises :class:`AssertionError` with a human-readable message if
        *user_agent* is too short or *language* is empty.  Issues a
        warning log if *language* looks suspiciously long (> 5 chars).
        Both *language* and *variant* are stripped and lower-cased.

        :param language: raw language code supplied by the caller
        :param variant: raw language variant supplied by the caller
        :param user_agent: raw user-agent string supplied by the caller
        :return: tuple of ``(language, variant, user_agent)`` where
            *language* and *variant* are normalised and *user_agent* is
            returned unchanged
        :raises AssertionError: if *user_agent* is ``None`` or shorter
            than :data:`MIN_USER_AGENT_LEN`, or if *language* is empty
        """
        if not user_agent or len(user_agent) < MIN_USER_AGENT_LEN:
            raise AssertionError(
                "Please, be nice to Wikipedia and specify user agent - "
                + "https://meta.wikimedia.org/wiki/User-Agent_policy. Current user_agent: '"
                + str(user_agent)
                + "' is not sufficient. "
                + "Use Wikipedia(user_agent='your-user-agent', language='"
                + (str(user_agent) or "your-language")
                + "')"
            )

        if not language:
            raise AssertionError(
                "Specify language. Current language: '"
                + str(language)
                + "' is not sufficient. "
                + "Use Wikipedia(user_agent='"
                + str(user_agent)
                + "', language='your-language')"
            )

        used_language = language.strip().lower()
        if len(used_language) > MAX_LANG_LEN:
            log.warning(
                "Used language '%s' is longer than %d. It is suspicious",
                used_language,
                MAX_LANG_LEN,
            )

        return (
            used_language,
            variant.strip().lower() if variant else variant,
            user_agent,
        )


class SyncHTTPClient(BaseHTTPClient):
    """
    Blocking HTTP client built on ``httpx.Client``.

    Creates a persistent ``httpx.Client`` at construction time and uses
    it for all requests.  Retry logic is implemented via
    ``tenacity.Retrying`` with :class:`_RetryAfterWait` as the wait
    strategy and :func:`_is_retryable` as the retry predicate.

    :attr _client: the underlying ``httpx.Client`` instance
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialise the sync client.

        Calls :meth:`BaseHTTPClient.__init__` then creates the shared
        ``httpx.Client`` with the computed headers and timeout.

        :param args: positional arguments forwarded to
            :class:`BaseHTTPClient`
        :param kwargs: keyword arguments forwarded to
            :class:`BaseHTTPClient`
        """
        super().__init__(*args, **kwargs)
        self._client = httpx.Client(
            headers=self._default_headers,
            timeout=self._client_kwargs.get("timeout", 10.0),
            transport=httpx.HTTPTransport(),
        )

    def _do_get(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a single (non-retried) GET request.

        Called by :meth:`_get` on each attempt.  Translates
        ``httpx``-specific exceptions into library exceptions so the
        tenacity retry loop sees only :class:`~wikipediaapi.WikipediaException`
        subclasses.

        :param url: full API endpoint URL
        :param params: query-string parameters to send
        :return: parsed JSON response dict
        :raises WikiHttpTimeoutError: on ``httpx.TimeoutException``
        :raises WikiConnectionError: on ``httpx.ConnectError``
        :raises WikiRateLimitError: on HTTP 429
        :raises WikiHttpError: on HTTP 5xx or other non-200
        :raises WikiInvalidJsonError: when the 200 body is not valid JSON
        """
        try:
            r = self._client.get(url, params=params)
        except httpx.TimeoutException:
            raise WikiHttpTimeoutError(url)
        except httpx.ConnectError:
            raise WikiConnectionError(url)
        return self._process_response(r, url)

    def _get(self, language: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Make a GET request to the Wikipedia API with automatic retry logic.

        Constructs the endpoint URL from *language*, logs the full
        request URL, then runs :meth:`_do_get` inside a
        ``tenacity.Retrying`` loop that retries on transient errors
        up to ``_max_retries`` times.

        :param language: two-letter Wikipedia language code; used to
            build the endpoint URL
        :param params: fully-merged query-string parameters (produced
            by :meth:`~wikipediaapi._resources.BaseWikipediaResource
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
        retryer: Callable[..., Any] = Retrying(
            stop=stop_after_attempt(1 + self._max_retries),
            wait=_RetryAfterWait(self._retry_wait),
            retry=retry_if_exception(_is_retryable),
            reraise=True,
        )
        try:
            return retryer(self._do_get, url, params)  # type: ignore[no-any-return]
        except httpx.RequestError:
            raise WikiConnectionError(url)


class AsyncHTTPClient(BaseHTTPClient):
    """
    Non-blocking HTTP client built on ``httpx.AsyncClient``.

    Creates a persistent ``httpx.AsyncClient`` at construction time and
    uses it for all requests.  Retry logic is implemented via
    ``tenacity.AsyncRetrying`` with :class:`_RetryAfterWait` as the wait
    strategy and :func:`_is_retryable` as the retry predicate.

    All request methods are coroutines and must be ``await``-ed.

    :attr _client: the underlying ``httpx.AsyncClient`` instance
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
            timeout=self._client_kwargs.get("timeout", 10.0),
            transport=httpx.AsyncHTTPTransport(),
        )

    async def _do_get(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a single (non-retried) async GET request.

        Called by :meth:`_get` on each attempt.  Translates
        ``httpx``-specific exceptions into library exceptions so the
        tenacity retry loop sees only :class:`~wikipediaapi.WikipediaException`
        subclasses.

        :param url: full API endpoint URL
        :param params: query-string parameters to send
        :return: parsed JSON response dict
        :raises WikiHttpTimeoutError: on ``httpx.TimeoutException``
        :raises WikiConnectionError: on ``httpx.ConnectError``
        :raises WikiRateLimitError: on HTTP 429
        :raises WikiHttpError: on HTTP 5xx or other non-200
        :raises WikiInvalidJsonError: when the 200 body is not valid JSON
        """
        try:
            r = await self._client.get(url, params=params)
        except httpx.TimeoutException:
            raise WikiHttpTimeoutError(url)
        except httpx.ConnectError:
            raise WikiConnectionError(url)
        return self._process_response(r, url)

    async def _get(self, language: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Make an async GET request to the Wikipedia API with automatic retry logic.

        Constructs the endpoint URL from *language*, logs the full
        request URL, then runs :meth:`_do_get` inside a
        ``tenacity.AsyncRetrying`` loop that retries on transient errors
        up to ``_max_retries`` times.

        :param language: two-letter Wikipedia language code; used to
            build the endpoint URL
        :param params: fully-merged query-string parameters (produced
            by :meth:`~wikipediaapi._resources.BaseWikipediaResource
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
        retryer: AsyncRetrying = AsyncRetrying(
            stop=stop_after_attempt(1 + self._max_retries),
            wait=_RetryAfterWait(self._retry_wait),
            retry=retry_if_exception(_is_retryable),
            reraise=True,
        )
        try:
            return await retryer(self._do_get, url, params)  # type: ignore[return-value]
        except httpx.RequestError:
            raise WikiConnectionError(url)
