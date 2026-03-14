import unittest

import respx

import httpx
from tests.mock_data import user_agent
import wikipediaapi

API_URL = "https://en.wikipedia.org/w/api.php"


class TestQueryHttpErrors(unittest.TestCase):
    """Tests for _get HTTP error handling."""

    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en", max_retries=0, retry_wait=0.0)

    @respx.mock
    def test_http_404_raises_http_error(self):
        respx.get(API_URL).mock(return_value=httpx.Response(404))
        with self.assertRaises(wikipediaapi.WikiHttpError) as ctx:
            self.wiki._get("en", {"action": "query"})
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIsInstance(ctx.exception, wikipediaapi.WikipediaException)

    @respx.mock
    def test_http_403_raises_http_error(self):
        respx.get(API_URL).mock(return_value=httpx.Response(403))
        with self.assertRaises(wikipediaapi.WikiHttpError) as ctx:
            self.wiki._get("en", {"action": "query"})
        self.assertEqual(ctx.exception.status_code, 403)

    @respx.mock
    def test_http_429_raises_rate_limit_error(self):
        respx.get(API_URL).mock(return_value=httpx.Response(429, headers={"Retry-After": "5"}))
        with self.assertRaises(wikipediaapi.WikiRateLimitError) as ctx:
            self.wiki._get("en", {"action": "query"})
        self.assertEqual(ctx.exception.status_code, 429)
        self.assertEqual(ctx.exception.retry_after, 5)
        self.assertIsInstance(ctx.exception, wikipediaapi.WikiHttpError)

    @respx.mock
    def test_http_429_without_retry_after(self):
        respx.get(API_URL).mock(return_value=httpx.Response(429))
        with self.assertRaises(wikipediaapi.WikiRateLimitError) as ctx:
            self.wiki._get("en", {"action": "query"})
        self.assertIsNone(ctx.exception.retry_after)

    @respx.mock
    def test_http_500_raises_http_error(self):
        respx.get(API_URL).mock(return_value=httpx.Response(500))
        with self.assertRaises(wikipediaapi.WikiHttpError) as ctx:
            self.wiki._get("en", {"action": "query"})
        self.assertEqual(ctx.exception.status_code, 500)

    @respx.mock
    def test_http_503_raises_http_error(self):
        respx.get(API_URL).mock(return_value=httpx.Response(503))
        with self.assertRaises(wikipediaapi.WikiHttpError) as ctx:
            self.wiki._get("en", {"action": "query"})
        self.assertEqual(ctx.exception.status_code, 503)

    @respx.mock
    def test_invalid_json_raises_invalid_json_error(self):
        respx.get(API_URL).mock(return_value=httpx.Response(200, content=b"not json"))
        with self.assertRaises(wikipediaapi.WikiInvalidJsonError):
            self.wiki._get("en", {"action": "query"})

    @respx.mock
    def test_timeout_raises_http_timeout_error(self):
        respx.get(API_URL).mock(side_effect=httpx.TimeoutException("timeout"))
        with self.assertRaises(wikipediaapi.WikiHttpTimeoutError):
            self.wiki._get("en", {"action": "query"})

    @respx.mock
    def test_connection_error_raises_connection_error(self):
        respx.get(API_URL).mock(side_effect=httpx.ConnectError("conn error"))
        with self.assertRaises(wikipediaapi.WikiConnectionError):
            self.wiki._get("en", {"action": "query"})

    @respx.mock
    def test_request_exception_raises_connection_error(self):
        respx.get(API_URL).mock(side_effect=httpx.RequestError("request error"))
        with self.assertRaises(wikipediaapi.WikiConnectionError):
            self.wiki._get("en", {"action": "query"})

    @respx.mock
    def test_http_200_valid_json_returns_data(self):
        expected = {"query": {"pages": {}}}
        respx.get(API_URL).mock(return_value=httpx.Response(200, json=expected))
        result = self.wiki._get("en", {"action": "query"})
        self.assertEqual(result, expected)


