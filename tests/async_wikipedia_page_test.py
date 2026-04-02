import asyncio

import wikipediaapi
from tests.mock_data import async_wikipedia_api_request
from tests.mock_data import user_agent
from wikipediaapi._enums import Namespace
from wikipediaapi.async_wikipedia_page import AsyncWikipediaPage


class TestAsyncWikipediaPageInit:
    """Tests for AsyncWikipediaPage construction."""

    def setup_method(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

    def test_title(self):
        page = self.wiki.page("Python")
        assert page.title == "Python"

    def test_language(self):
        page = self.wiki.page("Python")
        assert page.language == "en"

    def test_ns_default(self):
        page = self.wiki.page("Python")
        assert page.ns == 0

    def test_variant_default_none(self):
        page = self.wiki.page("Python")
        assert page.variant is None

    def test_variant_set(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "zh", variant="zh-tw")
        page = wiki.page("Test")
        assert page.variant == "zh-tw"

    def test_page_identity_equality(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("Test_1")
        assert p1 == p2
        assert hash(p1) == hash(p2)

    def test_page_identity_inequality(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("Test_1", ns=wikipediaapi.Namespace.CATEGORY)
        assert p1 != p2

    def test_dir_includes_attributes_mapping_keys(self):
        page = self.wiki.page("Test_1")
        d = dir(page)
        for attr in ["pageid", "fullurl", "displaytitle", "canonicalurl", "editurl"]:
            assert attr in d  # always present: __getattr__ returns non-blocking coroutines

    def test_dir_includes_coroutine_properties(self):
        page = self.wiki.page("Test_1")
        d = dir(page)
        for attr in ["summary", "text", "langlinks", "links", "backlinks", "categories"]:
            assert attr in d

    def test_namespace_default(self):
        page = self.wiki.page("Python")
        assert page.namespace == 0

    def test_repr_before_fetch(self):
        page = self.wiki.page("Python")
        assert repr(page) == "Python (lang: en, variant: None, id: ??, ns: 0)"

    def test_repr_after_fetch(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        wiki._get = async_wikipedia_api_request(wiki)
        page = wiki.page("Test_1")
        assert repr(page) == "Test_1 (lang: en, variant: None, id: ??, ns: 0)"
        asyncio.run(page.summary)
        assert repr(page) == "Test 1 (lang: en, variant: None, id: 4, ns: 0)"

    def test_sections_empty_before_fetch(self):
        page = self.wiki.page("Python")
        # Check that the property exists on the class
        sections_prop = getattr(type(page), "sections", None)
        assert sections_prop is not None, "sections property should exist"

        # Verify that accessing it returns a coroutine
        # (this will create a coroutine that we don't await)
        import asyncio

        sections = page.sections
        assert asyncio.iscoroutine(sections), "sections should return a coroutine"
        # Explicitly close the coroutine to avoid warnings
        sections.close()

    def test_url_stored_in_attributes(self):
        page = AsyncWikipediaPage(
            wiki=self.wiki,
            title="Test",
            ns=Namespace.MAIN,
            language="en",
            url="https://en.wikipedia.org/wiki/Test",
        )
        assert asyncio.run(page.fullurl) == "https://en.wikipedia.org/wiki/Test"


class TestAsyncWikipediaPageFetch:
    """Tests for async fetch methods on AsyncWikipediaPage."""

    def setup_method(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        self.wiki._get = async_wikipedia_api_request(self.wiki)

    async def test_pageid_from_extracts_no_info_call(self):
        page = self.wiki.page("Test_1")
        await page.summary  # triggers extracts, which includes pageid
        assert page._called["info"] is False
        pageid = await page.pageid
        assert pageid == 4
        assert page._called["info"] is False  # pageid was cached; info still not needed

    async def test_pageid_from_langlinks_no_info_call(self):
        page = self.wiki.page("Test_1")
        await page.langlinks  # triggers langlinks, which includes pageid
        assert page._called["info"] is False
        pageid = await page.pageid
        assert pageid == 4
        assert page._called["info"] is False  # pageid was cached; info still not needed

    async def test_title_from_extracts_no_info_call(self):
        page = self.wiki.page("Test_1")
        await page.summary  # extracts also populates title and ns
        assert page._called["info"] is False
        assert page.title == "Test 1"
        assert page.ns == 0

    async def test_summary_fetches_and_returns_str(self):
        page = self.wiki.page("Test_1")
        summary = await page.summary
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert page._called["extracts"] is True

    async def test_text_fetches_and_returns_str(self):
        page = self.wiki.page("Test_1")
        text = await page.text
        assert isinstance(text, str)
        assert len(text) > 0
        assert page._called["extracts"] is True

    async def test_summary_not_refetched_on_second_call(self):
        page = self.wiki.page("Test_1")
        await page.summary
        calls_before = page._called.copy()
        await page.summary
        assert calls_before == page._called

    async def test_langlinks_returns_dict(self):
        page = self.wiki.page("Test_1")
        langlinks = await page.langlinks
        assert isinstance(langlinks, dict)
        assert page._called["langlinks"] is True

    async def test_links_returns_dict_of_async_pages(self):
        page = self.wiki.page("Test_1")
        links = await page.links
        assert isinstance(links, dict)
        assert len(links) == 3
        for p in links.values():
            assert isinstance(p, AsyncWikipediaPage)

    async def test_backlinks_returns_dict(self):
        page = self.wiki.page("Test_1")
        backlinks = await page.backlinks
        assert isinstance(backlinks, dict)
        assert page._called["backlinks"] is True

    async def test_categories_returns_dict(self):
        page = self.wiki.page("Test_1")
        categories = await page.categories
        assert isinstance(categories, dict)
        assert page._called["categories"] is True

    async def test_categorymembers_returns_dict(self):
        page = self.wiki.page("Category:C1")
        members = await page.categorymembers
        assert isinstance(members, dict)
        assert page._called["categorymembers"] is True

    async def test_undocumented_api_field(self):
        page = self.wiki.page("Test_1")
        assert page._called["info"] is False
        value = await page.api_new_experimental_field
        assert value == "test_value"
        assert page._called["info"] is True

    async def test_undocumented_api_field_cached_after_first_access(self):
        page = self.wiki.page("Test_1")
        await page.api_new_experimental_field
        assert page._called["info"] is True
        calls_before = page._called.copy()
        await page.api_new_experimental_field
        assert calls_before == page._called

    async def test_exists_true(self):
        page = self.wiki.page("Test_1")
        assert (await page.exists()) is True

    async def test_exists_false_for_nonexistent(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

        async def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get  # ty: ignore[invalid-assignment]
        page = wiki.page("NonExistent")
        assert (await page.exists()) is False

    async def test_section_by_title_found(self):
        page = self.wiki.page("Test_1")
        await page.summary
        sec = page.section_by_title("Section 1")
        assert sec is not None
        assert sec.title == "Section 1"

    async def test_section_by_title_not_found(self):
        page = self.wiki.page("Test_1")
        await page.summary
        sec = page.section_by_title("Nonexistent Section")
        assert sec is None

    async def test_sections_by_title_found(self):
        page = self.wiki.page("Test_1")
        await page.sections
        secs = page.sections_by_title("Section 1")
        assert isinstance(secs, list)
        assert len(secs) == 1
        assert secs[0].title == "Section 1"

    async def test_sections_by_title_not_found(self):
        page = self.wiki.page("Test_1")
        await page.sections
        secs = page.sections_by_title("Nonexistent Section")
        assert isinstance(secs, list)
        assert len(secs) == 0

    async def test_sections_populated_after_summary(self):
        page = self.wiki.page("Test_1")
        await page.summary
        sections = await page.sections
        assert len(sections) > 0


class TestAsyncWikipediaPageAttributesMapping:
    """Verify every key in ATTRIBUTES_MAPPING is accessible on AsyncWikipediaPage."""

    def setup_method(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        self.wiki._get = async_wikipedia_api_request(self.wiki)

    # ---- Init attributes — no fetch required ----

    def test_language_no_fetch(self):
        page = self.wiki.page("Test_1")
        assert page.language == "en"

    def test_variant_no_fetch(self):
        page = self.wiki.page("Test_1")
        assert page.variant is None

    # ---- pageid — lazy awaitable; ns / title — set at init ----

    async def test_pageid(self):
        page = self.wiki.page("Test_1")
        assert await page.pageid == 4

    def test_ns(self):
        page = self.wiki.page("Test_1")
        assert page.ns == 0

    def test_title(self):
        page = self.wiki.page("Test_1")
        assert page.title == "Test_1"

    # ---- Attributes populated by info ----

    async def test_contentmodel(self):
        page = self.wiki.page("Test_1")
        assert await page.contentmodel == "wikitext"

    async def test_pagelanguage(self):
        page = self.wiki.page("Test_1")
        assert await page.pagelanguage == "en"

    async def test_pagelanguagehtmlcode(self):
        page = self.wiki.page("Test_1")
        assert await page.pagelanguagehtmlcode == "en"

    async def test_pagelanguagedir(self):
        page = self.wiki.page("Test_1")
        assert await page.pagelanguagedir == "ltr"

    async def test_touched(self):
        page = self.wiki.page("Test_1")
        assert await page.touched == "2023-01-01T00:00:00Z"

    async def test_lastrevid(self):
        page = self.wiki.page("Test_1")
        assert await page.lastrevid == 12345

    async def test_length(self):
        page = self.wiki.page("Test_1")
        assert await page.length == 6789

    async def test_protection(self):
        page = self.wiki.page("Test_1")
        protection = await page.protection
        assert isinstance(protection, list)
        assert len(protection) == 1
        assert protection[0]["type"] == "create"

    async def test_restrictiontypes(self):
        page = self.wiki.page("Test_1")
        assert await page.restrictiontypes == ["create"]

    async def test_watchers(self):
        page = self.wiki.page("Test_1")
        assert await page.watchers == 100

    async def test_visitingwatchers(self):
        page = self.wiki.page("Test_1")
        assert await page.visitingwatchers == 50

    async def test_notificationtimestamp(self):
        page = self.wiki.page("Test_1")
        assert await page.notificationtimestamp == ""

    async def test_talkid(self):
        page = self.wiki.page("Test_1")
        assert await page.talkid == 5

    async def test_fullurl(self):
        page = self.wiki.page("Test_1")
        assert await page.fullurl == "https://en.wikipedia.org/wiki/Test_1"

    async def test_editurl(self):
        page = self.wiki.page("Test_1")
        assert await page.editurl == "https://en.wikipedia.org/w/index.php?title=Test_1&action=edit"

    async def test_canonicalurl(self):
        page = self.wiki.page("Test_1")
        assert await page.canonicalurl == "https://en.wikipedia.org/wiki/Test_1"

    async def test_readable(self):
        page = self.wiki.page("Test_1")
        assert await page.readable == ""

    async def test_preload(self):
        page = self.wiki.page("Test_1")
        assert await page.preload is None

    async def test_displaytitle(self):
        page = self.wiki.page("Test_1")
        assert await page.displaytitle == "Test 1"

    async def test_varianttitles(self):
        page = self.wiki.page("Test_1")
        assert await page.varianttitles == {}

    # ---- pageid / ns / title also populated by langlinks ----

    async def test_pageid_after_langlinks(self):
        page = self.wiki.page("Test_1")
        await page.langlinks
        assert await page.pageid == 4

    async def test_ns_after_langlinks(self):
        page = self.wiki.page("Test_1")
        await page.langlinks
        assert page.ns == 0

    async def test_title_after_langlinks(self):
        page = self.wiki.page("Test_1")
        await page.langlinks
        assert page.title == "Test 1"
