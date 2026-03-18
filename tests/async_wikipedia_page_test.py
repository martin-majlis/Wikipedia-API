import asyncio
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

    def test_dir_includes_attributes_mapping_keys(self):
        page = self.wiki.page("Test_1")
        d = dir(page)
        for attr in ["pageid", "fullurl", "displaytitle", "canonicalurl", "editurl"]:
            self.assertIn(attr, d)  # always present: __getattr__ returns non-blocking coroutines

    def test_dir_includes_coroutine_properties(self):
        page = self.wiki.page("Test_1")
        d = dir(page)
        for attr in ["summary", "text", "langlinks", "links", "backlinks", "categories"]:
            self.assertIn(attr, d)

    def test_namespace_default(self):
        page = self.wiki.page("Python")
        self.assertEqual(page.namespace, 0)

    def test_repr_before_fetch(self):
        page = self.wiki.page("Python")
        self.assertEqual(repr(page), "Python (lang: en, variant: None, id: ??, ns: 0)")

    def test_repr_after_fetch(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        wiki._get = async_wikipedia_api_request(wiki)
        page = wiki.page("Test_1")
        self.assertEqual(repr(page), "Test_1 (lang: en, variant: None, id: ??, ns: 0)")
        asyncio.run(page.summary)
        self.assertEqual(repr(page), "Test 1 (lang: en, variant: None, id: 4, ns: 0)")

    def test_sections_empty_before_fetch(self):
        page = self.wiki.page("Python")
        sections = page.sections
        # sections should be a coroutine (awaitable) now
        import asyncio

        self.assertTrue(asyncio.iscoroutine(sections))

    def test_url_stored_in_attributes(self):
        page = AsyncWikipediaPage(
            wiki=self.wiki,
            title="Test",
            ns=Namespace.MAIN,
            language="en",
            url="https://en.wikipedia.org/wiki/Test",
        )
        self.assertEqual(asyncio.run(page.fullurl), "https://en.wikipedia.org/wiki/Test")


class TestAsyncWikipediaPageFetch(unittest.IsolatedAsyncioTestCase):
    """Tests for async fetch methods on AsyncWikipediaPage."""

    def setUp(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        self.wiki._get = async_wikipedia_api_request(self.wiki)

    async def test_pageid_from_extracts_no_info_call(self):
        page = self.wiki.page("Test_1")
        await page.summary  # triggers extracts, which includes pageid
        self.assertFalse(page._called["info"])
        pageid = await page.pageid
        self.assertEqual(pageid, 4)
        self.assertFalse(page._called["info"])  # pageid was cached; info still not needed

    async def test_pageid_from_langlinks_no_info_call(self):
        page = self.wiki.page("Test_1")
        await page.langlinks  # triggers langlinks, which includes pageid
        self.assertFalse(page._called["info"])
        pageid = await page.pageid
        self.assertEqual(pageid, 4)
        self.assertFalse(page._called["info"])  # pageid was cached; info still not needed

    async def test_title_from_extracts_no_info_call(self):
        page = self.wiki.page("Test_1")
        await page.summary  # extracts also populates title and ns
        self.assertFalse(page._called["info"])
        self.assertEqual(page.title, "Test 1")
        self.assertEqual(page.ns, 0)

    async def test_summary_fetches_and_returns_str(self):
        page = self.wiki.page("Test_1")
        summary = await page.summary
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)
        self.assertTrue(page._called["extracts"])

    async def test_text_fetches_and_returns_str(self):
        page = self.wiki.page("Test_1")
        text = await page.text
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)
        self.assertTrue(page._called["extracts"])

    async def test_summary_not_refetched_on_second_call(self):
        page = self.wiki.page("Test_1")
        await page.summary
        calls_before = page._called.copy()
        await page.summary
        self.assertEqual(calls_before, page._called)

    async def test_langlinks_returns_dict(self):
        page = self.wiki.page("Test_1")
        langlinks = await page.langlinks
        self.assertIsInstance(langlinks, dict)
        self.assertTrue(page._called["langlinks"])

    async def test_links_returns_dict_of_async_pages(self):
        page = self.wiki.page("Test_1")
        links = await page.links
        self.assertIsInstance(links, dict)
        self.assertEqual(len(links), 3)
        for p in links.values():
            self.assertIsInstance(p, AsyncWikipediaPage)

    async def test_backlinks_returns_dict(self):
        page = self.wiki.page("Test_1")
        backlinks = await page.backlinks
        self.assertIsInstance(backlinks, dict)
        self.assertTrue(page._called["backlinks"])

    async def test_categories_returns_dict(self):
        page = self.wiki.page("Test_1")
        categories = await page.categories
        self.assertIsInstance(categories, dict)
        self.assertTrue(page._called["categories"])

    async def test_categorymembers_returns_dict(self):
        page = self.wiki.page("Category:C1")
        members = await page.categorymembers
        self.assertIsInstance(members, dict)
        self.assertTrue(page._called["categorymembers"])

    async def test_undocumented_api_field(self):
        page = self.wiki.page("Test_1")
        self.assertFalse(page._called["info"])
        value = await page.api_new_experimental_field
        self.assertEqual(value, "test_value")
        self.assertTrue(page._called["info"])

    async def test_undocumented_api_field_cached_after_first_access(self):
        page = self.wiki.page("Test_1")
        await page.api_new_experimental_field
        self.assertTrue(page._called["info"])
        calls_before = page._called.copy()
        await page.api_new_experimental_field
        self.assertEqual(calls_before, page._called)

    async def test_exists_true(self):
        page = self.wiki.page("Test_1")
        self.assertTrue(await page.exists())

    async def test_exists_false_for_nonexistent(self):
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")

        async def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get
        page = wiki.page("NonExistent")
        self.assertFalse(await page.exists())

    async def test_section_by_title_found(self):
        page = self.wiki.page("Test_1")
        await page.summary
        sec = page.section_by_title("Section 1")
        self.assertIsNotNone(sec)
        self.assertEqual(sec.title, "Section 1")

    async def test_section_by_title_not_found(self):
        page = self.wiki.page("Test_1")
        await page.summary
        sec = page.section_by_title("Nonexistent Section")
        self.assertIsNone(sec)

    async def test_sections_by_title_found(self):
        page = self.wiki.page("Test_1")
        await page.sections
        secs = page.sections_by_title("Section 1")
        self.assertIsInstance(secs, list)
        self.assertEqual(len(secs), 1)
        self.assertEqual(secs[0].title, "Section 1")

    async def test_sections_by_title_not_found(self):
        page = self.wiki.page("Test_1")
        await page.sections
        secs = page.sections_by_title("Nonexistent Section")
        self.assertIsInstance(secs, list)
        self.assertEqual(len(secs), 0)

    async def test_sections_populated_after_summary(self):
        page = self.wiki.page("Test_1")
        await page.summary
        sections = await page.sections
        self.assertGreater(len(sections), 0)


