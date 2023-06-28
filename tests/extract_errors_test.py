# -*- coding: utf-8 -*-
import unittest

from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi


class TestErrorsExtracts(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._query = wikipedia_api_request

    def test_title_before_fetching(self):
        page = self.wiki.page("NonExisting")
        self.assertEqual(page.title, "NonExisting")

    def test_pageid(self):
        page = self.wiki.page("NonExisting")
        self.assertEqual(page.pageid, -1)
