"""Integration tests for AsyncWikipediaResource methods using VCR cassettes."""

import pytest

import wikipediaapi
from wikipediaapi import (
    CoordinatesProp,
    CoordinateType,
    Direction,
    GeoBox,
    GeoPoint,
    GeoSearchSort,
    Namespace,
    RedirectFilter,
    SearchInfo,
    SearchProp,
    SearchQiProfile,
    SearchSort,
    SearchWhat,
)


class TestVcrAsyncWikiConstruction:
    """Test page/article/pages construction (no API calls)."""

    def test_page(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        assert isinstance(page, wikipediaapi.AsyncWikipediaPage)
        assert page.title == "Python_(programming_language)"

    def test_article(self, async_wiki):
        page = async_wiki.article("Python_(programming_language)")
        assert isinstance(page, wikipediaapi.AsyncWikipediaPage)
        assert page.title == "Python_(programming_language)"

    @pytest.mark.vcr
    async def test_pages(self, async_wiki):
        pages = await async_wiki.pages(["Earth", "Python_(programming_language)"])
        assert isinstance(pages, wikipediaapi.AsyncPagesDict)
        assert len(pages) == 2
        assert "Earth" in pages
        assert "Python_(programming_language)" in pages

    def test_page_with_namespace(self, async_wiki):
        page = async_wiki.page("Physics", ns=Namespace.CATEGORY)
        assert page.ns == Namespace.CATEGORY

    def test_page_with_unquote(self, async_wiki):
        page = async_wiki.page("Python_%28programming_language%29", unquote=True)
        assert page.title == "Python_(programming_language)"


class TestVcrAsyncWikiExtracts:
    """Test wiki.extracts() method."""

    @pytest.mark.vcr
    async def test_extracts(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        result = await async_wiki.extracts(page)
        assert isinstance(result, str)
        assert "Python" in result


class TestVcrAsyncWikiInfo:
    """Test wiki.info() method."""

    @pytest.mark.vcr
    async def test_info(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        result = await async_wiki.info(page)
        assert result is page
        pageid = await page.pageid
        assert pageid > 0
        assert await page.pagelanguage == "en"


class TestVcrAsyncWikiLanglinks:
    """Test wiki.langlinks() method."""

    @pytest.mark.vcr
    async def test_langlinks(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        ll = await async_wiki.langlinks(page)
        assert isinstance(ll, dict)
        assert len(ll) > 0


class TestVcrAsyncWikiLinks:
    """Test wiki.links() method."""

    @pytest.mark.vcr
    async def test_links(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        links = await async_wiki.links(page)
        assert isinstance(links, dict)
        assert len(links) > 0


class TestVcrAsyncWikiBacklinks:
    """Test wiki.backlinks() method."""

    @pytest.mark.vcr
    async def test_backlinks(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        bl = await async_wiki.backlinks(page)
        assert isinstance(bl, dict)
        assert len(bl) > 0


class TestVcrAsyncWikiCategories:
    """Test wiki.categories() method."""

    @pytest.mark.vcr
    async def test_categories(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        cats = await async_wiki.categories(page)
        assert isinstance(cats, dict)
        assert len(cats) > 0


class TestVcrAsyncWikiCategorymembers:
    """Test wiki.categorymembers() method."""

    @pytest.mark.vcr
    async def test_categorymembers(self, async_wiki):
        page = async_wiki.page("Category:Physics")
        members = await async_wiki.categorymembers(page)
        assert isinstance(members, dict)
        assert len(members) > 0


class TestVcrAsyncWikiCoordinates:
    """Test wiki.coordinates() with various parameter values."""

    @pytest.mark.vcr
    async def test_default(self, async_wiki):
        page = async_wiki.page("London")
        coords = await async_wiki.coordinates(page)
        assert isinstance(coords, list)
        assert len(coords) > 0
        assert isinstance(coords[0], wikipediaapi.Coordinate)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "primary",
        [CoordinateType.PRIMARY, CoordinateType.SECONDARY, CoordinateType.ALL],
        ids=["primary", "secondary", "all"],
    )
    async def test_primary(self, async_wiki, primary):
        page = async_wiki.page("London")
        coords = await async_wiki.coordinates(page, primary=primary)
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
    async def test_prop(self, async_wiki, prop):
        page = async_wiki.page("London")
        coords = await async_wiki.coordinates(page, prop=[prop])
        assert isinstance(coords, list)

    @pytest.mark.vcr
    async def test_distance_from_point(self, async_wiki):
        page = async_wiki.page("London")
        coords = await async_wiki.coordinates(page, distance_from_point=GeoPoint(51.5074, -0.1278))
        assert isinstance(coords, list)

    @pytest.mark.vcr
    async def test_distance_from_page(self, async_wiki):
        page = async_wiki.page("London")
        ref_page = async_wiki.page("Paris")
        coords = await async_wiki.coordinates(page, distance_from_page=ref_page)
        assert isinstance(coords, list)


class TestVcrAsyncWikiBatchCoordinates:
    """Test wiki.batch_coordinates() method."""

    @pytest.mark.vcr
    async def test_batch_coordinates(self, async_wiki):
        pages = [async_wiki.page("London"), async_wiki.page("Paris")]
        result = await async_wiki.batch_coordinates(pages)
        assert isinstance(result, dict)
        assert len(result) > 0


class TestVcrAsyncWikiImages:
    """Test wiki.images() with various parameter values."""

    @pytest.mark.vcr
    async def test_default(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        imgs = await async_wiki.images(page)
        assert isinstance(imgs, dict)
        assert len(imgs) > 0

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "direction",
        [Direction.ASCENDING, Direction.DESCENDING],
        ids=["ascending", "descending"],
    )
    async def test_direction(self, async_wiki, direction):
        page = async_wiki.page("Python_(programming_language)")
        imgs = await async_wiki.images(page, direction=direction)
        assert isinstance(imgs, dict)

    @pytest.mark.vcr
    async def test_limit(self, async_wiki):
        page = async_wiki.page("Python_(programming_language)")
        imgs = await async_wiki.images(page, limit=3)
        assert isinstance(imgs, dict)


class TestVcrAsyncWikiBatchImages:
    """Test wiki.batch_images() method."""

    @pytest.mark.vcr
    async def test_batch_images(self, async_wiki):
        pages = [
            async_wiki.page("Earth"),
            async_wiki.page("Python_(programming_language)"),
        ]
        result = await async_wiki.batch_images(pages)
        assert isinstance(result, dict)
        assert len(result) > 0


class TestVcrAsyncWikiGeosearch:
    """Test wiki.geosearch() with various parameter values."""

    @pytest.mark.vcr
    async def test_coord(self, async_wiki):
        results = await async_wiki.geosearch(coord=GeoPoint(51.5074, -0.1278), limit=5)
        assert isinstance(results, wikipediaapi.AsyncPagesDict)
        assert len(results) > 0

    @pytest.mark.vcr
    async def test_page(self, async_wiki):
        page = async_wiki.page("London")
        results = await async_wiki.geosearch(page=page, limit=5)
        assert isinstance(results, wikipediaapi.AsyncPagesDict)
        assert len(results) > 0

    @pytest.mark.vcr
    async def test_bbox(self, async_wiki):
        results = await async_wiki.geosearch(
            bbox=GeoBox(
                top_left=GeoPoint(51.52, -0.15),
                bottom_right=GeoPoint(51.50, -0.10),
            ),
            limit=5,
        )
        assert isinstance(results, wikipediaapi.AsyncPagesDict)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "sort",
        [GeoSearchSort.DISTANCE, GeoSearchSort.RELEVANCE],
        ids=["distance", "relevance"],
    )
    async def test_sort(self, async_wiki, sort):
        results = await async_wiki.geosearch(coord=GeoPoint(51.5074, -0.1278), sort=sort, limit=5)
        assert isinstance(results, wikipediaapi.AsyncPagesDict)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "ns",
        [Namespace.MAIN, Namespace.CATEGORY, Namespace.FILE, Namespace.USER],
        ids=["main", "category", "file", "user"],
    )
    async def test_namespace(self, async_wiki, ns):
        results = await async_wiki.geosearch(coord=GeoPoint(51.5074, -0.1278), ns=ns, limit=5)
        assert isinstance(results, wikipediaapi.AsyncPagesDict)

    @pytest.mark.vcr
    async def test_radius(self, async_wiki):
        results = await async_wiki.geosearch(coord=GeoPoint(51.5074, -0.1278), radius=1000, limit=5)
        assert isinstance(results, wikipediaapi.AsyncPagesDict)

    @pytest.mark.vcr
    async def test_prop_and_primary(self, async_wiki):
        results = await async_wiki.geosearch(
            coord=GeoPoint(51.5074, -0.1278),
            prop=[CoordinatesProp.GLOBE, CoordinatesProp.COUNTRY],
            primary=CoordinateType.ALL,
            limit=5,
        )
        assert isinstance(results, wikipediaapi.AsyncPagesDict)


class TestVcrAsyncWikiRandom:
    """Test wiki.random() with various parameter values."""

    @pytest.mark.vcr
    async def test_default(self, async_wiki):
        results = await async_wiki.random()
        assert isinstance(results, wikipediaapi.AsyncPagesDict)
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
    async def test_filter_redirect(self, async_wiki, filter_redirect):
        results = await async_wiki.random(filter_redirect=filter_redirect, limit=3)
        assert isinstance(results, wikipediaapi.AsyncPagesDict)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "ns",
        [Namespace.MAIN, Namespace.CATEGORY],
        ids=["main", "category"],
    )
    async def test_namespace(self, async_wiki, ns):
        results = await async_wiki.random(ns=ns, limit=3)
        assert isinstance(results, wikipediaapi.AsyncPagesDict)

    @pytest.mark.vcr
    async def test_limit(self, async_wiki):
        results = await async_wiki.random(limit=5)
        assert isinstance(results, wikipediaapi.AsyncPagesDict)
        assert len(results) == 5


class TestVcrAsyncWikiSearch:
    """Test wiki.search() with various parameter values."""

    @pytest.mark.vcr
    async def test_default(self, async_wiki):
        results = await async_wiki.search("Python programming")
        assert isinstance(results, wikipediaapi.SearchResults)
        assert len(results.pages) > 0

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "what",
        [SearchWhat.TEXT, SearchWhat.TITLE, SearchWhat.NEAR_MATCH],
        ids=["text", "title", "near_match"],
    )
    async def test_what(self, async_wiki, what):
        results = await async_wiki.search("Python programming", what=what)
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
    async def test_sort(self, async_wiki, sort):
        results = await async_wiki.search("Python programming", sort=sort)
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
    async def test_info(self, async_wiki, info_val):
        results = await async_wiki.search("Python programming", info=[info_val])
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
    async def test_prop(self, async_wiki, prop_val):
        results = await async_wiki.search("Python programming", prop=[prop_val])
        assert isinstance(results, wikipediaapi.SearchResults)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "ns",
        [Namespace.MAIN, Namespace.CATEGORY, Namespace.FILE, Namespace.USER],
        ids=["main", "category", "file", "user"],
    )
    async def test_namespace(self, async_wiki, ns):
        results = await async_wiki.search("Python programming", ns=ns)
        assert isinstance(results, wikipediaapi.SearchResults)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "qi_profile",
        [SearchQiProfile.ENGINE_AUTO_SELECT, SearchQiProfile.CLASSIC],
        ids=["engine_autoselect", "classic"],
    )
    async def test_qi_profile(self, async_wiki, qi_profile):
        results = await async_wiki.search("Python programming", qi_profile=qi_profile)
        assert isinstance(results, wikipediaapi.SearchResults)

    @pytest.mark.vcr
    async def test_interwiki(self, async_wiki):
        results = await async_wiki.search("Python programming", interwiki=True)
        assert isinstance(results, wikipediaapi.SearchResults)

    @pytest.mark.vcr
    async def test_enable_rewrites(self, async_wiki):
        results = await async_wiki.search("Python programming", enable_rewrites=True)
        assert isinstance(results, wikipediaapi.SearchResults)

    @pytest.mark.vcr
    async def test_limit(self, async_wiki):
        results = await async_wiki.search("Python programming", limit=3)
        assert isinstance(results, wikipediaapi.SearchResults)
        assert len(results.pages) <= 3
