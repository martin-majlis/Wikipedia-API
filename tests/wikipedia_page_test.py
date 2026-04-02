import pytest

import wikipediaapi
from tests.mock_data import user_agent, wikipedia_api_request


class TestWikipediaPage:
    def setup_method(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_dir_includes_attributes_mapping_keys(self):
        page = self.wiki.page("Test_1")
        d = dir(page)
        for attr in ["pageid", "fullurl", "displaytitle", "canonicalurl", "editurl"]:
            assert attr in d

    def test_dir_includes_data_properties(self):
        page = self.wiki.page("Test_1")
        d = dir(page)
        for attr in ["summary", "text", "langlinks", "links", "backlinks", "categories"]:
            assert attr in d

    def test_pageid_from_extracts_no_info_call(self):
        page = self.wiki.page("Test_1")
        _ = page.summary  # triggers extracts, which includes pageid
        assert page._called["info"] is False
        assert page.pageid == 4
        assert page._called["info"] is False  # pageid was cached; info still not needed

    def test_pageid_from_langlinks_no_info_call(self):
        page = self.wiki.page("Test_1")
        _ = page.langlinks  # triggers langlinks, which includes pageid
        assert page._called["info"] is False
        assert page.pageid == 4
        assert page._called["info"] is False  # pageid was cached; info still not needed

    def test_title_from_extracts_no_info_call(self):
        page = self.wiki.page("Test_1")
        _ = page.summary  # extracts also populates title and ns
        assert page._called["info"] is False
        assert page.title == "Test 1"
        assert page.ns == 0

    def test_repr_before_fetching(self):
        page = self.wiki.page("Test_1")
        assert repr(page) == "Test_1 (lang: en, variant: None, id: ??, ns: 0)"

    def test_repr_after_fetching(self):
        page = self.wiki.page("Test_1")
        assert repr(page) == "Test_1 (lang: en, variant: None, id: ??, ns: 0)"
        assert page.pageid == 4
        assert repr(page) == "Test 1 (lang: en, variant: None, id: 4, ns: 0)"

    def test_extract(self):
        page = self.wiki.page("Test_1")
        assert page.pageid == 4
        assert page.title == "Test 1"
        assert page.ns == 0
        assert page.contentmodel == "wikitext"
        assert page.pagelanguage == "en"
        assert page.pagelanguagedir == "ltr"
        assert page.fullurl == "https://en.wikipedia.org/wiki/Test_1"
        assert page.editurl == "https://en.wikipedia.org/w/index.php?title=Test_1&action=edit"
        assert page.canonicalurl == "https://en.wikipedia.org/wiki/Test_1"
        assert page.displaytitle == "Test 1"
        assert page.variant is None

    def test_unknown_property(self):
        page = self.wiki.page("Test_1")
        with pytest.raises(AttributeError):
            _ = page.unknown_property

    def test_undocumented_api_field(self):
        page = self.wiki.page("Test_1")
        assert page._called["info"] is False
        assert page.api_new_experimental_field == "test_value"
        assert page._called["info"] is True

    def test_undocumented_api_field_cached_after_first_access(self):
        page = self.wiki.page("Test_1")
        _ = page.api_new_experimental_field
        assert page._called["info"] is True
        calls_before = page._called.copy()
        _ = page.api_new_experimental_field
        assert calls_before == page._called

    def test_nonexisting(self):
        page = self.wiki.page("NonExisting")
        assert page.exists() is False

    def test_existing(self):
        page = self.wiki.page("Test_1")
        assert page.exists() is True

    def test_page_identity_equality(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("Test_1")
        assert p1 == p2
        assert hash(p1) == hash(p2)

    def test_page_identity_inequality(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("Test_1", ns=wikipediaapi.Namespace.CATEGORY)
        assert p1 != p2

    def test_page_equality_with_non_page_object(self):
        p1 = self.wiki.page("Test_1")
        assert p1 != "not a page"
        assert p1 is not None
        assert p1 != 42

    def test_page_hash_consistency(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("Test_1")
        p3 = self.wiki.page("Test_2")

        # Same pages should have same hash
        assert hash(p1) == hash(p2)
        # Different pages should have different hashes
        assert hash(p1) != hash(p3)

        # Hash should be consistent across multiple calls
        h1 = hash(p1)
        h2 = hash(p1)
        assert h1 == h2

    def test_private_attribute_access(self):
        p = self.wiki.page("Test_1")

        # Test accessing private attributes raises AttributeError
        with pytest.raises(AttributeError) as cm:
            _ = p._private_attr
        assert "object has no attribute '_private_attr'" in str(cm.value)

        with pytest.raises(AttributeError) as cm:
            _ = p.__dict__
        assert "object has no attribute '__dict__'" in str(cm.value)

    def test_missing_attribute_access(self):
        p = self.wiki.page("Test_1")

        # Test accessing non-existent attributes raises AttributeError
        with pytest.raises(AttributeError) as cm:
            _ = p.non_existent_attr
        assert "object has no attribute 'non_existent_attr'" in str(cm.value)

        with pytest.raises(AttributeError) as cm:
            _ = p.definitely_not_here
        assert "object has no attribute 'definitely_not_here'" in str(cm.value)

    def test_attribute_access_without_cache(self):
        p = self.wiki.page("Test_1")

        # Remove _attributes to simulate uninitialized state
        if hasattr(p, "_attributes"):
            object.__delattr__(p, "_attributes")

        with pytest.raises(AttributeError) as cm:
            _ = p.any_attr
        assert "object has no attribute 'any_attr'" in str(cm.value)

    def test_article_method(self):
        p = self.wiki.page("Test_1")
        a = self.wiki.article("Test_1")
        assert p.pageid == a.pageid

    def test_article_title_unquote(self):
        # https://github.com/goldsmith/Wikipedia/issues/190
        w = wikipediaapi.Wikipedia(user_agent, "hi")
        w._get = wikipedia_api_request(w)
        p_encoded = w.article(
            "%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8",
            unquote=True,
        )
        p_decoded = w.article("पाइथन")
        assert p_encoded.pageid == p_decoded.pageid

    def test_page_title_unquote(self):
        # https://github.com/goldsmith/Wikipedia/issues/190
        w = wikipediaapi.Wikipedia(user_agent, "hi")
        w._get = wikipedia_api_request(w)
        p_encoded = w.page(
            "%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8",
            unquote=True,
        )
        p_decoded = w.page("पाइथन")
        assert p_encoded.pageid == p_decoded.pageid

    def test_page_with_int_namespace(self):
        page = self.wiki.page("NonExisting", ns=110)
        assert page.exists() is False
        assert 110 == page.namespace

    def test_page_with_variant(self):
        wiki = wikipediaapi.Wikipedia(user_agent, "zh", "zh-tw")
        wiki._get = wikipedia_api_request(wiki)
        page = wiki.page("Test_Zh-Tw")
        assert page.exists() is True
        assert page.pageid == 44
        assert page.title == "Test Zh-Tw"
        assert page.variant == "zh-tw"
        assert page.varianttitles == {
            "zh": "Test Zh",
            "zh-hans": "Test Zh-Hans",
            "zh-tw": "Test Zh-Tw",
        }

    def test_page_with_extra_parameters(self):
        wiki = wikipediaapi.Wikipedia(user_agent, "en", extra_api_params={"foo": "bar"})
        wiki._get = wikipedia_api_request(wiki)
        page = wiki.page("Extra_API_Params")
        assert page.exists() is True

    def test_section_by_title_found(self):
        page = self.wiki.page("Test_1")
        sec = page.section_by_title("Section 1")
        assert sec is not None
        assert sec.title == "Section 1"

    def test_section_by_title_not_found(self):
        page = self.wiki.page("Test_1")
        sec = page.section_by_title("Nonexistent Section")
        assert sec is None

    def test_sections_by_title_found(self):
        page = self.wiki.page("Test_1")
        secs = page.sections_by_title("Section 1")
        assert isinstance(secs, list)
        assert len(secs) == 1
        assert secs[0].title == "Section 1"

    def test_sections_by_title_not_found(self):
        page = self.wiki.page("Test_1")
        secs = page.sections_by_title("Nonexistent Section")
        assert isinstance(secs, list)
        assert len(secs) == 0


class TestWikipediaPageAttributesMapping:
    """Verify every key in ATTRIBUTES_MAPPING is accessible on WikipediaPage."""

    def setup_method(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    # ---- Init attributes — no fetch required ----

    def test_language(self):
        page = self.wiki.page("Test_1")
        assert page.language == "en"

    def test_variant(self):
        page = self.wiki.page("Test_1")
        assert page.variant is None

    # ---- pageid — lazy fetch; ns / title — set at init ----

    def test_pageid(self):
        page = self.wiki.page("Test_1")
        assert page.pageid == 4

    def test_ns(self):
        page = self.wiki.page("Test_1")
        assert page.ns == 0

    def test_title(self):
        page = self.wiki.page("Test_1")
        assert page.title == "Test_1"

    # ---- Info-only attributes — lazily fetched on first access ----

    def test_contentmodel(self):
        page = self.wiki.page("Test_1")
        assert page.contentmodel == "wikitext"

    def test_pagelanguage(self):
        page = self.wiki.page("Test_1")
        assert page.pagelanguage == "en"

    def test_pagelanguagehtmlcode(self):
        page = self.wiki.page("Test_1")
        assert page.pagelanguagehtmlcode == "en"

    def test_pagelanguagedir(self):
        page = self.wiki.page("Test_1")
        assert page.pagelanguagedir == "ltr"

    def test_touched(self):
        page = self.wiki.page("Test_1")
        assert page.touched == "2023-01-01T00:00:00Z"

    def test_lastrevid(self):
        page = self.wiki.page("Test_1")
        assert page.lastrevid == 12345

    def test_length(self):
        page = self.wiki.page("Test_1")
        assert page.length == 6789

    def test_protection(self):
        page = self.wiki.page("Test_1")
        protection = page.protection
        assert isinstance(protection, list)
        assert len(protection) == 1
        assert protection[0]["type"] == "create"

    def test_restrictiontypes(self):
        page = self.wiki.page("Test_1")
        assert page.restrictiontypes == ["create"]

    def test_watchers(self):
        page = self.wiki.page("Test_1")
        assert page.watchers == 100

    def test_visitingwatchers(self):
        page = self.wiki.page("Test_1")
        assert page.visitingwatchers == 50

    def test_notificationtimestamp(self):
        page = self.wiki.page("Test_1")
        assert page.notificationtimestamp == ""

    def test_talkid(self):
        page = self.wiki.page("Test_1")
        assert page.talkid == 5

    def test_fullurl(self):
        page = self.wiki.page("Test_1")
        assert page.fullurl == "https://en.wikipedia.org/wiki/Test_1"

    def test_editurl(self):
        page = self.wiki.page("Test_1")
        assert page.editurl == "https://en.wikipedia.org/w/index.php?title=Test_1&action=edit"

    def test_canonicalurl(self):
        page = self.wiki.page("Test_1")
        assert page.canonicalurl == "https://en.wikipedia.org/wiki/Test_1"

    def test_readable(self):
        page = self.wiki.page("Test_1")
        assert page.readable == ""

    def test_preload(self):
        page = self.wiki.page("Test_1")
        assert page.preload is None

    def test_displaytitle(self):
        page = self.wiki.page("Test_1")
        assert page.displaytitle == "Test 1"

    def test_varianttitles(self):
        page = self.wiki.page("Test_1")
        assert page.varianttitles == {}
