import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from tests.mock_data import user_agent
import wikipediaapi


class TestQueryHttpErrors(unittest.TestCase):
    """Tests for _query HTTP error handling."""

    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en", max_retries=0, retry_wait=0.0)
        self.page = self.wiki.page("Test")

    def _mock_response(self, status_code=200, json_data=None, headers=None):
        resp = MagicMock()
        resp.status_code = status_code
        resp.headers = headers or {}
        if json_data is not None:
            resp.json.return_value = json_data
        else:
            resp.json.side_effect = ValueError("No JSON")
        return resp

    @patch("requests.Session.get")
    def test_http_404_raises_http_error(self, mock_get):
        mock_get.return_value = self._mock_response(status_code=404)
        with self.assertRaises(wikipediaapi.WikiHttpError) as ctx:
            self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIsInstance(ctx.exception, wikipediaapi.WikipediaException)

    @patch("requests.Session.get")
    def test_http_403_raises_http_error(self, mock_get):
        mock_get.return_value = self._mock_response(status_code=403)
        with self.assertRaises(wikipediaapi.WikiHttpError) as ctx:
            self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(ctx.exception.status_code, 403)

    @patch("requests.Session.get")
    def test_http_429_raises_rate_limit_error(self, mock_get):
        mock_get.return_value = self._mock_response(status_code=429, headers={"Retry-After": "5"})
        with self.assertRaises(wikipediaapi.WikiRateLimitError) as ctx:
            self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(ctx.exception.status_code, 429)
        self.assertEqual(ctx.exception.retry_after, 5)
        self.assertIsInstance(ctx.exception, wikipediaapi.WikiHttpError)

    @patch("requests.Session.get")
    def test_http_429_without_retry_after(self, mock_get):
        mock_get.return_value = self._mock_response(status_code=429)
        with self.assertRaises(wikipediaapi.WikiRateLimitError) as ctx:
            self.wiki._query(self.page, {"action": "query"})
        self.assertIsNone(ctx.exception.retry_after)

    @patch("requests.Session.get")
    def test_http_500_raises_http_error(self, mock_get):
        mock_get.return_value = self._mock_response(status_code=500)
        with self.assertRaises(wikipediaapi.WikiHttpError) as ctx:
            self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(ctx.exception.status_code, 500)

    @patch("requests.Session.get")
    def test_http_503_raises_http_error(self, mock_get):
        mock_get.return_value = self._mock_response(status_code=503)
        with self.assertRaises(wikipediaapi.WikiHttpError) as ctx:
            self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(ctx.exception.status_code, 503)

    @patch("requests.Session.get")
    def test_invalid_json_raises_invalid_json_error(self, mock_get):
        mock_get.return_value = self._mock_response(status_code=200)
        with self.assertRaises(wikipediaapi.WikiInvalidJsonError):
            self.wiki._query(self.page, {"action": "query"})

    @patch("requests.Session.get")
    def test_timeout_raises_http_timeout_error(self, mock_get):
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()
        with self.assertRaises(wikipediaapi.WikiHttpTimeoutError):
            self.wiki._query(self.page, {"action": "query"})

    @patch("requests.Session.get")
    def test_connection_error_raises_connection_error(self, mock_get):
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError()
        with self.assertRaises(wikipediaapi.WikiConnectionError):
            self.wiki._query(self.page, {"action": "query"})

    @patch("requests.Session.get")
    def test_request_exception_raises_connection_error(self, mock_get):
        import requests

        mock_get.side_effect = requests.exceptions.RequestException()
        with self.assertRaises(wikipediaapi.WikiConnectionError):
            self.wiki._query(self.page, {"action": "query"})

    @patch("requests.Session.get")
    def test_http_200_valid_json_returns_data(self, mock_get):
        expected = {"query": {"pages": {}}}
        mock_get.return_value = self._mock_response(status_code=200, json_data=expected)
        result = self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(result, expected)


