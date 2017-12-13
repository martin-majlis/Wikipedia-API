# -*- coding: utf-8 -*-
from collections import defaultdict
import unittest
from wikipedia import wikipedia

from mock_data import wikipedia_api_request


class TestLinks(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipedia.Wikipedia("en")
        self.wiki._query = wikipedia_api_request

    def test_links_single_page_count(self):
        page = self.wiki.article('Test_1')
        self.assertEqual(len(page.links), 3)

    def test_links_single_page_titles(self):
        page = self.wiki.article('Test_1')
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.links.values()))),
            ['Title - ' + str(i + 1) for i in range(3)]
        )

    def test_links_multi_page_count(self):
        page = self.wiki.article('Test_2')
        self.assertEqual(len(page.links), 5)

    def test_links_multi_page_titles(self):
        page = self.wiki.article('Test_2')
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.links.values()))),
            ['Title - ' + str(i + 1) for i in range(5)]
        )
