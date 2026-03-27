import unittest

from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi


class TestErrorsExtracts(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_title_before_fetching(self):
        page = self.wiki.page("NonExisting")
        self.assertEqual(page.title, "NonExisting")

    def test_pageid(self):
        page = self.wiki.page("NonExisting")
        self.assertLess(page.pageid, 0)
