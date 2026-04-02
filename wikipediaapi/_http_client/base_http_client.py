"""Abstract base for synchronous and asynchronous HTTP clients.

Provides shared constructor logic (parameter validation, header
construction, configuration storage) and stateless helpers used by
both SyncHTTPClient and AsyncHTTPClient.
"""

import logging
from abc import ABC
from abc import abstractmethod
from typing import Any

import httpx  # noqa: F401

from .._version import __version_str__
from ..exceptions import WikiConnectionError  # noqa: F401
from ..exceptions import WikiHttpError
from ..exceptions import WikiHttpTimeoutError  # noqa: F401
from ..exceptions import WikiInvalidJsonError
from ..exceptions import WikiRateLimitError
from ..extract_format import ExtractFormat
from .retry_after_wait import _RetryAfterWait  # noqa: F401
from .retry_utils import _is_retryable  # noqa: F401

USER_AGENT = (
    "Wikipedia-API/" + __version_str__ + "; https://github.com/martin-majlis/Wikipedia-API/"
)

MIN_USER_AGENT_LEN = 5
MAX_LANG_LEN = 5

log = logging.getLogger(__name__)


class BaseHTTPClient(ABC):
    """
    Abstract base for synchronous and asynchronous HTTP clients.

    Provides shared constructor logic (parameter validation, header
    construction, configuration storage) and stateless helpers used by
    both :class:`SyncHTTPClient` and :class:`AsyncHTTPClient`.

    Subclasses must implement ``_get(language, params)`` (sync or async)
    that issues the actual HTTP request.

    **Note on HTTP Library**: This implementation uses ``httpx`` as the underlying
    HTTP client library.  Advanced HTTP configuration (timeouts, proxies,
    SSL settings, connection limits, etc.) is exposed through the
    ``SyncHTTPClient`` and ``AsyncHTTPClient`` classes.  For most use
    cases, use the standard Wikipedia API parameters.  Direct httpx
    configuration should only be needed for advanced use cases.

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
        builds composite ``User-Agent`` header
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
            ``User-Agent`` key is set from *user_agent* if absent
        :param extra_api_params: extra query-string parameters appended
            to every MediaWiki API call
        :param max_retries: number of retry attempts for transient
            errors; ``0`` disables retries
        :param retry_wait: base wait time in seconds between retries
            (exponential backoff); overridden by ``Retry-After`` for 429
        :param kwargs: forwarded to ``httpx`` client constructor
            (e.g. ``timeout=30.0``, ``proxy={'https://': 'http://proxy.example.com:8080'}``,
            ``verify=False``, ``http2=True``); ``timeout`` defaults to ``10.0``.
            **Advanced Usage**: These parameters provide direct access to httpx
            capabilities.  For standard Wikipedia API usage, prefer the
            documented parameters above.  Use httpx parameters only for
            specific requirements like custom proxies, SSL configuration, or
            connection pooling.
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
        Issue a GET request to MediaWiki API and return parsed JSON response.

        Implemented as a blocking def returning dict[str, Any]
        by :class:`SyncHTTPClient`, and as an async def coroutine
        (returning dict[str, Any] when awaited) by
        :class:`AsyncHTTPClient`.  The return type is ``Any`` here to
        accommodate both.

        :param language: two-letter Wikipedia language code; used to
                    build endpoint URL
        :param params: fully-merged query-string parameters
        :return: parsed JSON response dict (sync) or an awaitable
                    thereof (async)
        """

    @staticmethod
    def _build_url(language: str) -> str:
        """
        Build MediaWiki API endpoint URL for given language.

        :param language: two-letter (or short) Wikipedia language code
        :return: full HTTPS URL, e.g.
            ``"https://en.wikipedia.org/w/api.php"``
        """
        return f"https://{language}.wikipedia.org/w/api.php"

    def _process_response(self, r: Any, url: str) -> dict[str, Any]:
        """
        Convert an ``httpx`` response object to a parsed JSON dict.

        Inspects HTTP status code and raises a typed exception for
        every non-success case:

        * ``429`` → :class:`~wikipediaapi.WikiRateLimitError`
          (with ``retry_after`` from ``Retry-After`` header)
        * ``>= 500`` → :class:`~wikipediaapi.WikiHttpError`
        * other non-200 → :class:`~wikipediaapi.WikiHttpError`
        * ``200`` with invalid JSON →
          :class:`~wikipediaapi.WikiInvalidJsonError`

        :param r: ``httpx.Response`` object
        :param url: request URL, embedded in raised exceptions
        :return: parsed JSON response body as a ``dict``
        :raises WikiRateLimitError: on HTTP 429
        :raises WikiHttpError: on HTTP 5xx or other non-200 status
        :raises WikiInvalidJsonError: when 200 body is not valid JSON
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
        except ValueError as err:
            raise WikiInvalidJsonError(url) from err

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
