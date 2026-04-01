"""Integration tests for WikipediaPage properties using VCR cassettes."""

import pytest

import wikipediaapi


class TestVcrPageInfoProps:
    """Test all info-sourced properties on WikipediaPage."""

    @pytest.mark.vcr
    def test_pageid(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert isinstance(page.pageid, int)
        assert page.pageid > 0

    @pytest.mark.vcr
    def test_contentmodel(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert page.contentmodel == "wikitext"

    @pytest.mark.vcr
    def test_pagelanguage(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert page.pagelanguage == "en"

    @pytest.mark.vcr
    def test_pagelanguagehtmlcode(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert page.pagelanguagehtmlcode == "en"

    @pytest.mark.vcr
    def test_pagelanguagedir(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert page.pagelanguagedir == "ltr"

    @pytest.mark.vcr
    def test_touched(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert isinstance(page.touched, str)
        assert len(page.touched) > 0

    @pytest.mark.vcr
    def test_lastrevid(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert isinstance(page.lastrevid, int)
        assert page.lastrevid > 0

    @pytest.mark.vcr
    def test_length(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert isinstance(page.length, int)
        assert page.length > 0

    @pytest.mark.vcr
    def test_protection(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert isinstance(page.protection, list)

    @pytest.mark.vcr
    def test_restrictiontypes(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert isinstance(page.restrictiontypes, list)
        assert len(page.restrictiontypes) > 0

    @pytest.mark.vcr
    def test_watchers(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        # watchers may be None if the API doesn't expose it
        watchers = page.watchers
        assert watchers is None or isinstance(watchers, int)

    @pytest.mark.vcr
    def test_visitingwatchers(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        vw = page.visitingwatchers
        assert vw is None or isinstance(vw, int)

    @pytest.mark.vcr
    def test_notificationtimestamp(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        ts = page.notificationtimestamp
        assert ts is None or isinstance(ts, str)

    @pytest.mark.vcr
    def test_talkid(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert isinstance(page.talkid, int)
        assert page.talkid > 0

    @pytest.mark.vcr
    def test_fullurl(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert isinstance(page.fullurl, str)
        assert "wikipedia.org" in page.fullurl

    @pytest.mark.vcr
    def test_editurl(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert isinstance(page.editurl, str)
        assert "wikipedia.org" in page.editurl

    @pytest.mark.vcr
    def test_canonicalurl(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert isinstance(page.canonicalurl, str)
        assert "wikipedia.org" in page.canonicalurl

    @pytest.mark.vcr
    def test_readable(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        # readable is a string or None
        r = page.readable
        assert r is None or isinstance(r, (str, bool))

    @pytest.mark.vcr
    def test_preload(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        # preload is typically empty string or None
        p = page.preload
        assert p is None or isinstance(p, str)

    @pytest.mark.vcr
    def test_displaytitle(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert isinstance(page.displaytitle, str)
        assert "Python" in page.displaytitle

    @pytest.mark.vcr
    def test_varianttitles(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        vt = page.varianttitles
        assert vt is None or isinstance(vt, dict)


class TestVcrPageExtractProps:
    """Test extract-sourced properties on WikipediaPage."""

    @pytest.mark.vcr
    def test_summary(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert isinstance(page.summary, str)
        assert len(page.summary) > 100
        assert "Python" in page.summary

    @pytest.mark.vcr
    def test_sections(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        sections = page.sections
        assert isinstance(sections, list)
        assert len(sections) > 0
        assert all(isinstance(s, wikipediaapi.WikipediaPageSection) for s in sections)

    @pytest.mark.vcr
    def test_text(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        text = page.text
        assert isinstance(text, str)
        assert len(text) > len(page.summary)

    @pytest.mark.vcr
    def test_sections_by_title(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        sections = page.sections_by_title("History")
        assert isinstance(sections, list)
        assert len(sections) >= 1
        assert sections[0].title == "History"

    @pytest.mark.vcr
    def test_sections_by_title_missing(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        sections = page.sections_by_title("NonexistentSection12345")
        assert sections == []

    @pytest.mark.vcr
    def test_section_by_title(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        section = page.section_by_title("History")
        assert section is not None
        assert section.title == "History"

    @pytest.mark.vcr
    def test_section_by_title_missing(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        section = page.section_by_title("NonexistentSection12345")
        assert section is None


class TestVcrPageRelationProps:
    """Test relation properties on WikipediaPage."""

    @pytest.mark.vcr
    def test_langlinks(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        ll = page.langlinks
        assert isinstance(ll, dict)
        assert len(ll) > 0
        # Should contain some well-known languages
        assert any(lang in ll for lang in ("de", "fr", "es", "ja"))

    @pytest.mark.vcr
    def test_links(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        links = page.links
        assert isinstance(links, dict)
        assert len(links) > 0

    @pytest.mark.vcr
    def test_backlinks(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        bl = page.backlinks
        assert isinstance(bl, dict)
        assert len(bl) > 0

    @pytest.mark.vcr
    def test_categories(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        cats = page.categories
        assert isinstance(cats, dict)
        assert len(cats) > 0

    @pytest.mark.vcr
    def test_categorymembers(self, sync_wiki):
        page = sync_wiki.page("Category:Physics")
        members = page.categorymembers
        assert isinstance(members, dict)
        assert len(members) > 0


class TestVcrPageCoordinatesImages:
    """Test coordinates and images properties on WikipediaPage."""

    @pytest.mark.vcr
    def test_coordinates(self, sync_wiki):
        page = sync_wiki.page("London")
        coords = page.coordinates
        assert isinstance(coords, list)
        assert len(coords) > 0
        coord = coords[0]
        assert isinstance(coord, wikipediaapi.Coordinate)

    @pytest.mark.vcr
    def test_images(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        imgs = page.images
        assert isinstance(imgs, wikipediaapi.ImagesDict)
        assert len(imgs) > 0


class TestVcrPageMeta:
    """Test geosearch_meta and search_meta on WikipediaPage."""

    @pytest.mark.vcr
    def test_geosearch_meta(self, sync_wiki):
        results = sync_wiki.geosearch(
            coord=wikipediaapi.GeoPoint(51.5074, -0.1278),
            limit=3,
        )
        assert len(results) > 0
        first_page = next(iter(results.values()))
        meta = first_page.geosearch_meta
        assert isinstance(meta, wikipediaapi.GeoSearchMeta)

    @pytest.mark.vcr
    def test_search_meta(self, sync_wiki):
        results = sync_wiki.search("Python programming", limit=3)
        assert len(results.pages) > 0
        first_page = next(iter(results.pages.values()))
        meta = first_page.search_meta
        assert isinstance(meta, wikipediaapi.SearchMeta)


class TestVcrPageExistence:
    """Test exists() for existing and non-existing pages."""

    @pytest.mark.vcr
    def test_exists_true(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert page.exists() is True

    @pytest.mark.vcr
    def test_exists_false(self, sync_wiki):
        page = sync_wiki.page("NonExistentPage_WikiAPI_Test_12345")
        assert page.exists() is False


class TestVcrPageIdentity:
    """Test named props, repr, eq, and hash on WikipediaPage."""

    def test_named_props(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert page.language == "en"
        assert page.variant is None
        assert page.title == "Python_(programming_language)"
        assert page.ns == wikipediaapi.Namespace.MAIN
        assert page.namespace == wikipediaapi.Namespace.MAIN

    @pytest.mark.vcr
    def test_repr_after_fetch(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        _ = page.pageid  # trigger fetch
        r = repr(page)
        assert "Python" in r
        assert "lang: en" in r
        assert "ns: 0" in r

    def test_eq_and_hash(self, sync_wiki):
        p1 = sync_wiki.page("Python_(programming_language)")
        p2 = sync_wiki.page("Python_(programming_language)")
        p3 = sync_wiki.page("Earth")
        assert p1 == p2
        assert p1 != p3
        assert hash(p1) == hash(p2)
        assert hash(p1) != hash(p3)
