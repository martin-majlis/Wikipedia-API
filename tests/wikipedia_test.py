import unittest

import requests
import wikipediaapi


class TestWikipedia(unittest.TestCase):
    def test_missing_user_agent_should_fail(self):
        with self.assertRaises(AssertionError) as e:
            wikipediaapi.Wikipedia("en")
        self.assertEqual(
            str(e.exception),
            str(
                AssertionError(
                    "Please, be nice to Wikipedia and specify user agent - "
                    + "https://meta.wikimedia.org/wiki/User-Agent_policy. "
                    + "Current user_agent: 'en' is not sufficient. "
                    + "Use Wikipedia(user_agent='your-user-agent', language='en')"
                )
            ),
        )

    def test_swapped_parameters_in_constructor(self):
        with self.assertRaises(AssertionError) as e:
            wikipediaapi.Wikipedia("en", "my-user-agent")
        self.assertEqual(
            str(e.exception),
            str(
                AssertionError(
                    "Please, be nice to Wikipedia and specify user agent - "
                    + "https://meta.wikimedia.org/wiki/User-Agent_policy. "
                    + "Current user_agent: 'en' is not sufficient. "
                    + "Use Wikipedia(user_agent='your-user-agent', language='en')"
                )
            ),
        )

    def test_empty_parameters_in_constructor(self):
        with self.assertRaises(AssertionError) as e:
            wikipediaapi.Wikipedia("", "")
        self.assertEqual(
            str(e.exception),
            str(
                AssertionError(
                    "Please, be nice to Wikipedia and specify user agent - "
                    + "https://meta.wikimedia.org/wiki/User-Agent_policy. "
                    + "Current user_agent: '' is not sufficient. "
                    + "Use Wikipedia(user_agent='your-user-agent', language='your-language')"
                )
            ),
        )

    def test_empty_language_in_constructor(self):
        with self.assertRaises(AssertionError) as e:
            wikipediaapi.Wikipedia("test-user-agent", "")
        self.assertEqual(
            str(e.exception),
            str(
                AssertionError(
                    "Specify language. Current language: '' is not sufficient. "
                    + "Use Wikipedia(user_agent='test-user-agent', language='your-language')"
                )
            ),
        )

    def test_long_language_and_user_agent(self):
        wiki = wikipediaapi.Wikipedia(
            user_agent="param-user-agent", language="very-long-language"
        )
        self.assertIsNotNone(wiki)
        self.assertEqual(wiki.language, "very-long-language")
        self.assertIsNone(wiki.variant)

    def test_user_agent_is_used(self):
        wiki = wikipediaapi.Wikipedia(
            user_agent="param-user-agent",
        )
        self.assertIsNotNone(wiki)
        user_agent = wiki._session.headers.get("User-Agent")
        self.assertEqual(
            user_agent,
            "param-user-agent (" + wikipediaapi.USER_AGENT + ")",
        )
        self.assertEqual(wiki.language, "en")

    def test_user_agent_in_headers_is_fine(self):
        wiki = wikipediaapi.Wikipedia(
            "en",
            headers={"User-Agent": "header-user-agent"},
        )
        self.assertIsNotNone(wiki)
        user_agent = wiki._session.headers.get("User-Agent")
        self.assertEqual(
            user_agent,
            "header-user-agent (" + wikipediaapi.USER_AGENT + ")",
        )

    def test_user_agent_in_headers_win(self):
        wiki = wikipediaapi.Wikipedia(
            user_agent="param-user-agent",
            headers={"User-Agent": "header-user-agent"},
        )
        self.assertIsNotNone(wiki)
        user_agent = wiki._session.headers.get("User-Agent")
        self.assertEqual(
            user_agent,
            "header-user-agent (" + wikipediaapi.USER_AGENT + ")",
        )

    def test_injecting_session(self):
        session = requests.Session()
        wiki = wikipediaapi.Wikipedia(session=session)
        self.assertEqual(wiki._session, session)
