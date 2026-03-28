import httpx
import pytest
import respx

from tests.mock_data import user_agent
import wikipediaapi
from wikipediaapi._http_client import SyncHTTPClient

API_URL = "https://en.wikipedia.org/w/api.php"


class TestSyncHTTPClientInit:
    """Tests for SyncHTTPClient initialisation."""

    def test_user_agent_set_in_client_headers(self):
        client = SyncHTTPClient(user_agent, "en")
        assert user_agent in client._client.headers.get("User-Agent")

    def test_user_agent_appends_library_agent(self):
        client = SyncHTTPClient(user_agent, "en")
        header = client._client.headers.get("User-Agent")
        assert wikipediaapi.USER_AGENT in header

    def test_language_set(self):
        client = SyncHTTPClient(user_agent, "de")
        assert client.language == "de"

    def test_variant_set(self):
        client = SyncHTTPClient(user_agent, "zh", variant="zh-tw")
        assert client.variant == "zh-tw"

    def test_extract_format_default(self):
        from wikipediaapi.extract_format import ExtractFormat

        client = SyncHTTPClient(user_agent, "en")
        assert client.extract_format == ExtractFormat.WIKI

    def test_max_retries_stored(self):
        client = SyncHTTPClient(user_agent, "en", max_retries=5)
        assert client._max_retries == 5

    def test_retry_wait_stored(self):
        client = SyncHTTPClient(user_agent, "en", retry_wait=2.5)
        assert client._retry_wait == 2.5

    def test_extra_api_params_stored(self):
        client = SyncHTTPClient(user_agent, "en", extra_api_params={"foo": "bar"})
        assert client._extra_api_params == {"foo": "bar"}

    def test_missing_user_agent_raises(self):
        with pytest.raises(AssertionError):
            SyncHTTPClient("en")

    def test_empty_language_raises(self):
        with pytest.raises(AssertionError):
            SyncHTTPClient(user_agent, "")

    def test_header_user_agent_takes_precedence(self):
        client = SyncHTTPClient(
            "param-agent",
            "en",
            headers={"User-Agent": "header-agent"},
        )
        header = client._client.headers.get("User-Agent")
        assert "header-agent" in header
        assert "param-agent" not in header


class TestSyncHTTPClientGet:
    """Tests for SyncHTTPClient._get."""

    def setup_method(self):
        self.client = SyncHTTPClient(user_agent, "en", max_retries=0, retry_wait=0.0)

    @respx.mock
    def test_successful_get_returns_json(self):
        data = {"query": {"pages": {"1": {"title": "Test"}}}}
        respx.get(API_URL).mock(return_value=httpx.Response(200, json=data))
        result = self.client._get("en", {"action": "query"})
        assert result == data

    @respx.mock
    def test_get_uses_correct_url(self):
        data = {"ok": True}
        route = respx.get(API_URL).mock(return_value=httpx.Response(200, json=data))
        self.client._get("en", {"action": "query"})
        assert route.called is True

    @respx.mock
    def test_get_de_uses_de_url(self):
        de_url = "https://de.wikipedia.org/w/api.php"
        data = {"ok": True}
        route = respx.get(de_url).mock(return_value=httpx.Response(200, json=data))
        self.client._get("de", {"action": "query"})
        assert route.called is True

    @respx.mock
    def test_404_raises_http_error(self):
        respx.get(API_URL).mock(return_value=httpx.Response(404))
        with pytest.raises(wikipediaapi.WikiHttpError) as ctx:
            self.client._get("en", {"action": "query"})
        assert ctx.value.status_code == 404

    @respx.mock
    def test_500_raises_http_error(self):
        respx.get(API_URL).mock(return_value=httpx.Response(500))
        with pytest.raises(wikipediaapi.WikiHttpError) as ctx:
            self.client._get("en", {"action": "query"})
        assert ctx.value.status_code == 500

    @respx.mock
    def test_429_raises_rate_limit_error(self):
        respx.get(API_URL).mock(return_value=httpx.Response(429, headers={"Retry-After": "10"}))
        with pytest.raises(wikipediaapi.WikiRateLimitError) as ctx:
            self.client._get("en", {"action": "query"})
        assert ctx.value.retry_after == 10

    @respx.mock
    def test_timeout_raises_timeout_error(self):
        respx.get(API_URL).mock(side_effect=httpx.TimeoutException("timeout"))
        with pytest.raises(wikipediaapi.WikiHttpTimeoutError):
            self.client._get("en", {"action": "query"})

    @respx.mock
    def test_connect_error_raises_connection_error(self):
        respx.get(API_URL).mock(side_effect=httpx.ConnectError("err"))
        with pytest.raises(wikipediaapi.WikiConnectionError):
            self.client._get("en", {"action": "query"})

    @respx.mock
    def test_invalid_json_raises_invalid_json_error(self):
        respx.get(API_URL).mock(return_value=httpx.Response(200, content=b"not-json"))
        with pytest.raises(wikipediaapi.WikiInvalidJsonError):
            self.client._get("en", {"action": "query"})


class TestSyncHTTPClientRetry:
    """Tests for retry behaviour in SyncHTTPClient."""

    def setup_method(self):
        self.client = SyncHTTPClient(user_agent, "en", max_retries=2, retry_wait=0.0)

    @respx.mock
    def test_retries_on_500(self):
        success = {"ok": True}
        responses = iter([httpx.Response(500), httpx.Response(200, json=success)])
        route = respx.get(API_URL).mock(side_effect=lambda req: next(responses))
        result = self.client._get("en", {"action": "query"})
        assert result == success
        assert route.call_count == 2

    @respx.mock
    def test_exhausts_retries_on_500(self):
        route = respx.get(API_URL).mock(return_value=httpx.Response(500))
        with pytest.raises(wikipediaapi.WikiHttpError):
            self.client._get("en", {"action": "query"})
        assert route.call_count == 3
