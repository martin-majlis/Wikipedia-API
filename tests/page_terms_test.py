import unittest

import wikipediaapi
from tests.mock_data import wikipedia_api_request


class TestPageTerm(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia("en")
        self.wiki._query = wikipedia_api_request

    def test_alias_good_parsing(self):
        page = self.wiki.page('Test1')
        self.assertEqual(page.alias, ["Test 1", "Test one", "Test ONE"])

    def test_description_good_parsing(self):
        page = self.wiki.page('Test1')
        self.assertEqual(page.desc, ['test'])

    def test_label_good_parsing(self):
        page = self.wiki.page('Test1')
        self.assertEqual(page.label, ['Test 1'])

    def test_label_nonexistent_page(self):
        page = self.wiki.page('Non_Existent')
        self.assertEqual(page.label, [])

    def test_alias_nonexistent_page(self):
        page = self.wiki.page('Non_Existent')
        self.assertEqual(page.alias, [])

    def test_description_nonexistent_page(self):
        page = self.wiki.page('Non_Existent')
        self.assertEqual(page.desc, [])