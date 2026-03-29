"""Integration tests for AsyncWikipediaPage properties using VCR cassettes."""

import pytest

import wikipediaapi


class TestVcrAsyncPageInfoProps:
    """Test all info-sourced properties on AsyncWikipediaPage."""

    @pytest.mark.vcr
    async def test_pageid(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        pageid = await page.pageid
        assert isinstance(pageid, int)
        assert pageid > 0

    @pytest.mark.vcr
    async def test_contentmodel(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        assert await page.contentmodel == "wikitext"

    @pytest.mark.vcr
    async def test_pagelanguage(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        assert await page.pagelanguage == "en"

    @pytest.mark.vcr
    async def test_pagelanguagehtmlcode(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        assert await page.pagelanguagehtmlcode == "en"

    @pytest.mark.vcr
    async def test_pagelanguagedir(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        assert await page.pagelanguagedir == "ltr"

    @pytest.mark.vcr
    async def test_touched(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        touched = await page.touched
        assert isinstance(touched, str)
        assert len(touched) > 0

    @pytest.mark.vcr
    async def test_lastrevid(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        lastrevid = await page.lastrevid
        assert isinstance(lastrevid, int)
        assert lastrevid > 0

    @pytest.mark.vcr
    async def test_length(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        length = await page.length
        assert isinstance(length, int)
        assert length > 0

    @pytest.mark.vcr
    async def test_protection(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        protection = await page.protection
        assert isinstance(protection, list)

    @pytest.mark.vcr
    async def test_restrictiontypes(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        rt = await page.restrictiontypes
        assert isinstance(rt, list)
        assert len(rt) > 0

    @pytest.mark.vcr
    async def test_watchers(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        watchers = await page.watchers
        assert watchers is None or isinstance(watchers, int)

    @pytest.mark.vcr
    async def test_visitingwatchers(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        vw = await page.visitingwatchers
        assert vw is None or isinstance(vw, int)

    @pytest.mark.vcr
    async def test_notificationtimestamp(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        ts = await page.notificationtimestamp
        assert ts is None or isinstance(ts, str)

    @pytest.mark.vcr
    async def test_talkid(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        talkid = await page.talkid
        assert isinstance(talkid, int)
        assert talkid > 0

    @pytest.mark.vcr
    async def test_fullurl(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        fullurl = await page.fullurl
        assert isinstance(fullurl, str)
        assert "wikipedia.org" in fullurl

    @pytest.mark.vcr
    async def test_editurl(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        editurl = await page.editurl
        assert isinstance(editurl, str)
        assert "wikipedia.org" in editurl

    @pytest.mark.vcr
    async def test_canonicalurl(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        curl = await page.canonicalurl
        assert isinstance(curl, str)
        assert "wikipedia.org" in curl

    @pytest.mark.vcr
    async def test_readable(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        r = await page.readable
        assert r is None or isinstance(r, (str, bool))

    @pytest.mark.vcr
    async def test_preload(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        p = await page.preload
        assert p is None or isinstance(p, str)

    @pytest.mark.vcr
    async def test_displaytitle(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        dt = await page.displaytitle
        assert isinstance(dt, str)
        assert "Python" in dt

    @pytest.mark.vcr
    async def test_varianttitles(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        vt = await page.varianttitles
        assert vt is None or isinstance(vt, dict)


class TestVcrAsyncPageExtractProps:
    """Test extract-sourced properties on AsyncWikipediaPage."""

    @pytest.mark.vcr
    async def test_summary(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        summary = await page.summary
        assert isinstance(summary, str)
        assert len(summary) > 100
        assert "Python" in summary

    @pytest.mark.vcr
    async def test_sections(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        sections = await page.sections
        assert isinstance(sections, list)
        assert len(sections) > 0
        assert all(isinstance(s, wikipediaapi.WikipediaPageSection) for s in sections)

    @pytest.mark.vcr
    async def test_text(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        text = await page.text
        summary = await page.summary
        assert isinstance(text, str)
        assert len(text) > len(summary)

    @pytest.mark.vcr
    async def test_sections_by_title(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        # Need to trigger extracts fetch first for sections_by_title
        _ = await page.sections
        sections = page.sections_by_title("History")
        assert isinstance(sections, list)
        assert len(sections) >= 1
        assert sections[0].title == "History"

    @pytest.mark.vcr
    async def test_sections_by_title_missing(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        _ = await page.sections
        sections = page.sections_by_title("NonexistentSection12345")
        assert sections == []

    @pytest.mark.vcr
    async def test_section_by_title(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        _ = await page.sections
        section = page.section_by_title("History")
        assert section is not None
        assert section.title == "History"

    @pytest.mark.vcr
    async def test_section_by_title_missing(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        _ = await page.sections
        section = page.section_by_title("NonexistentSection12345")
        assert section is None


class TestVcrAsyncPageRelationProps:
    """Test relation properties on AsyncWikipediaPage."""

    @pytest.mark.vcr
    async def test_langlinks(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        ll = await page.langlinks
        assert isinstance(ll, dict)
        assert len(ll) > 0
        assert any(lang in ll for lang in ("de", "fr", "es", "ja"))

    @pytest.mark.vcr
    async def test_links(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        links = await page.links
        assert isinstance(links, dict)
        assert len(links) > 0

    @pytest.mark.vcr
    async def test_backlinks(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        bl = await page.backlinks
        assert isinstance(bl, dict)
        assert len(bl) > 0

    @pytest.mark.vcr
    async def test_categories(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        cats = await page.categories
        assert isinstance(cats, dict)
        assert len(cats) > 0

    @pytest.mark.vcr
    async def test_categorymembers(self, async_wiki):
        page = async_wiki.page("Category:Physics")
        members = await page.categorymembers
        assert isinstance(members, dict)
        assert len(members) > 0


class TestVcrAsyncPageCoordinatesImages:
    """Test coordinates and images on AsyncWikipediaPage."""

    @pytest.mark.vcr
    async def test_coordinates(self, async_wiki):
        page = async_wiki.page("London")
        coords = await page.coordinates
        assert isinstance(coords, list)
        assert len(coords) > 0
        coord = coords[0]
        assert isinstance(coord, wikipediaapi.Coordinate)

    @pytest.mark.vcr
    async def test_images(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        imgs = await page.images
        assert isinstance(imgs, dict)
        assert len(imgs) > 0


class TestVcrAsyncPageMeta:
    """Test geosearch_meta and search_meta on AsyncWikipediaPage."""

    @pytest.mark.vcr
    async def test_geosearch_meta(self, async_wiki):
        results = await async_wiki.geosearch(
            coord=wikipediaapi.GeoPoint(51.5074, -0.1278),
            limit=3,
        )
        assert len(results) > 0
        first_page = next(iter(results.values()))
        meta = first_page.geosearch_meta
        assert isinstance(meta, wikipediaapi.GeoSearchMeta)

    @pytest.mark.vcr
    async def test_search_meta(self, async_wiki):
        results = await async_wiki.search("Python programming", limit=3)
        assert len(results.pages) > 0
        first_page = next(iter(results.pages.values()))
        meta = first_page.search_meta
        assert isinstance(meta, wikipediaapi.SearchMeta)


class TestVcrAsyncPageExistence:
    """Test exists() for existing and non-existing pages."""

    @pytest.mark.vcr
    async def test_exists_true(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        assert await page.exists() is True

    @pytest.mark.vcr
    async def test_exists_false(self, async_wiki):
        page = async_wiki.page("NonExistentPage_WikiAPI_Test_12345")
        assert await page.exists() is False


class TestVcrAsyncPageIdentity:
    """Test named props, repr, eq, and hash on AsyncWikipediaPage."""

    def test_named_props(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        assert page.language == "en"
        assert page.variant is None
        assert page.title == "Python_(programming_language)"
        assert page.ns == wikipediaapi.Namespace.MAIN
        assert page.namespace == wikipediaapi.Namespace.MAIN

    @pytest.mark.vcr
    async def test_repr_after_fetch(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        _ = await page.pageid
        r = repr(page)
        assert "Python" in r
        assert "lang: en" in r
        assert "ns: 0" in r

    def test_eq_and_hash(self, async_wiki):
        p1 = async_wiki.page("Python_(programming_language)")
        p2 = async_wiki.page("Python_(programming_language)")
        p3 = async_wiki.page("Earth")
        assert p1 == p2
        assert p1 != p3
        assert hash(p1) == hash(p2)
        assert hash(p1) != hash(p3)
