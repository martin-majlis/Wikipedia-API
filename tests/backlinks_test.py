# -*- coding: utf-8 -*-
import unittest

from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi


class TestBackLinks(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._query = wikipedia_api_request

    def test_backlinks_nonexistent_count(self):
        page = self.wiki.page("Non_Existent")
        self.assertEqual(len(page.backlinks), 0)

    def test_backlinks_single_page_count(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(len(page.backlinks), 3)

    def test_backlinks_single_page_titles(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.backlinks.values()))),
            ["Title - " + str(i + 1) for i in range(3)],
        )

    def test_backlinks_multi_page_count(self):
        page = self.wiki.page("Test_2")
        self.assertEqual(len(page.backlinks), 5)

    def test_backlinks_multi_page_titles(self):
        page = self.wiki.page("Test_2")
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.backlinks.values()))),
            ["Title - " + str(i + 1) for i in range(5)],
        )
