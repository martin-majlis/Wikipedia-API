# -*- coding: utf-8 -*-
from collections import defaultdict
import unittest
import wikipediaapi

from mock_data import wikipedia_api_request


class TestCategoryMembers(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia("en")
        self.wiki._query = wikipedia_api_request

    def test_links_single_page_count(self):
        page = self.wiki.page('Category:C1')
        self.assertEqual(len(page.categorymembers), 3)

    def test_links_single_page_titles(self):
        page = self.wiki.page('Category:C1')
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.categorymembers.values()))),
            ['Title - ' + str(i + 1) for i in range(3)]
        )

    def test_links_multi_page_count(self):
        page = self.wiki.page('Category:C2')
        self.assertEqual(len(page.categorymembers), 5)

    def test_links_multi_page_titles(self):
        page = self.wiki.page('Category:C2')
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.categorymembers.values()))),
            ['Title - ' + str(i + 1) for i in range(5)]
        )
