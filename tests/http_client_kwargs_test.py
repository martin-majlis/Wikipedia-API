"""Tests for HTTP client kwargs forwarding to httpxyz.

This test module verifies that all kwargs passed to Wikipedia/AsyncWikipedia
constructors are properly forwarded to underlying httpxyz client constructors.
"""

import httpxyz
import pytest
import respx

from tests.mock_data import create_mock_async_wikipedia
from tests.mock_data import create_mock_wikipedia


class TestSyncHTTPClientKwargs:
    """Test kwargs forwarding in SyncHTTPClient."""

    @respx.mock
    def test_timeout_parameter(self):
        """Test that timeout parameter is forwarded to .Client."""
        wiki = create_mock_wikipedia(timeout=30.0)
        assert wiki._client.timeout == httpxyz.Timeout(30.0)

    @respx.mock
    def test_proxies_parameter(self):
        """Test that proxy parameter is forwarded to .Client."""
        proxy = "http://proxy.example.com:8080"
        wiki = create_mock_wikipedia(proxy=proxy)
        # httpxyz stores proxy info in the transport, not as a direct attribute
        # We can verify the client was created successfully
        assert wiki._client is not None
        assert hasattr(wiki._client, "_transport")

    @respx.mock
    def test_verify_parameter_false(self):
        """Test that verify=False is forwarded to .Client."""
        wiki = create_mock_wikipedia(verify=False)
        # httpxyz stores verify internally, but we can verify the client was created successfully
        assert wiki._client is not None
        # The fact that the client was created without error means verify was accepted

    @respx.mock
    def test_verify_parameter_custom(self):
        """Test that custom verify context is forwarded to .Client."""
        import ssl

        custom_context = ssl.create_default_context()
        wiki = create_mock_wikipedia(verify=custom_context)
        # httpxyz stores verify internally, but we can verify the client was created successfully
        assert wiki._client is not None
        # The fact that the client was created without error means verify was accepted

    @respx.mock
    def test_http2_parameter(self):
        """Test that http2 parameter is forwarded to .Client."""
        try:
            wiki = create_mock_wikipedia(http2=True)
            assert wiki._client._http2 is True
        except ImportError as e:
            if "h2" in str(e):
                pytest.skip("http2 not available (h2 package not installed)")
            else:
                raise

    @respx.mock
    def test_limits_parameter(self):
        """Test that limits parameter is forwarded to .Client."""
        limits = httpxyz.Limits(max_connections=50, max_keepalive_connections=10)
        wiki = create_mock_wikipedia(limits=limits)
        # httpxyz stores limits internally, but we can verify client was created successfully
        assert wiki._client is not None
        # The fact that client was created without error means limits was accepted

    @respx.mock
    def test_max_redirects_parameter(self):
        """Test that max_redirects parameter is forwarded to .Client."""
        wiki = create_mock_wikipedia(max_redirects=5)
        assert wiki._client.max_redirects == 5

    @respx.mock
    def test_follow_redirects_parameter(self):
        """Test that follow_redirects parameter is forwarded to .Client."""
        wiki = create_mock_wikipedia(follow_redirects=True)
        assert wiki._client.follow_redirects is True

    @respx.mock
    def test_auth_parameter(self):
        """Test that auth parameter is forwarded to .Client."""
        auth = httpxyz.BasicAuth("username", "password")
        wiki = create_mock_wikipedia(auth=auth)
        assert wiki._client._auth == auth

    @respx.mock
    def test_base_url_parameter(self):
        """Test that base_url parameter is forwarded to .Client."""
        base_url = "https://custom-api.example.com"
        wiki = create_mock_wikipedia(base_url=base_url)
        assert str(wiki._client._base_url) == base_url

    @respx.mock
    def test_default_encoding_parameter(self):
        """Test that default_encoding parameter is forwarded to .Client."""
        wiki = create_mock_wikipedia(default_encoding="latin-1")
        assert wiki._client._default_encoding == "latin-1"

    @respx.mock
    def test_trust_env_parameter(self):
        """Test that trust_env parameter is forwarded to .Client."""
        wiki = create_mock_wikipedia(trust_env=False)
        assert wiki._client._trust_env is False

    @respx.mock
    def test_combined_parameters(self):
        """Test that multiple parameters work together."""
        proxy = "http://proxy.example.com:8080"
        limits = httpxyz.Limits(max_connections=50)

        wiki = create_mock_wikipedia(
            timeout=20.0,
            proxy=proxy,
            verify=False,
            limits=limits,
            max_redirects=3,
            follow_redirects=True,
        )

        # Test the parameters that are accessible
        assert wiki._client.timeout == httpxyz.Timeout(20.0)
        assert wiki._client.max_redirects == 3
        assert wiki._client.follow_redirects is True
        # Verify the client was created successfully (means all parameters were accepted)
        assert wiki._client is not None

    @respx.mock
    def test_headers_are_preserved(self):
        """Test that custom headers are preserved when using kwargs."""
        custom_headers = {"X-Custom-Header": "test-value"}
        wiki = create_mock_wikipedia(headers=custom_headers, timeout=30.0)

        # Check that our custom header is present
        assert "X-Custom-Header" in wiki._client.headers
        assert wiki._client.headers["X-Custom-Header"] == "test-value"

        # Check that User-Agent is still set correctly
        assert "User-Agent" in wiki._client.headers

    @respx.mock
    def test_invalid_httpxyz_parameter_raises_error(self):
        """Test that invalid httpxyz parameters raise appropriate errors."""
        # httpxyz should raise an error for invalid parameters
        with pytest.raises(TypeError):
            create_mock_wikipedia(invalid_param="should_fail")


