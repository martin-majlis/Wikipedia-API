# -*- coding: utf-8 -*-
import unittest

from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi


class TestLangLinks(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._query = wikipedia_api_request

    def test_langlinks_count(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(len(page.langlinks), 3)

    def test_langlinks_titles(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.langlinks.values()))),
            ["Test 1 - " + str(i + 1) for i in range(3)],
        )

    def test_langlinks_lang_values(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(
            list(sorted(map(lambda s: s.language, page.langlinks.values()))),
            ["l" + str(i + 1) for i in range(3)],
        )

    def test_langlinks_lang_keys(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(
            list(sorted(page.langlinks.keys())), ["l" + str(i + 1) for i in range(3)]
        )

    def test_langlinks_urls(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(
            list(sorted(map(lambda s: s.fullurl, page.langlinks.values()))),
            [
                (
                    "https://l"
                    + str(i + 1)
                    + ".wikipedia.org/wiki/Test_1_-_"
                    + str(i + 1)
                )
                for i in range(3)
            ],
        )

    def test_jump_between_languages(self):
        page = self.wiki.page("Test_1")
        langlinks = page.langlinks
        p1 = langlinks["l1"]
        self.assertEqual(p1.language, "l1")
        self.assertEqual(p1.pageid, 10)

    def test_langlinks_no_langlink_count(self):
        page = self.wiki.page("No_LangLinks")
        self.assertEqual(len(page.langlinks), 0)
