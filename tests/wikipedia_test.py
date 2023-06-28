# -*- coding: utf-8 -*-
import unittest

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
                    + "Current user_agent: 'en' is not sufficient."
                )
            ),
        )

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