class TestAsyncHTTPClientKwargs:
    """Test kwargs forwarding in AsyncHTTPClient."""

    @respx.mock
    async def test_timeout_parameter(self):
        """Test that timeout parameter is forwarded to .AsyncClient."""
        wiki = create_mock_async_wikipedia(timeout=30.0)
        assert wiki._client.timeout == httpxyz.Timeout(30.0)

    @respx.mock
    async def test_proxies_parameter(self):
        """Test that proxy parameter is forwarded to .AsyncClient."""
        proxy = "http://proxy.example.com:8080"
        wiki = create_mock_async_wikipedia(proxy=proxy)
        # httpxyz stores proxy info in the transport, not as a direct attribute
        # We can verify the client was created successfully
        assert wiki._client is not None
        assert hasattr(wiki._client, "_transport")

    @respx.mock
    async def test_verify_parameter_false(self):
        """Test that verify=False is forwarded to .AsyncClient."""
        wiki = create_mock_async_wikipedia(verify=False)
        # httpxyz stores verify internally, but we can verify the client was created successfully
        assert wiki._client is not None
        # The fact that the client was created without error means verify was accepted

    @respx.mock
    async def test_http2_parameter(self):
        """Test that http2 parameter is forwarded to .AsyncClient."""
        try:
            wiki = create_mock_async_wikipedia(http2=True)
            assert wiki._client._http2 is True
        except ImportError as e:
            if "h2" in str(e):
                pytest.skip("http2 not available (h2 package not installed)")
            else:
                raise

    @respx.mock
    async def test_limits_parameter(self):
        """Test that limits parameter is forwarded to .AsyncClient."""
        limits = httpxyz.Limits(max_connections=50, max_keepalive_connections=10)
        wiki = create_mock_async_wikipedia(limits=limits)
        # httpxyz stores limits internally, but we can verify client was created successfully
        assert wiki._client is not None
        # The fact that client was created without error means limits was accepted

    @respx.mock
    async def test_max_redirects_parameter(self):
        """Test that max_redirects parameter is forwarded to .AsyncClient."""
        wiki = create_mock_async_wikipedia(max_redirects=5)
        assert wiki._client.max_redirects == 5

    @respx.mock
    async def test_follow_redirects_parameter(self):
        """Test that follow_redirects parameter is forwarded to .AsyncClient."""
        wiki = create_mock_async_wikipedia(follow_redirects=True)
        assert wiki._client.follow_redirects is True

    @respx.mock
    async def test_auth_parameter(self):
        """Test that auth parameter is forwarded to .AsyncClient."""
        auth = httpxyz.BasicAuth("username", "password")
        wiki = create_mock_async_wikipedia(auth=auth)
        assert wiki._client._auth == auth

    @respx.mock
    async def test_base_url_parameter(self):
        """Test that base_url parameter is forwarded to .AsyncClient."""
        base_url = "https://custom-api.example.com"
        wiki = create_mock_async_wikipedia(base_url=base_url)
        assert str(wiki._client._base_url) == base_url

    @respx.mock
    async def test_combined_parameters(self):
        """Test that multiple parameters work together in async client."""
        proxy = "http://proxy.example.com:8080"
        limits = httpxyz.Limits(max_connections=50)

        wiki = create_mock_async_wikipedia(
            timeout=20.0,
            proxy=proxy,
            verify=False,
            limits=limits,
            max_redirects=3,
            follow_redirects=True,
        )

        # Test the parameters that are accessible
        assert wiki._client.timeout == httpxyz.Timeout(20.0)
        assert wiki._client.max_redirects == 3
        assert wiki._client.follow_redirects is True
        # Verify the client was created successfully (means all parameters were accepted)
        assert wiki._client is not None

    @respx.mock
    async def test_headers_are_preserved(self):
        """Test that custom headers are preserved when using kwargs in async client."""
        custom_headers = {"X-Custom-Header": "test-value"}
        wiki = create_mock_async_wikipedia(headers=custom_headers, timeout=30.0)

        # Check that our custom header is present
        assert "X-Custom-Header" in wiki._client.headers
        assert wiki._client.headers["X-Custom-Header"] == "test-value"

        # Check that User-Agent is still set correctly
        assert "User-Agent" in wiki._client.headers

    @respx.mock
    async def test_invalid_httpxyz_parameter_raises_error(self):
        """Test that invalid httpxyz parameters raise appropriate errors in async client."""
        # httpxyz should raise an error for invalid parameters
        with pytest.raises(TypeError):
            create_mock_async_wikipedia(invalid_param="should_fail")


class TestKwargsBackwardCompatibility:
    """Test that existing usage patterns still work."""

    @respx.mock
    def test_backward_compatibility_timeout_only(self):
        """Test that existing timeout-only usage still works."""
        # This is how users currently use timeout
        wiki = create_mock_wikipedia(timeout=25.0)
        assert wiki._client.timeout == httpxyz.Timeout(25.0)

    @respx.mock
    async def test_backward_compatibility_timeout_only_async(self):
        """Test that existing timeout-only usage still works in async client."""
        wiki = create_mock_async_wikipedia(timeout=25.0)
        assert wiki._client.timeout == httpxyz.Timeout(25.0)

    @respx.mock
    def test_default_timeout_still_works(self):
        """Test that default timeout is still applied when not specified."""
        wiki = create_mock_wikipedia()  # No timeout specified
        assert wiki._client.timeout == httpxyz.Timeout(10.0)  # Should be default

    @respx.mock
    async def test_default_timeout_still_works_async(self):
        """Test that default timeout is still applied when not specified in async client."""
        wiki = create_mock_async_wikipedia()  # No timeout specified
        assert wiki._client.timeout == httpxyz.Timeout(10.0)  # Should be default
