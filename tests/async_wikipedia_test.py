import pytest

import wikipediaapi
from tests.mock_data import async_wikipedia_api_request, user_agent
from wikipediaapi.async_wikipedia_page import AsyncWikipediaPage


class TestAsyncWikipedia:
    def setup_method(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        self.wiki._get = async_wikipedia_api_request(self.wiki)

    def test_page_returns_async_page(self):
        page = self.wiki.page("Test_1")
        assert isinstance(page, AsyncWikipediaPage)

    def test_article_returns_async_page(self):
        page = self.wiki.article("Test_1")
        assert isinstance(page, AsyncWikipediaPage)

    def test_page_title(self):
        page = self.wiki.page("Test_1")
        assert page.title == "Test_1"

    def test_page_language(self):
        page = self.wiki.page("Test_1")
        assert page.language == "en"

    def test_page_with_variant(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "zh", variant="zh-tw")
        wiki._get = async_wikipedia_api_request(wiki)
        page = wiki.page("Test_Zh-Tw")
        assert page.variant == "zh-tw"

    @pytest.mark.asyncio
    async def test_extracts_existing_page(self):
        page = self.wiki.page("Test_1")
        summary = await self.wiki.extracts(page)
        assert isinstance(summary, str)
        assert len(summary) > 0

    @pytest.mark.asyncio
    async def test_extracts_nonexistent_page(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

        async def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get  # ty: ignore[invalid-assignment]
        page = wiki.page("NonExistent")
        result = await wiki.extracts(page)
        assert result == ""

    @pytest.mark.asyncio
    async def test_info_existing_page(self):
        page = self.wiki.page("Test_1")
        result = await self.wiki.info(page)
        assert result == page

    @pytest.mark.asyncio
    async def test_langlinks_existing_page(self):
        page = self.wiki.page("Test_1")
        langlinks = await self.wiki.langlinks(page)
        assert isinstance(langlinks, dict)

    @pytest.mark.asyncio
    async def test_links_existing_page(self):
        page = self.wiki.page("Test_1")
        links = await self.wiki.links(page)
        assert isinstance(links, dict)
        assert len(links) == 3

    @pytest.mark.asyncio
    async def test_backlinks_existing_page(self):
        page = self.wiki.page("Test_1")
        backlinks = await self.wiki.backlinks(page)
        assert isinstance(backlinks, dict)

    @pytest.mark.asyncio
    async def test_categories_existing_page(self):
        page = self.wiki.page("Test_1")
        categories = await self.wiki.categories(page)
        assert isinstance(categories, dict)

    @pytest.mark.asyncio
    async def test_categorymembers_existing_page(self):
        page = self.wiki.page("Category:C1")
        members = await self.wiki.categorymembers(page)
        assert isinstance(members, dict)

    @pytest.mark.asyncio
    async def test_nonexistent_page_links_empty(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

        async def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get  # ty: ignore[invalid-assignment]
        page = wiki.page("NonExistent")
        result = await wiki.links(page)
        assert result == {}

    @pytest.mark.asyncio
    async def test_nonexistent_page_backlinks_empty(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

        async def mock_get(language, params):
            return {"query": {"backlinks": []}}

        wiki._get = mock_get  # ty: ignore[invalid-assignment]
        page = wiki.page("NonExistent")
        result = await wiki.backlinks(page)
        assert result == {}

    @pytest.mark.asyncio
    async def test_nonexistent_page_categories_empty(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

        async def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get  # ty: ignore[invalid-assignment]
        page = wiki.page("NonExistent")
        result = await wiki.categories(page)
        assert result == {}

    @pytest.mark.asyncio
    async def test_nonexistent_page_categorymembers_empty(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

        async def mock_get(language, params):
            return {"query": {"categorymembers": []}}

        wiki._get = mock_get  # ty: ignore[invalid-assignment]
        page = wiki.page("NonExistent")
        result = await wiki.categorymembers(page)
        assert result == {}
