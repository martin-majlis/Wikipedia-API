# -*- coding: utf-8 -*-
from collections import defaultdict
import unittest
from wikipedia import wikipedia

from mock_data import wikipedia_api_request


class TestErrorsExtracts(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipedia.Wikipedia("en")
        self.wiki._query = wikipedia_api_request

    def test_title_before_fetching(self):
        page = self.wiki.page('NonExisting')
        self.assertEqual(page.title, 'NonExisting')

    def test_pageid(self):
        page = self.wiki.page('NonExisting')
        self.assertEqual(page.pageid, -1)