# -*- coding: utf-8 -*-
from collections import defaultdict
import unittest
import wikipediaapi

from mock_data import wikipedia_api_request


class TestCategories(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia("en")
        self.wiki._query = wikipedia_api_request

    def test_categories_count(self):
        page = self.wiki.page('Test_1')
        self.assertEqual(len(page.categories), 3)

    def test_categories_titles(self):
        page = self.wiki.page('Test_1')
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.categories.values()))),
            ['Category:C' + str(i + 1) for i in range(3)]
        )

    def test_categories_nss(self):
        page = self.wiki.page('Test_1')
        self.assertEqual(
            list(sorted(map(lambda s: s.ns, page.categories.values()))),
            [14] * 3
        )