class TestQueryRetryLogic(unittest.TestCase):
    """Tests for _query retry behavior."""

    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en", max_retries=2, retry_wait=0.0)
        self.page = self.wiki.page("Test")

    def _mock_response(self, status_code=200, json_data=None, headers=None):
        resp = MagicMock()
        resp.status_code = status_code
        resp.headers = headers or {}
        if json_data is not None:
            resp.json.return_value = json_data
        else:
            resp.json.side_effect = ValueError("No JSON")
        return resp

    @patch("requests.Session.get")
    def test_retry_on_429_then_success(self, mock_get):
        success_data = {"query": {"pages": {}}}
        mock_get.side_effect = [
            self._mock_response(status_code=429),
            self._mock_response(status_code=200, json_data=success_data),
        ]
        result = self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(result, success_data)
        self.assertEqual(mock_get.call_count, 2)

    @patch("requests.Session.get")
    def test_retry_on_500_then_success(self, mock_get):
        success_data = {"query": {"pages": {}}}
        mock_get.side_effect = [
            self._mock_response(status_code=500),
            self._mock_response(status_code=200, json_data=success_data),
        ]
        result = self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(result, success_data)
        self.assertEqual(mock_get.call_count, 2)

    @patch("requests.Session.get")
    def test_retry_on_timeout_then_success(self, mock_get):
        import requests

        success_data = {"query": {"pages": {}}}
        mock_get.side_effect = [
            requests.exceptions.Timeout(),
            self._mock_response(status_code=200, json_data=success_data),
        ]
        result = self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(result, success_data)
        self.assertEqual(mock_get.call_count, 2)

    @patch("requests.Session.get")
    def test_retry_on_connection_error_then_success(self, mock_get):
        import requests

        success_data = {"query": {"pages": {}}}
        mock_get.side_effect = [
            requests.exceptions.ConnectionError(),
            self._mock_response(status_code=200, json_data=success_data),
        ]
        result = self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(result, success_data)
        self.assertEqual(mock_get.call_count, 2)

    @patch("requests.Session.get")
    def test_max_retries_exhausted_raises(self, mock_get):
        mock_get.return_value = self._mock_response(status_code=429)
        with self.assertRaises(wikipediaapi.WikiRateLimitError):
            self.wiki._query(self.page, {"action": "query"})
        # 1 initial + 2 retries = 3 attempts
        self.assertEqual(mock_get.call_count, 3)

    @patch("requests.Session.get")
    def test_max_retries_exhausted_on_500(self, mock_get):
        mock_get.return_value = self._mock_response(status_code=500)
        with self.assertRaises(wikipediaapi.WikiHttpError) as ctx:
            self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(ctx.exception.status_code, 500)
        self.assertEqual(mock_get.call_count, 3)

    @patch("requests.Session.get")
    def test_max_retries_exhausted_on_timeout(self, mock_get):
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()
        with self.assertRaises(wikipediaapi.WikiHttpTimeoutError):
            self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(mock_get.call_count, 3)

    @patch("requests.Session.get")
    def test_no_retry_on_4xx(self, mock_get):
        """Non-retryable 4xx errors should raise immediately without retries."""
        mock_get.return_value = self._mock_response(status_code=404)
        with self.assertRaises(wikipediaapi.WikiHttpError):
            self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(mock_get.call_count, 1)

    @patch("requests.Session.get")
    def test_retry_429_with_retry_after_header(self, mock_get):
        success_data = {"query": {"pages": {}}}
        mock_get.side_effect = [
            self._mock_response(status_code=429, headers={"Retry-After": "1"}),
            self._mock_response(status_code=200, json_data=success_data),
        ]
        result = self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(result, success_data)

    @patch("requests.Session.get")
    def test_no_retry_on_invalid_json(self, mock_get):
        """Invalid JSON on 200 should raise immediately, no retry."""
        mock_get.return_value = self._mock_response(status_code=200)
        with self.assertRaises(wikipediaapi.WikiInvalidJsonError):
            self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(mock_get.call_count, 1)

    @patch("requests.Session.get")
    def test_no_retry_on_request_exception(self, mock_get):
        """Generic RequestException (not Timeout/ConnectionError) should not retry."""
        import requests

        mock_get.side_effect = requests.exceptions.RequestException()
        with self.assertRaises(wikipediaapi.WikiConnectionError):
            self.wiki._query(self.page, {"action": "query"})
        self.assertEqual(mock_get.call_count, 1)

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

    def test_exceptions_do_not_expose_requests(self):
        """Ensure our exceptions don't inherit from requests exceptions."""
        import requests

        self.assertFalse(
            issubclass(
                wikipediaapi.WikipediaException,
                requests.exceptions.RequestException,
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
