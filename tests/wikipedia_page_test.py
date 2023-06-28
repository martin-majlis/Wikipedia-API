# -*- coding: utf-8 -*-
import unittest

from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi


class TestWikipediaPage(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._query = wikipedia_api_request

    def test_repr_before_fetching(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(repr(page), "Test_1 (id: ??, ns: 0)")

    def test_repr_after_fetching(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(repr(page), "Test_1 (id: ??, ns: 0)")
        self.assertEqual(page.pageid, 4)
        self.assertEqual(repr(page), "Test 1 (id: 4, ns: 0)")

    def test_extract(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.pageid, 4)
        self.assertEqual(page.title, "Test 1")
        self.assertEqual(page.ns, 0)
        self.assertEqual(page.contentmodel, "wikitext")
        self.assertEqual(page.pagelanguage, "en")
        self.assertEqual(page.pagelanguagedir, "ltr")
        self.assertEqual(page.fullurl, "https://en.wikipedia.org/wiki/Test_1")
        self.assertEqual(
            page.editurl,
            "https://en.wikipedia.org/w/index.php?title=Test_1&action=edit",
        )
        self.assertEqual(page.canonicalurl, "https://en.wikipedia.org/wiki/Test_1")
        self.assertEqual(page.displaytitle, "Test 1")

    def test_unknown_property(self):
        page = self.wiki.page("Test_1")
        with self.assertRaises(AttributeError):
            page.unknown_property

    def test_nonexisting(self):
        page = self.wiki.page("NonExisting")
        self.assertFalse(page.exists())

    def test_existing(self):
        page = self.wiki.page("Test_1")
        self.assertTrue(page.exists())

    def test_article_method(self):
        p = self.wiki.page("Test_1")
        a = self.wiki.article("Test_1")
        self.assertEqual(p.pageid, a.pageid)

    def test_article_title_unquote(self):
        # https://github.com/goldsmith/Wikipedia/issues/190
        w = wikipediaapi.Wikipedia(user_agent, "hi")
        w._query = wikipedia_api_request
        p_encoded = w.article(
            "%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8",
            unquote=True,
        )
        p_decoded = w.article("पाइथन")
        self.assertEqual(p_encoded.pageid, p_decoded.pageid)

    def test_page_title_unquote(self):
        # https://github.com/goldsmith/Wikipedia/issues/190
        w = wikipediaapi.Wikipedia(user_agent, "hi")
        w._query = wikipedia_api_request
        p_encoded = w.page(
            "%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8",
            unquote=True,
        )
        p_decoded = w.page("पाइथन")
        self.assertEqual(p_encoded.pageid, p_decoded.pageid)

    def test_page_with_int_namespace(self):
        page = self.wiki.page("NonExisting", ns=110)
        self.assertFalse(page.exists())
        self.assertEqual(110, page.namespace)
