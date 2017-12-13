# -*- coding: utf-8 -*-
from collections import defaultdict
import unittest
import wikipediaapi

from mock_data import wikipedia_api_request


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

    def test_unknown_property(self):
        page = self.wiki.page('Test_1')
        with self.assertRaises(AttributeError):
            page.unknown_property

    def test_nonexisting(self):
        page = self.wiki.page('NonExisting')
        self.assertFalse(page.exists())

    def test_existing(self):
        page = self.wiki.page('Test_1')
        self.assertTrue(page.exists())

    def test_article_method(self):
        p = self.wiki.page('Test_1')
        a = self.wiki.article('Test_1')
        self.assertEqual(p.pageid, a.pageid)
