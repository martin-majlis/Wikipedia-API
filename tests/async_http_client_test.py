import httpx
import pytest
import respx

import wikipediaapi
from tests.mock_data import user_agent
from wikipediaapi._http_client import AsyncHTTPClient

API_URL = "https://en.wikipedia.org/w/api.php"


class TestAsyncHTTPClientInit:
    """Tests for AsyncHTTPClient initialisation."""

    def test_user_agent_set_in_client_headers(self):
        client = AsyncHTTPClient(user_agent, "en")
        assert user_agent in client._client.headers.get("User-Agent")

    def test_user_agent_appends_library_agent(self):
        client = AsyncHTTPClient(user_agent, "en")
        header = client._client.headers.get("User-Agent")
        assert wikipediaapi.USER_AGENT in header

    def test_language_set(self):
        client = AsyncHTTPClient(user_agent, "de")
        assert client.language == "de"

    def test_variant_set(self):
        client = AsyncHTTPClient(user_agent, "zh", variant="zh-tw")
        assert client.variant == "zh-tw"

    def test_max_retries_stored(self):
        client = AsyncHTTPClient(user_agent, "en", max_retries=5)
        assert client._max_retries == 5

    def test_retry_wait_stored(self):
        client = AsyncHTTPClient(user_agent, "en", retry_wait=2.5)
        assert client._retry_wait == 2.5

    def test_missing_user_agent_raises(self):
        with pytest.raises(AssertionError):
            AsyncHTTPClient("en")


class TestAsyncHTTPClientGet:
    """Tests for AsyncHTTPClient._get."""

    def setup_method(self):
        self.client = AsyncHTTPClient(user_agent, "en", max_retries=0, retry_wait=0.0)

    @respx.mock
    @pytest.mark.asyncio
    async def test_successful_get_returns_json(self):
        data = {"query": {"pages": {"1": {"title": "Test"}}}}
        respx.get(API_URL).mock(return_value=httpx.Response(200, json=data))
        result = await self.client._get("en", {"action": "query"})
        assert result == data

    @respx.mock
    async def test_get_de_uses_de_url(self):
        de_url = "https://de.wikipedia.org/w/api.php"
        data = {"ok": True}
        route = respx.get(de_url).mock(return_value=httpx.Response(200, json=data))
        await self.client._get("de", {"action": "query"})
        assert route.called is True

    @respx.mock
    async def test_404_raises_http_error(self):
        respx.get(API_URL).mock(return_value=httpx.Response(404))
        with pytest.raises(wikipediaapi.WikiHttpError) as ctx:
            await self.client._get("en", {"action": "query"})
        assert ctx.value.status_code == 404

    @respx.mock
    async def test_429_raises_rate_limit_error(self):
        respx.get(API_URL).mock(return_value=httpx.Response(429, headers={"Retry-After": "10"}))
        with pytest.raises(wikipediaapi.WikiRateLimitError) as ctx:
            await self.client._get("en", {"action": "query"})
        assert ctx.value.retry_after == 10

    @respx.mock
    async def test_timeout_raises_timeout_error(self):
        respx.get(API_URL).mock(side_effect=httpx.TimeoutException("timeout"))
        with pytest.raises(wikipediaapi.WikiHttpTimeoutError):
            await self.client._get("en", {"action": "query"})

    @respx.mock
    async def test_connect_error_raises_connection_error(self):
        respx.get(API_URL).mock(side_effect=httpx.ConnectError("err"))
        with pytest.raises(wikipediaapi.WikiConnectionError):
            await self.client._get("en", {"action": "query"})

    @respx.mock
    async def test_invalid_json_raises_invalid_json_error(self):
        respx.get(API_URL).mock(return_value=httpx.Response(200, content=b"not-json"))
        with pytest.raises(wikipediaapi.WikiInvalidJsonError):
            await self.client._get("en", {"action": "query"})


class TestAsyncHTTPClientRetry:
    """Tests for retry behaviour in AsyncHTTPClient."""

    def setup_method(self):
        self.client = AsyncHTTPClient(user_agent, "en", max_retries=2, retry_wait=0.0)

    @respx.mock
    async def test_retries_on_500(self):
        success = {"ok": True}
        responses = iter([httpx.Response(500), httpx.Response(200, json=success)])
        route = respx.get(API_URL).mock(side_effect=lambda req: next(responses))
        result = await self.client._get("en", {"action": "query"})
        assert result == success
        assert route.call_count == 2

    @respx.mock
    async def test_exhausts_retries_on_500(self):
        route = respx.get(API_URL).mock(return_value=httpx.Response(500))
        with pytest.raises(wikipediaapi.WikiHttpError):
            await self.client._get("en", {"action": "query"})
        assert route.call_count == 3

    @respx.mock
    async def test_retries_on_429(self):
        success = {"ok": True}
        responses = iter([httpx.Response(429), httpx.Response(200, json=success)])
        route = respx.get(API_URL).mock(side_effect=lambda req: next(responses))
        result = await self.client._get("en", {"action": "query"})
        assert result == success
        assert route.call_count == 2
