from collections.abc import Callable
import logging
from typing import Any

from tenacity import AsyncRetrying
from tenacity import retry_if_exception
from tenacity import Retrying
from tenacity import stop_after_attempt

import httpx

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
    """Tenacity wait strategy that honours Retry-After header for rate limits."""

    def __init__(self, retry_wait: float) -> None:
        self._retry_wait = retry_wait

    def __call__(self, retry_state: Any) -> float:
        exc = retry_state.outcome.exception()
        if isinstance(exc, WikiRateLimitError) and exc.retry_after is not None:
            return float(exc.retry_after)
        return float(self._retry_wait * (2 ** (retry_state.attempt_number - 1)))


def _is_retryable(exc: BaseException) -> bool:
    """Return True for exceptions that warrant a retry."""
    if isinstance(exc, WikiRateLimitError):
        return True
    if isinstance(exc, WikiHttpError) and exc.status_code >= 500:
        return True
    return isinstance(exc, (WikiHttpTimeoutError, WikiConnectionError))


class BaseHTTPClient:
    """Base HTTP client: configuration, URL building, response processing."""

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

    @staticmethod
    def _build_url(language: str) -> str:
        return f"https://{language}.wikipedia.org/w/api.php"

    def _process_response(self, r: Any, url: str) -> dict[str, Any]:
        """Convert an httpx response to a dict, raising appropriate exceptions."""
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
        Checks the constructor parameters and throws AssertionError if they are incorrect.
        Otherwise, it normalises them to easy use later on.
        :param language: Language mutation of Wikipedia
        :param variant: Language variant
        :param user_agent: HTTP User-Agent used in requests
        :return: tuple of language, variant, user_agent
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
    """Synchronous HTTP client built on httpx."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._client = httpx.Client(
            headers=self._default_headers,
            timeout=self._client_kwargs.get("timeout", 10.0),
            transport=httpx.HTTPTransport(),
        )

    def _do_get(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            r = self._client.get(url, params=params)
        except httpx.TimeoutException:
            raise WikiHttpTimeoutError(url)
        except httpx.ConnectError:
            raise WikiConnectionError(url)
        return self._process_response(r, url)

    def _get(self, language: str, params: dict[str, Any]) -> dict[str, Any]:
        """Make a GET request to the Wikipedia API with retry logic."""
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
    """Asynchronous HTTP client built on httpx."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._client = httpx.AsyncClient(
            headers=self._default_headers,
            timeout=self._client_kwargs.get("timeout", 10.0),
            transport=httpx.AsyncHTTPTransport(),
        )

    async def _do_get(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            r = await self._client.get(url, params=params)
        except httpx.TimeoutException:
            raise WikiHttpTimeoutError(url)
        except httpx.ConnectError:
            raise WikiConnectionError(url)
        return self._process_response(r, url)

    async def _get(self, language: str, params: dict[str, Any]) -> dict[str, Any]:
        """Make an async GET request to the Wikipedia API with retry logic."""
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
