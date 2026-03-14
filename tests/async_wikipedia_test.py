import unittest

from tests.mock_data import async_wikipedia_api_request
from tests.mock_data import user_agent
import wikipediaapi
from wikipediaapi.async_wikipedia_page import AsyncWikipediaPage


class TestAsyncWikipedia(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        self.wiki._get = async_wikipedia_api_request(self.wiki)

    def test_page_returns_async_page(self):
        page = self.wiki.page("Test_1")
        self.assertIsInstance(page, AsyncWikipediaPage)

    def test_article_returns_async_page(self):
        page = self.wiki.article("Test_1")
        self.assertIsInstance(page, AsyncWikipediaPage)

    def test_page_title(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.title, "Test_1")

    def test_page_language(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.language, "en")

    def test_page_with_variant(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "zh", variant="zh-tw")
        wiki._get = async_wikipedia_api_request(wiki)
        page = wiki.page("Test_Zh-Tw")
        self.assertEqual(page.variant, "zh-tw")

    async def test_extracts_existing_page(self):
        page = self.wiki.page("Test_1")
        summary = await self.wiki.extracts(page)
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)

    async def test_extracts_nonexistent_page(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

        async def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get
        page = wiki.page("NonExistent")
        result = await wiki.extracts(page)
        self.assertEqual(result, "")

    async def test_info_existing_page(self):
        page = self.wiki.page("Test_1")
        result = await self.wiki.info(page)
        self.assertEqual(result, page)

    async def test_langlinks_existing_page(self):
        page = self.wiki.page("Test_1")
        langlinks = await self.wiki.langlinks(page)
        self.assertIsInstance(langlinks, dict)

    async def test_links_existing_page(self):
        page = self.wiki.page("Test_1")
        links = await self.wiki.links(page)
        self.assertIsInstance(links, dict)
        self.assertEqual(len(links), 3)

    async def test_backlinks_existing_page(self):
        page = self.wiki.page("Test_1")
        backlinks = await self.wiki.backlinks(page)
        self.assertIsInstance(backlinks, dict)

    async def test_categories_existing_page(self):
        page = self.wiki.page("Test_1")
        categories = await self.wiki.categories(page)
        self.assertIsInstance(categories, dict)

    async def test_categorymembers_existing_page(self):
        page = self.wiki.page("Category:C1")
        members = await self.wiki.categorymembers(page)
        self.assertIsInstance(members, dict)

    async def test_nonexistent_page_links_empty(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

        async def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get
        page = wiki.page("NonExistent")
        result = await wiki.links(page)
        self.assertEqual(result, {})

    async def test_nonexistent_page_backlinks_empty(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

        async def mock_get(language, params):
            return {"query": {"backlinks": []}}

        wiki._get = mock_get
        page = wiki.page("NonExistent")
        result = await wiki.backlinks(page)
        self.assertEqual(result, {})

    async def test_nonexistent_page_categories_empty(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

        async def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get
        page = wiki.page("NonExistent")
        result = await wiki.categories(page)
        self.assertEqual(result, {})

    async def test_nonexistent_page_categorymembers_empty(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

        async def mock_get(language, params):
            return {"query": {"categorymembers": []}}

        wiki._get = mock_get
        page = wiki.page("NonExistent")
        result = await wiki.categorymembers(page)
        self.assertEqual(result, {})
