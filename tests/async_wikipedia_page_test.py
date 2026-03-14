import unittest

from tests.mock_data import async_wikipedia_api_request
from tests.mock_data import user_agent
import wikipediaapi
from wikipediaapi.async_wikipedia_page import AsyncWikipediaPage
from wikipediaapi.namespace import Namespace


class TestAsyncWikipediaPageInit(unittest.TestCase):
    """Tests for AsyncWikipediaPage construction."""

    def setUp(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

    def test_title(self):
        page = self.wiki.page("Python")
        self.assertEqual(page.title, "Python")

    def test_language(self):
        page = self.wiki.page("Python")
        self.assertEqual(page.language, "en")

    def test_ns_default(self):
        page = self.wiki.page("Python")
        self.assertEqual(page.ns, 0)

    def test_variant_default_none(self):
        page = self.wiki.page("Python")
        self.assertIsNone(page.variant)

    def test_variant_set(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "zh", variant="zh-tw")
        page = wiki.page("Test")
        self.assertEqual(page.variant, "zh-tw")

    def test_repr(self):
        page = self.wiki.page("Python")
        r = repr(page)
        self.assertIn("Python", r)
        self.assertIn("en", r)

    def test_exists_before_fetch_returns_false(self):
        page = self.wiki.page("Python")
        self.assertFalse(page.exists())

    def test_sections_empty_before_fetch(self):
        page = self.wiki.page("Python")
        self.assertEqual(page.sections, [])

    def test_url_stored_in_attributes(self):
        page = AsyncWikipediaPage(
            wiki=self.wiki,
            title="Test",
            ns=Namespace.MAIN,
            language="en",
            url="https://en.wikipedia.org/wiki/Test",
        )
        self.assertEqual(page.fullurl, "https://en.wikipedia.org/wiki/Test")


class TestAsyncWikipediaPageFetch(unittest.IsolatedAsyncioTestCase):
    """Tests for async fetch methods on AsyncWikipediaPage."""

    def setUp(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        self.wiki._get = async_wikipedia_api_request(self.wiki)

    async def test_summary_fetches_and_returns_str(self):
        page = self.wiki.page("Test_1")
        summary = await page.summary()
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)
        self.assertTrue(page._called["extracts"])

    async def test_summary_not_refetched_on_second_call(self):
        page = self.wiki.page("Test_1")
        await page.summary()
        calls_before = page._called.copy()
        await page.summary()
        self.assertEqual(calls_before, page._called)

    async def test_langlinks_returns_dict(self):
        page = self.wiki.page("Test_1")
        langlinks = await page.langlinks()
        self.assertIsInstance(langlinks, dict)
        self.assertTrue(page._called["langlinks"])

    async def test_links_returns_dict_of_async_pages(self):
        page = self.wiki.page("Test_1")
        links = await page.links()
        self.assertIsInstance(links, dict)
        self.assertEqual(len(links), 3)
        for p in links.values():
            self.assertIsInstance(p, AsyncWikipediaPage)

    async def test_backlinks_returns_dict(self):
        page = self.wiki.page("Test_1")
        backlinks = await page.backlinks()
        self.assertIsInstance(backlinks, dict)
        self.assertTrue(page._called["backlinks"])

    async def test_categories_returns_dict(self):
        page = self.wiki.page("Test_1")
        categories = await page.categories()
        self.assertIsInstance(categories, dict)
        self.assertTrue(page._called["categories"])

    async def test_categorymembers_returns_dict(self):
        page = self.wiki.page("Category:C1")
        members = await page.categorymembers()
        self.assertIsInstance(members, dict)
        self.assertTrue(page._called["categorymembers"])

    async def test_exists_true_after_fetch(self):
        page = self.wiki.page("Test_1")
        await page.summary()
        self.assertTrue(page.exists())

    async def test_exists_false_for_nonexistent(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

        async def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get
        page = wiki.page("NonExistent")
        await page.summary()
        self.assertFalse(page.exists())

    async def test_section_by_title_found(self):
        page = self.wiki.page("Test_1")
        await page.summary()
        sec = page.section_by_title("Section 1")
        self.assertIsNotNone(sec)
        self.assertEqual(sec.title, "Section 1")

    async def test_section_by_title_not_found(self):
        page = self.wiki.page("Test_1")
        await page.summary()
        sec = page.section_by_title("Nonexistent Section")
        self.assertIsNone(sec)

    async def test_sections_populated_after_summary(self):
        page = self.wiki.page("Test_1")
        await page.summary()
        self.assertGreater(len(page.sections), 0)
