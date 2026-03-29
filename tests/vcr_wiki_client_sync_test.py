"""Integration tests for WikipediaResource methods using VCR cassettes."""

import pytest

import wikipediaapi
from wikipediaapi import CoordinatesProp
from wikipediaapi import CoordinateType
from wikipediaapi import Direction
from wikipediaapi import GeoBox
from wikipediaapi import GeoPoint
from wikipediaapi import GeoSearchSort
from wikipediaapi import Namespace
from wikipediaapi import RedirectFilter
from wikipediaapi import SearchInfo
from wikipediaapi import SearchProp
from wikipediaapi import SearchQiProfile
from wikipediaapi import SearchSort
from wikipediaapi import SearchWhat


class TestVcrWikiConstruction:
    """Test page/article/pages construction (no API calls)."""

    def test_page(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        assert isinstance(page, wikipediaapi.WikipediaPage)
        assert page.title == "Python_(programming_language)"

    def test_article(self, sync_wiki):
        page = sync_wiki.article("Python_(programming_language)")
        assert isinstance(page, wikipediaapi.WikipediaPage)
        assert page.title == "Python_(programming_language)"

    def test_pages(self, sync_wiki):
        pages = sync_wiki.pages(["Earth", "Python_(programming_language)"])
        assert isinstance(pages, wikipediaapi.PagesDict)
        assert len(pages) == 2
        assert "Earth" in pages
        assert "Python_(programming_language)" in pages

    def test_page_with_namespace(self, sync_wiki):
        page = sync_wiki.page("Physics", ns=Namespace.CATEGORY)
        assert page.ns == Namespace.CATEGORY

    def test_page_with_unquote(self, sync_wiki):
        page = sync_wiki.page("Python_%28programming_language%29", unquote=True)
        assert page.title == "Python_(programming_language)"


class TestVcrWikiExtracts:
    """Test wiki.extracts() method."""

    @pytest.mark.vcr
    def test_extracts(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        result = sync_wiki.extracts(page)
        assert isinstance(result, str)
        assert "Python" in result


class TestVcrWikiInfo:
    """Test wiki.info() method."""

    @pytest.mark.vcr
    def test_info(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        result = sync_wiki.info(page)
        assert result is page
        assert page.pageid > 0
        assert page.pagelanguage == "en"


class TestVcrWikiLanglinks:
    """Test wiki.langlinks() method."""

    @pytest.mark.vcr
    def test_langlinks(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        ll = sync_wiki.langlinks(page)
        assert isinstance(ll, dict)
        assert len(ll) > 0


class TestVcrWikiLinks:
    """Test wiki.links() method."""

    @pytest.mark.vcr
    def test_links(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        links = sync_wiki.links(page)
        assert isinstance(links, dict)
        assert len(links) > 0


class TestVcrWikiBacklinks:
    """Test wiki.backlinks() method."""

    @pytest.mark.vcr
    def test_backlinks(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        bl = sync_wiki.backlinks(page)
        assert isinstance(bl, dict)
        assert len(bl) > 0


class TestVcrWikiCategories:
    """Test wiki.categories() method."""

    @pytest.mark.vcr
    def test_categories(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        cats = sync_wiki.categories(page)
        assert isinstance(cats, dict)
        assert len(cats) > 0


class TestVcrWikiCategorymembers:
    """Test wiki.categorymembers() method."""

    @pytest.mark.vcr
    def test_categorymembers(self, sync_wiki):
        page = sync_wiki.page("Category:Physics")
        members = sync_wiki.categorymembers(page)
        assert isinstance(members, dict)
        assert len(members) > 0


class TestVcrWikiCoordinates:
    """Test wiki.coordinates() with various parameter values."""

    @pytest.mark.vcr
    def test_default(self, sync_wiki):
        page = sync_wiki.page("London")
        coords = sync_wiki.coordinates(page)
        assert isinstance(coords, list)
        assert len(coords) > 0
        assert isinstance(coords[0], wikipediaapi.Coordinate)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "primary",
        [CoordinateType.PRIMARY, CoordinateType.SECONDARY, CoordinateType.ALL],
        ids=["primary", "secondary", "all"],
    )
    def test_primary(self, sync_wiki, primary):
        page = sync_wiki.page("London")
        coords = sync_wiki.coordinates(page, primary=primary)
        assert isinstance(coords, list)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "prop",
        [
            CoordinatesProp.COUNTRY,
            CoordinatesProp.DIM,
            CoordinatesProp.GLOBE,
            CoordinatesProp.NAME,
            CoordinatesProp.REGION,
            CoordinatesProp.TYPE,
        ],
        ids=["country", "dim", "globe", "name", "region", "type"],
    )
    def test_prop(self, sync_wiki, prop):
        page = sync_wiki.page("London")
        coords = sync_wiki.coordinates(page, prop=[prop])
        assert isinstance(coords, list)

    @pytest.mark.vcr
    def test_distance_from_point(self, sync_wiki):
        page = sync_wiki.page("London")
        coords = sync_wiki.coordinates(page, distance_from_point=GeoPoint(51.5074, -0.1278))
        assert isinstance(coords, list)

    @pytest.mark.vcr
    def test_distance_from_page(self, sync_wiki):
        page = sync_wiki.page("London")
        ref_page = sync_wiki.page("Paris")
        coords = sync_wiki.coordinates(page, distance_from_page=ref_page)
        assert isinstance(coords, list)


class TestVcrWikiBatchCoordinates:
    """Test wiki.batch_coordinates() method."""

    @pytest.mark.vcr
    def test_batch_coordinates(self, sync_wiki):
        pages = [sync_wiki.page("London"), sync_wiki.page("Paris")]
        result = sync_wiki.batch_coordinates(pages)
        assert isinstance(result, dict)
        assert len(result) > 0


class TestVcrWikiImages:
    """Test wiki.images() with various parameter values."""

    @pytest.mark.vcr
    def test_default(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        imgs = sync_wiki.images(page)
        assert isinstance(imgs, wikipediaapi.PagesDict)
        assert len(imgs) > 0

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "direction",
        [Direction.ASCENDING, Direction.DESCENDING],
        ids=["ascending", "descending"],
    )
    def test_direction(self, sync_wiki, direction):
        page = sync_wiki.page("Python_(programming_language)")
        imgs = sync_wiki.images(page, direction=direction)
        assert isinstance(imgs, wikipediaapi.PagesDict)

    @pytest.mark.vcr
    def test_limit(self, sync_wiki):
        page = sync_wiki.page("Python_(programming_language)")
        imgs = sync_wiki.images(page, limit=3)
        assert isinstance(imgs, wikipediaapi.PagesDict)


class TestVcrWikiBatchImages:
    """Test wiki.batch_images() method."""

    @pytest.mark.vcr
    def test_batch_images(self, sync_wiki):
        pages = [
            sync_wiki.page("Earth"),
            sync_wiki.page("Python_(programming_language)"),
        ]
        result = sync_wiki.batch_images(pages)
        assert isinstance(result, dict)
        assert len(result) > 0


class TestVcrWikiGeosearch:
    """Test wiki.geosearch() with various parameter values."""

    @pytest.mark.vcr
    def test_coord(self, sync_wiki):
        results = sync_wiki.geosearch(coord=GeoPoint(51.5074, -0.1278), limit=5)
        assert isinstance(results, wikipediaapi.PagesDict)
        assert len(results) > 0

    @pytest.mark.vcr
    def test_page(self, sync_wiki):
        page = sync_wiki.page("London")
        results = sync_wiki.geosearch(page=page, limit=5)
        assert isinstance(results, wikipediaapi.PagesDict)
        assert len(results) > 0

    @pytest.mark.vcr
    def test_bbox(self, sync_wiki):
        results = sync_wiki.geosearch(
            bbox=GeoBox(
                top_left=GeoPoint(51.52, -0.15),
                bottom_right=GeoPoint(51.50, -0.10),
            ),
            limit=5,
        )
        assert isinstance(results, wikipediaapi.PagesDict)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "sort",
        [GeoSearchSort.DISTANCE, GeoSearchSort.RELEVANCE],
        ids=["distance", "relevance"],
    )
    def test_sort(self, sync_wiki, sort):
        results = sync_wiki.geosearch(coord=GeoPoint(51.5074, -0.1278), sort=sort, limit=5)
        assert isinstance(results, wikipediaapi.PagesDict)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "ns",
        [Namespace.MAIN, Namespace.CATEGORY, Namespace.FILE, Namespace.USER],
        ids=["main", "category", "file", "user"],
    )
    def test_namespace(self, sync_wiki, ns):
        results = sync_wiki.geosearch(coord=GeoPoint(51.5074, -0.1278), ns=ns, limit=5)
        assert isinstance(results, wikipediaapi.PagesDict)

    @pytest.mark.vcr
    def test_radius(self, sync_wiki):
        results = sync_wiki.geosearch(coord=GeoPoint(51.5074, -0.1278), radius=1000, limit=5)
        assert isinstance(results, wikipediaapi.PagesDict)

    @pytest.mark.vcr
    def test_prop_and_primary(self, sync_wiki):
        results = sync_wiki.geosearch(
            coord=GeoPoint(51.5074, -0.1278),
            prop=[CoordinatesProp.GLOBE, CoordinatesProp.COUNTRY],
            primary=CoordinateType.ALL,
            limit=5,
        )
        assert isinstance(results, wikipediaapi.PagesDict)


class TestVcrWikiRandom:
    """Test wiki.random() with various parameter values."""

    @pytest.mark.vcr
    def test_default(self, sync_wiki):
        results = sync_wiki.random()
        assert isinstance(results, wikipediaapi.PagesDict)
        assert len(results) >= 1

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "filter_redirect",
        [
            RedirectFilter.ALL,
            RedirectFilter.NONREDIRECTS,
            RedirectFilter.REDIRECTS,
        ],
        ids=["all", "nonredirects", "redirects"],
    )
    def test_filter_redirect(self, sync_wiki, filter_redirect):
        results = sync_wiki.random(filter_redirect=filter_redirect, limit=3)
        assert isinstance(results, wikipediaapi.PagesDict)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "ns",
        [Namespace.MAIN, Namespace.CATEGORY],
        ids=["main", "category"],
    )
    def test_namespace(self, sync_wiki, ns):
        results = sync_wiki.random(ns=ns, limit=3)
        assert isinstance(results, wikipediaapi.PagesDict)

    @pytest.mark.vcr
    def test_limit(self, sync_wiki):
        results = sync_wiki.random(limit=5)
        assert isinstance(results, wikipediaapi.PagesDict)
        assert len(results) == 5


class TestVcrWikiSearch:
    """Test wiki.search() with various parameter values."""

    @pytest.mark.vcr
    def test_default(self, sync_wiki):
        results = sync_wiki.search("Python programming")
        assert isinstance(results, wikipediaapi.SearchResults)
        assert len(results.pages) > 0

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "what",
        [SearchWhat.TEXT, SearchWhat.TITLE, SearchWhat.NEAR_MATCH],
        ids=["text", "title", "near_match"],
    )
    def test_what(self, sync_wiki, what):
        results = sync_wiki.search("Python programming", what=what)
        assert isinstance(results, wikipediaapi.SearchResults)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "sort",
        [
            SearchSort.RELEVANCE,
            SearchSort.CREATE_TIMESTAMP_DESC,
            SearchSort.LAST_EDIT_DESC,
            SearchSort.NONE,
        ],
        ids=["relevance", "create_timestamp_desc", "last_edit_desc", "none"],
    )
    def test_sort(self, sync_wiki, sort):
        results = sync_wiki.search("Python programming", sort=sort)
        assert isinstance(results, wikipediaapi.SearchResults)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "info_val",
        [
            SearchInfo.TOTAL_HITS,
            SearchInfo.SUGGESTION,
            SearchInfo.REWRITTEN_QUERY,
        ],
        ids=["totalhits", "suggestion", "rewrittenquery"],
    )
    def test_info(self, sync_wiki, info_val):
        results = sync_wiki.search("Python programming", info=[info_val])
        assert isinstance(results, wikipediaapi.SearchResults)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "prop_val",
        [
            SearchProp.SIZE,
            SearchProp.WORDCOUNT,
            SearchProp.TIMESTAMP,
            SearchProp.SNIPPET,
        ],
        ids=["size", "wordcount", "timestamp", "snippet"],
    )
    def test_prop(self, sync_wiki, prop_val):
        results = sync_wiki.search("Python programming", prop=[prop_val])
        assert isinstance(results, wikipediaapi.SearchResults)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "ns",
        [Namespace.MAIN, Namespace.CATEGORY, Namespace.FILE, Namespace.USER],
        ids=["main", "category", "file", "user"],
    )
    def test_namespace(self, sync_wiki, ns):
        results = sync_wiki.search("Python programming", ns=ns)
        assert isinstance(results, wikipediaapi.SearchResults)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "qi_profile",
        [SearchQiProfile.ENGINE_AUTO_SELECT, SearchQiProfile.CLASSIC],
        ids=["engine_autoselect", "classic"],
    )
    def test_qi_profile(self, sync_wiki, qi_profile):
        results = sync_wiki.search("Python programming", qi_profile=qi_profile)
        assert isinstance(results, wikipediaapi.SearchResults)

    @pytest.mark.vcr
    def test_interwiki(self, sync_wiki):
        results = sync_wiki.search("Python programming", interwiki=True)
        assert isinstance(results, wikipediaapi.SearchResults)

    @pytest.mark.vcr
    def test_enable_rewrites(self, sync_wiki):
        results = sync_wiki.search("Python programming", enable_rewrites=True)
        assert isinstance(results, wikipediaapi.SearchResults)

    @pytest.mark.vcr
    def test_limit(self, sync_wiki):
        results = sync_wiki.search("Python programming", limit=3)
        assert isinstance(results, wikipediaapi.SearchResults)
        assert len(results.pages) <= 3