class TestAsyncWikipediaPageAttributesMapping(unittest.IsolatedAsyncioTestCase):
    """Verify every key in ATTRIBUTES_MAPPING is accessible on AsyncWikipediaPage."""

    def setUp(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        self.wiki._get = async_wikipedia_api_request(self.wiki)

    # ---- Init attributes — no fetch required ----

    def test_language_no_fetch(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.language, "en")

    def test_variant_no_fetch(self):
        page = self.wiki.page("Test_1")
        self.assertIsNone(page.variant)

    # ---- pageid — lazy awaitable; ns / title — set at init ----

    async def test_pageid(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.pageid, 4)

    def test_ns(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.ns, 0)

    def test_title(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.title, "Test_1")

    # ---- Attributes populated by info ----

    async def test_contentmodel(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.contentmodel, "wikitext")

    async def test_pagelanguage(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.pagelanguage, "en")

    async def test_pagelanguagehtmlcode(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.pagelanguagehtmlcode, "en")

    async def test_pagelanguagedir(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.pagelanguagedir, "ltr")

    async def test_touched(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.touched, "2023-01-01T00:00:00Z")

    async def test_lastrevid(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.lastrevid, 12345)

    async def test_length(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.length, 6789)

    async def test_protection(self):
        page = self.wiki.page("Test_1")
        protection = await page.protection
        self.assertIsInstance(protection, list)
        self.assertEqual(len(protection), 1)
        self.assertEqual(protection[0]["type"], "create")

    async def test_restrictiontypes(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.restrictiontypes, ["create"])

    async def test_watchers(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.watchers, 100)

    async def test_visitingwatchers(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.visitingwatchers, 50)

    async def test_notificationtimestamp(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.notificationtimestamp, "")

    async def test_talkid(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.talkid, 5)

    async def test_fullurl(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.fullurl, "https://en.wikipedia.org/wiki/Test_1")

    async def test_editurl(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(
            await page.editurl,
            "https://en.wikipedia.org/w/index.php?title=Test_1&action=edit",
        )

    async def test_canonicalurl(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.canonicalurl, "https://en.wikipedia.org/wiki/Test_1")

    async def test_readable(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.readable, "")

    async def test_preload(self):
        page = self.wiki.page("Test_1")
        self.assertIsNone(await page.preload)

    async def test_displaytitle(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.displaytitle, "Test 1")

    async def test_varianttitles(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(await page.varianttitles, {})

    # ---- pageid / ns / title also populated by langlinks ----

    async def test_pageid_after_langlinks(self):
        page = self.wiki.page("Test_1")
        await page.langlinks
        self.assertEqual(await page.pageid, 4)

    async def test_ns_after_langlinks(self):
        page = self.wiki.page("Test_1")
        await page.langlinks
        self.assertEqual(page.ns, 0)

    async def test_title_after_langlinks(self):
        page = self.wiki.page("Test_1")
        await page.langlinks
        self.assertEqual(page.title, "Test 1")