class TestQueryRetryLogic(unittest.TestCase):
    """Tests for _get retry behavior."""

    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en", max_retries=2, retry_wait=0.0)

    @respx.mock
    def test_retry_on_429_then_success(self):
        success_data = {"query": {"pages": {}}}
        responses = iter([httpx.Response(429), httpx.Response(200, json=success_data)])
        route = respx.get(API_URL).mock(side_effect=lambda req: next(responses))
        result = self.wiki._get("en", {"action": "query"})
        self.assertEqual(result, success_data)
        self.assertEqual(route.call_count, 2)

    @respx.mock
    def test_retry_on_500_then_success(self):
        success_data = {"query": {"pages": {}}}
        responses = iter([httpx.Response(500), httpx.Response(200, json=success_data)])
        route = respx.get(API_URL).mock(side_effect=lambda req: next(responses))
        result = self.wiki._get("en", {"action": "query"})
        self.assertEqual(result, success_data)
        self.assertEqual(route.call_count, 2)

    @respx.mock
    def test_retry_on_timeout_then_success(self):
        success_data = {"query": {"pages": {}}}
        call_num = [0]

        def side_effect(req):
            call_num[0] += 1
            if call_num[0] == 1:
                raise httpx.TimeoutException("timeout")
            return httpx.Response(200, json=success_data)

        route = respx.get(API_URL).mock(side_effect=side_effect)
        result = self.wiki._get("en", {"action": "query"})
        self.assertEqual(result, success_data)
        self.assertEqual(route.call_count, 2)

    @respx.mock
    def test_retry_on_connection_error_then_success(self):
        success_data = {"query": {"pages": {}}}
        call_num = [0]

        def side_effect(req):
            call_num[0] += 1
            if call_num[0] == 1:
                raise httpx.ConnectError("conn error")
            return httpx.Response(200, json=success_data)

        route = respx.get(API_URL).mock(side_effect=side_effect)
        result = self.wiki._get("en", {"action": "query"})
        self.assertEqual(result, success_data)
        self.assertEqual(route.call_count, 2)

    @respx.mock
    def test_max_retries_exhausted_raises(self):
        route = respx.get(API_URL).mock(return_value=httpx.Response(429))
        with self.assertRaises(wikipediaapi.WikiRateLimitError):
            self.wiki._get("en", {"action": "query"})
        # 1 initial + 2 retries = 3 attempts
        self.assertEqual(route.call_count, 3)

    @respx.mock
    def test_max_retries_exhausted_on_500(self):
        route = respx.get(API_URL).mock(return_value=httpx.Response(500))
        with self.assertRaises(wikipediaapi.WikiHttpError) as ctx:
            self.wiki._get("en", {"action": "query"})
        self.assertEqual(ctx.exception.status_code, 500)
        self.assertEqual(route.call_count, 3)

    @respx.mock
    def test_max_retries_exhausted_on_timeout(self):
        route = respx.get(API_URL).mock(side_effect=httpx.TimeoutException("timeout"))
        with self.assertRaises(wikipediaapi.WikiHttpTimeoutError):
            self.wiki._get("en", {"action": "query"})
        self.assertEqual(route.call_count, 3)

    @respx.mock
    def test_no_retry_on_4xx(self):
        """Non-retryable 4xx errors should raise immediately without retries."""
        route = respx.get(API_URL).mock(return_value=httpx.Response(404))
        with self.assertRaises(wikipediaapi.WikiHttpError):
            self.wiki._get("en", {"action": "query"})
        self.assertEqual(route.call_count, 1)

    @respx.mock
    def test_retry_429_with_retry_after_header(self):
        success_data = {"query": {"pages": {}}}
        responses = iter(
            [
                httpx.Response(429, headers={"Retry-After": "0"}),
                httpx.Response(200, json=success_data),
            ]
        )
        respx.get(API_URL).mock(side_effect=lambda req: next(responses))
        result = self.wiki._get("en", {"action": "query"})
        self.assertEqual(result, success_data)

    @respx.mock
    def test_no_retry_on_invalid_json(self):
        """Invalid JSON on 200 should raise immediately, no retry."""
        route = respx.get(API_URL).mock(return_value=httpx.Response(200, content=b"not json"))
        with self.assertRaises(wikipediaapi.WikiInvalidJsonError):
            self.wiki._get("en", {"action": "query"})
        self.assertEqual(route.call_count, 1)

    @respx.mock
    def test_no_retry_on_request_exception(self):
        """Generic RequestError (not Timeout/ConnectError) should not retry."""
        route = respx.get(API_URL).mock(side_effect=httpx.RequestError("request error"))
        with self.assertRaises(wikipediaapi.WikiConnectionError):
            self.wiki._get("en", {"action": "query"})
        self.assertEqual(route.call_count, 1)

    def test_max_retries_zero_disables_retry(self):
        wiki = wikipediaapi.Wikipedia(user_agent, "en", max_retries=0, retry_wait=0.0)
        self.assertEqual(wiki._max_retries, 0)


class TestExceptionHierarchy(unittest.TestCase):
    """Tests for custom exception class hierarchy."""

    def test_wikipedia_exception_is_base(self):
        self.assertTrue(issubclass(wikipediaapi.WikiHttpError, wikipediaapi.WikipediaException))
        self.assertTrue(
            issubclass(wikipediaapi.WikiHttpTimeoutError, wikipediaapi.WikipediaException)
        )
        self.assertTrue(
            issubclass(wikipediaapi.WikiInvalidJsonError, wikipediaapi.WikipediaException)
        )
        self.assertTrue(
            issubclass(wikipediaapi.WikiConnectionError, wikipediaapi.WikipediaException)
        )

    def test_rate_limit_error_is_http_error(self):
        self.assertTrue(issubclass(wikipediaapi.WikiRateLimitError, wikipediaapi.WikiHttpError))

    def test_exception_messages(self):
        e = wikipediaapi.WikiHttpError(404, "http://example.com")
        self.assertIn("404", str(e))
        self.assertIn("http://example.com", str(e))

        e = wikipediaapi.WikiRateLimitError("http://example.com", retry_after=5)
        self.assertEqual(e.retry_after, 5)
        self.assertEqual(e.status_code, 429)

        e = wikipediaapi.WikiHttpTimeoutError("http://example.com")
        self.assertIn("http://example.com", str(e))

        e = wikipediaapi.WikiInvalidJsonError("http://example.com")
        self.assertIn("http://example.com", str(e))

        e = wikipediaapi.WikiConnectionError("http://example.com")
        self.assertIn("http://example.com", str(e))

    def test_exceptions_do_not_expose_httpx(self):
        """Ensure our exceptions don't inherit from httpx exceptions."""
        self.assertFalse(
            issubclass(
                wikipediaapi.WikipediaException,
                httpx.HTTPStatusError,
            )
        )


class TestDefaultRetryParams(unittest.TestCase):
    """Tests for default retry parameters in Wikipedia constructor."""

    def test_default_max_retries(self):
        wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.assertEqual(wiki._max_retries, 3)

    def test_default_retry_wait(self):
        wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.assertEqual(wiki._retry_wait, 1.0)

    def test_custom_retry_params(self):
        wiki = wikipediaapi.Wikipedia(user_agent, "en", max_retries=5, retry_wait=2.0)
        self.assertEqual(wiki._max_retries, 5)
        self.assertEqual(wiki._retry_wait, 2.0)
