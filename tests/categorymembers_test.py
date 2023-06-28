# -*- coding: utf-8 -*-
import unittest

from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi


class TestCategoryMembers(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._query = wikipedia_api_request

    def test_links_single_page_count(self):
        page = self.wiki.page("Category:C1")
        self.assertEqual(len(page.categorymembers), 3)

    def test_links_single_page_titles(self):
        page = self.wiki.page("Category:C1")
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.categorymembers.values()))),
            ["Title - " + str(i + 1) for i in range(3)],
        )

    def test_links_multi_page_count(self):
        page = self.wiki.page("Category:C2")
        self.assertEqual(len(page.categorymembers), 5)

    def test_links_multi_page_titles(self):
        page = self.wiki.page("Category:C2")
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.categorymembers.values()))),
            ["Title - " + str(i + 1) for i in range(5)],
        )
