import unittest

from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi


class TestWikipediaPage(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_dir_includes_attributes_mapping_keys(self):
        page = self.wiki.page("Test_1")
        d = dir(page)
        for attr in ["pageid", "fullurl", "displaytitle", "canonicalurl", "editurl"]:
            self.assertIn(attr, d)

    def test_dir_includes_data_properties(self):
        page = self.wiki.page("Test_1")
        d = dir(page)
        for attr in ["summary", "text", "langlinks", "links", "backlinks", "categories"]:
            self.assertIn(attr, d)

    def test_pageid_from_extracts_no_info_call(self):
        page = self.wiki.page("Test_1")
        _ = page.summary  # triggers extracts, which includes pageid
        self.assertFalse(page._called["info"])
        self.assertEqual(page.pageid, 4)
        self.assertFalse(page._called["info"])  # pageid was cached; info still not needed

    def test_pageid_from_langlinks_no_info_call(self):
        page = self.wiki.page("Test_1")
        _ = page.langlinks  # triggers langlinks, which includes pageid
        self.assertFalse(page._called["info"])
        self.assertEqual(page.pageid, 4)
        self.assertFalse(page._called["info"])  # pageid was cached; info still not needed

    def test_title_from_extracts_no_info_call(self):
        page = self.wiki.page("Test_1")
        _ = page.summary  # extracts also populates title and ns
        self.assertFalse(page._called["info"])
        self.assertEqual(page.title, "Test 1")
        self.assertEqual(page.ns, 0)

    def test_repr_before_fetching(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(repr(page), "Test_1 (lang: en, variant: None, id: ??, ns: 0)")

    def test_repr_after_fetching(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(repr(page), "Test_1 (lang: en, variant: None, id: ??, ns: 0)")
        self.assertEqual(page.pageid, 4)
        self.assertEqual(repr(page), "Test 1 (lang: en, variant: None, id: 4, ns: 0)")

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
        self.assertEqual(page.variant, None)

    def test_unknown_property(self):
        page = self.wiki.page("Test_1")
        with self.assertRaises(AttributeError):
            page.unknown_property

    def test_undocumented_api_field(self):
        page = self.wiki.page("Test_1")
        self.assertFalse(page._called["info"])
        self.assertEqual(page.api_new_experimental_field, "test_value")
        self.assertTrue(page._called["info"])

    def test_undocumented_api_field_cached_after_first_access(self):
        page = self.wiki.page("Test_1")
        _ = page.api_new_experimental_field
        self.assertTrue(page._called["info"])
        calls_before = page._called.copy()
        _ = page.api_new_experimental_field
        self.assertEqual(calls_before, page._called)

    def test_nonexisting(self):
        page = self.wiki.page("NonExisting")
        self.assertFalse(page.exists())

    def test_existing(self):
        page = self.wiki.page("Test_1")
        self.assertTrue(page.exists())

    def test_page_identity_equality(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("Test_1")
        self.assertEqual(p1, p2)
        self.assertEqual(hash(p1), hash(p2))

    def test_page_identity_inequality(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("Test_1", ns=wikipediaapi.Namespace.CATEGORY)
        self.assertNotEqual(p1, p2)

    def test_page_equality_with_non_page_object(self):
        p1 = self.wiki.page("Test_1")
        self.assertNotEqual(p1, "not a page")
        self.assertNotEqual(p1, None)
        self.assertNotEqual(p1, 42)

    def test_page_hash_consistency(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("Test_1")
        p3 = self.wiki.page("Test_2")

        # Same pages should have same hash
        self.assertEqual(hash(p1), hash(p2))
        # Different pages should have different hashes
        self.assertNotEqual(hash(p1), hash(p3))

        # Hash should be consistent across multiple calls
        h1 = hash(p1)
        h2 = hash(p1)
        self.assertEqual(h1, h2)

    def test_private_attribute_access(self):
        p = self.wiki.page("Test_1")

        # Test accessing private attributes raises AttributeError
        with self.assertRaises(AttributeError) as cm:
            _ = p._private_attr
        self.assertIn("object has no attribute '_private_attr'", str(cm.exception))

        with self.assertRaises(AttributeError) as cm:
            _ = p.__dict__
        self.assertIn("object has no attribute '__dict__'", str(cm.exception))

    def test_missing_attribute_access(self):
        p = self.wiki.page("Test_1")

        # Test accessing non-existent attributes raises AttributeError
        with self.assertRaises(AttributeError) as cm:
            _ = p.non_existent_attr
        self.assertIn("object has no attribute 'non_existent_attr'", str(cm.exception))

        with self.assertRaises(AttributeError) as cm:
            _ = p.definitely_not_here
        self.assertIn("object has no attribute 'definitely_not_here'", str(cm.exception))

    def test_attribute_access_without_cache(self):
        p = self.wiki.page("Test_1")

        # Remove _attributes to simulate uninitialized state
        if hasattr(p, "_attributes"):
            object.__delattr__(p, "_attributes")

        with self.assertRaises(AttributeError) as cm:
            _ = p.any_attr
        self.assertIn("object has no attribute 'any_attr'", str(cm.exception))

    def test_article_method(self):
        p = self.wiki.page("Test_1")
        a = self.wiki.article("Test_1")
        self.assertEqual(p.pageid, a.pageid)

    def test_article_title_unquote(self):
        # https://github.com/goldsmith/Wikipedia/issues/190
        w = wikipediaapi.Wikipedia(user_agent, "hi")
        w._get = wikipedia_api_request(w)
        p_encoded = w.article(
            "%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8",
            unquote=True,
        )
        p_decoded = w.article("पाइथन")
        self.assertEqual(p_encoded.pageid, p_decoded.pageid)

    def test_page_title_unquote(self):
        # https://github.com/goldsmith/Wikipedia/issues/190
        w = wikipediaapi.Wikipedia(user_agent, "hi")
        w._get = wikipedia_api_request(w)
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

    def test_page_with_variant(self):
        wiki = wikipediaapi.Wikipedia(user_agent, "zh", "zh-tw")
        wiki._get = wikipedia_api_request(wiki)
        page = wiki.page("Test_Zh-Tw")
        self.assertTrue(page.exists())
        self.assertEqual(page.pageid, 44)
        self.assertEqual(page.title, "Test Zh-Tw")
        self.assertEqual(page.variant, "zh-tw")
        self.assertEqual(
            page.varianttitles,
            {"zh": "Test Zh", "zh-hans": "Test Zh-Hans", "zh-tw": "Test Zh-Tw"},
        )

    def test_page_with_extra_parameters(self):
        wiki = wikipediaapi.Wikipedia(user_agent, "en", extra_api_params={"foo": "bar"})
        wiki._get = wikipedia_api_request(wiki)
        page = wiki.page("Extra_API_Params")
        self.assertTrue(page.exists())

    def test_section_by_title_found(self):
        page = self.wiki.page("Test_1")
        sec = page.section_by_title("Section 1")
        self.assertIsNotNone(sec)
        self.assertEqual(sec.title, "Section 1")

    def test_section_by_title_not_found(self):
        page = self.wiki.page("Test_1")
        sec = page.section_by_title("Nonexistent Section")
        self.assertIsNone(sec)

    def test_sections_by_title_found(self):
        page = self.wiki.page("Test_1")
        secs = page.sections_by_title("Section 1")
        self.assertIsInstance(secs, list)
        self.assertEqual(len(secs), 1)
        self.assertEqual(secs[0].title, "Section 1")

    def test_sections_by_title_not_found(self):
        page = self.wiki.page("Test_1")
        secs = page.sections_by_title("Nonexistent Section")
        self.assertIsInstance(secs, list)
        self.assertEqual(len(secs), 0)


class TestWikipediaPageAttributesMapping(unittest.TestCase):
    """Verify every key in ATTRIBUTES_MAPPING is accessible on WikipediaPage."""

    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    # ---- Init attributes — no fetch required ----

    def test_language(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.language, "en")

    def test_variant(self):
        page = self.wiki.page("Test_1")
        self.assertIsNone(page.variant)

    # ---- pageid — lazy fetch; ns / title — set at init ----

    def test_pageid(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.pageid, 4)

    def test_ns(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.ns, 0)

    def test_title(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.title, "Test_1")

    # ---- Info-only attributes — lazily fetched on first access ----

    def test_contentmodel(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.contentmodel, "wikitext")

    def test_pagelanguage(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.pagelanguage, "en")

    def test_pagelanguagehtmlcode(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.pagelanguagehtmlcode, "en")

    def test_pagelanguagedir(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.pagelanguagedir, "ltr")

    def test_touched(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.touched, "2023-01-01T00:00:00Z")

    def test_lastrevid(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.lastrevid, 12345)

    def test_length(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.length, 6789)

    def test_protection(self):
        page = self.wiki.page("Test_1")
        protection = page.protection
        self.assertIsInstance(protection, list)
        self.assertEqual(len(protection), 1)
        self.assertEqual(protection[0]["type"], "create")

    def test_restrictiontypes(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.restrictiontypes, ["create"])

    def test_watchers(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.watchers, 100)

    def test_visitingwatchers(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.visitingwatchers, 50)

    def test_notificationtimestamp(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.notificationtimestamp, "")

    def test_talkid(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.talkid, 5)

    def test_fullurl(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.fullurl, "https://en.wikipedia.org/wiki/Test_1")

    def test_editurl(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(
            page.editurl,
            "https://en.wikipedia.org/w/index.php?title=Test_1&action=edit",
        )

    def test_canonicalurl(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.canonicalurl, "https://en.wikipedia.org/wiki/Test_1")

    def test_readable(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.readable, "")

    def test_preload(self):
        page = self.wiki.page("Test_1")
        self.assertIsNone(page.preload)

    def test_displaytitle(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.displaytitle, "Test 1")

    def test_varianttitles(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.varianttitles, {})
