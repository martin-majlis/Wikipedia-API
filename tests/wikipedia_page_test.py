# -*- coding: utf-8 -*-
from collections import defaultdict
import unittest

from mock_data import wikipedia_api_request
import wikipediaapi


class TestWikipediaPage(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia("en")
        self.wiki._query = wikipedia_api_request

    def test_repr_before_fetching(self):
        page = self.wiki.page('Test_1')
        self.assertEqual(repr(page), 'Test_1 (id: ??, ns: 0)')

    def test_repr_after_fetching(self):
        page = self.wiki.page('Test_1')
        self.assertEqual(repr(page), 'Test_1 (id: ??, ns: 0)')
        self.assertEqual(page.pageid, 4)
        self.assertEqual(repr(page), 'Test 1 (id: 4, ns: 0)')
