import unittest

from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi


class TestLinks(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._query = wikipedia_api_request(self.wiki)

    def test_links_single_page_count(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(len(page.links), 3)

    def test_links_single_page_titles(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.links.values()))),
            ["Title - " + str(i + 1) for i in range(3)],
        )

    def test_links_multi_page_count(self):
        page = self.wiki.page("Test_2")
        self.assertEqual(len(page.links), 5)

    def test_links_multi_page_titles(self):
        page = self.wiki.page("Test_2")
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.links.values()))),
            ["Title - " + str(i + 1) for i in range(5)],
        )

    def test_links_no_links_count(self):
        page = self.wiki.page("No_Links")
        self.assertEqual(len(page.links), 0)

    def test_links_from_variant(self):
        wiki = wikipediaapi.Wikipedia(user_agent, "zh", "zh-tw")
        wiki._query = wikipedia_api_request(wiki)
        page = wiki.page("Test_Zh-Tw")
        self.assertEqual(
            list(sorted(map(lambda s: (s.title, s.variant), page.links.values()))),
            [("Title - Zh-Tw - " + str(i + 1), "zh-tw") for i in range(3)],
        )
