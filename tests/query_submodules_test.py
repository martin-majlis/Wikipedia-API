# flake8: noqa
import pytest

from tests.mock_data import async_wikipedia_api_request
from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi
from wikipediaapi._base_wikipedia_page import _Sentinel
from wikipediaapi._base_wikipedia_page import NOT_CACHED
from wikipediaapi._enums import Direction
from wikipediaapi._params import CoordinatesParams
from wikipediaapi._params import GeoSearchParams
from wikipediaapi._params import ImagesParams
from wikipediaapi._params import RandomParams
from wikipediaapi._params import SearchParams
from wikipediaapi._types import GeoBox
from wikipediaapi._types import GeoPoint


class TestCoordinates:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_coordinates_default(self):
        page = self.wiki.page("Test_1")
        coords = self.wiki.coordinates(page)
        assert len(coords) == 1
        assert coords[0].lat == 51.5074
        assert coords[0].lon == -0.1278
        assert coords[0].primary is True
        assert coords[0].globe == "earth"

    def test_coordinates_primary_all(self):
        page = self.wiki.page("Test_1")
        coords = self.wiki.coordinates(page, primary="all")
        assert len(coords) == 2
        assert coords[0].lat == 51.5074
        assert coords[1].lat == 48.8566

    def test_coordinates_nonexistent_page(self):
        page = self.wiki.page("NonExistent")
        coords = self.wiki.coordinates(page)
        assert coords == []

    def test_coordinates_cached(self):
        page = self.wiki.page("Test_1")
        coords1 = self.wiki.coordinates(page)
        coords2 = self.wiki.coordinates(page)
        assert coords1 is coords2

    def test_coordinates_per_param_cache(self):
        page1 = self.wiki.page("Test_1")
        page2 = self.wiki.page("Test_1")
        coords_default = self.wiki.coordinates(page1)
        coords_all = self.wiki.coordinates(page2, primary="all")
        assert len(coords_default) == 1
        assert len(coords_all) == 2

    def test_coordinates_with_iterable_prop(self):
        page = self.wiki.page("Test_1")
        coords = self.wiki.coordinates(page, prop=["globe"])
        assert len(coords) == 1

    def test_page_coordinates_property(self):
        page = self.wiki.page("Test_1")
        coords = page.coordinates
        assert len(coords) == 1
        assert coords[0].lat == 51.5074

    def test_page_coordinates_property_cached(self):
        page = self.wiki.page("Test_1")
        _ = page.coordinates
        coords = page.coordinates
        assert len(coords) == 1


class TestImages:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_images_default(self):
        page = self.wiki.page("Test_1")
        imgs = self.wiki.images(page)
        assert isinstance(imgs, wikipediaapi.PagesDict)
        assert len(imgs) == 2
        assert "File:Example.png" in imgs
        assert "File:Logo.svg" in imgs

    def test_images_nonexistent_page(self):
        page = self.wiki.page("NonExistent")
        imgs = self.wiki.images(page)
        assert len(imgs) == 0

    def test_images_cached(self):
        page = self.wiki.page("Test_1")
        imgs1 = self.wiki.images(page)
        imgs2 = self.wiki.images(page)
        assert imgs1 is imgs2

    def test_page_images_property(self):
        page = self.wiki.page("Test_1")
        imgs = page.images
        assert isinstance(imgs, wikipediaapi.PagesDict)
        assert len(imgs) == 2


class TestGeoSearch:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_geosearch(self):
        # Test geosearch using a page as the center point
        center_page = self.wiki.page("Test_1")
        results = self.wiki.geosearch(page=center_page)
        assert isinstance(results, wikipediaapi.PagesDict)
        assert len(results) == 2
        assert "Nearby Page 1" in results
        assert "Nearby Page 2" in results

    def test_geosearch_with_coordinates(self):
        # Test geosearch using direct coordinates (alternative to page-based)
        results = self.wiki.geosearch(coord=GeoPoint(51.5074, -0.1278))
        assert isinstance(results, wikipediaapi.PagesDict)
        assert len(results) == 2
        assert "Nearby Page 1" in results
        assert "Nearby Page 2" in results

    def test_geosearch_meta(self):
        # Test geosearch metadata using page as center
        center_page = self.wiki.page("Test_1")
        results = self.wiki.geosearch(page=center_page)
        p1 = results["Nearby Page 1"]
        assert p1.geosearch_meta is not None
        assert p1.geosearch_meta.dist == 50.3
        assert p1.geosearch_meta.lat == 51.508
        assert p1.geosearch_meta.primary is True

    def test_geosearch_precaches_coordinates(self):
        # Test that geosearch precaches coordinates using page as center
        center_page = self.wiki.page("Test_1")
        results = self.wiki.geosearch(page=center_page)
        p1 = results["Nearby Page 1"]
        default_key = CoordinatesParams().cache_key()
        cached = p1._get_cached("coordinates", default_key)
        assert not isinstance(cached, type(NOT_CACHED))
        assert len(cached) == 1
        assert cached[0].lat == 51.508

    def test_geosearch_pageid_preset(self):
        # Test pageid preset using page as center
        center_page = self.wiki.page("Test_1")
        results = self.wiki.geosearch(page=center_page)
        p1 = results["Nearby Page 1"]
        assert p1._attributes["pageid"] == 100


class TestRandom:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_random(self):
        results = self.wiki.random(limit=2)
        assert isinstance(results, wikipediaapi.PagesDict)
        assert len(results) == 2
        assert "Random Page A" in results
        assert "Random Page B" in results

    def test_random_pageid_preset(self):
        results = self.wiki.random(limit=2)
        assert results["Random Page A"]._attributes["pageid"] == 200
        assert results["Random Page B"]._attributes["pageid"] == 201


class TestSearch:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_search(self):
        results = self.wiki.search("Python")
        assert isinstance(results, wikipediaapi.SearchResults)
        assert len(results.pages) == 2
        assert "Python (programming language)" in results.pages
        assert "Python (mythology)" in results.pages

    def test_search_totalhits(self):
        results = self.wiki.search("Python")
        assert results.totalhits == 5432

    def test_search_suggestion(self):
        results = self.wiki.search("Python")
        assert results.suggestion == "python programming"

    def test_search_meta(self):
        results = self.wiki.search("Python")
        p = results.pages["Python (programming language)"]
        assert p.search_meta is not None
        assert p.search_meta.size == 123456
        assert p.search_meta.wordcount == 15000
        assert "Python" in p.search_meta.snippet
        assert p.search_meta.timestamp == "2024-01-01T00:00:00Z"

    def test_search_pageid_preset(self):
        results = self.wiki.search("Python")
        p = results.pages["Python (programming language)"]
        assert p._attributes["pageid"] == 300


class TestPages:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_pages_creates_pages_dict(self):
        pd = self.wiki.pages(["Test_1", "NonExistent"])
        assert isinstance(pd, wikipediaapi.PagesDict)
        assert len(pd) == 2
        assert "Test_1" in pd
        assert "NonExistent" in pd

    def test_pages_lazy(self):
        pd = self.wiki.pages(["Test_1"])
        page = pd["Test_1"]
        assert any(page._called.values()) is False


class TestParamCache:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_get_cached_miss(self):
        page = self.wiki.page("Test_1")
        result = page._get_cached("coordinates", CoordinatesParams().cache_key())
        assert result is NOT_CACHED

    def test_set_and_get_cached(self):
        page = self.wiki.page("Test_1")
        key = CoordinatesParams().cache_key()
        page._set_cached("coordinates", key, ["test_value"])
        result = page._get_cached("coordinates", key)
        assert result == ["test_value"]

    def test_different_params_different_cache(self):
        page = self.wiki.page("Test_1")
        key1 = CoordinatesParams().cache_key()
        key2 = CoordinatesParams(primary="all").cache_key()
        assert key1 != key2
        page._set_cached("coordinates", key1, ["default"])
        page._set_cached("coordinates", key2, ["all"])
        assert page._get_cached("coordinates", key1) == ["default"]
        assert page._get_cached("coordinates", key2) == ["all"]


class TestParamsToApi:
    def test_coordinates_params(self):
        p = CoordinatesParams()
        api = p.to_api()
        assert api["colimit"] == "10"
        assert api["coprimary"] == "primary"
        assert api["coprop"] == "globe"
        assert "codistancefrompoint" not in api

    def test_coordinates_params_with_distance(self):
        p = CoordinatesParams(distance_from_point=GeoPoint(37.787, -122.4))
        api = p.to_api()
        assert api["codistancefrompoint"] == "37.787|-122.4"

    def test_images_params(self):
        p = ImagesParams()
        api = p.to_api()
        assert api["imlimit"] == "10"
        assert api["imdir"] == "ascending"
        assert "imimages" not in api

    def test_coordinates_params_with_iterable_prop(self):
        p = CoordinatesParams(prop=["name", "globe"])
        api = p.to_api()
        assert api["coprop"] == "name|globe"

    def test_images_params_with_iterable_images(self):
        p = ImagesParams(images=["File:Test.png", "File:Logo.svg"])
        api = p.to_api()
        assert api["imimages"] == "File:Test.png|File:Logo.svg"

    def test_coordinates_params_rejects_string_prop(self):
        with pytest.raises(TypeError):
            CoordinatesParams(prop="globe")

    def test_images_params_rejects_string_images(self):
        with pytest.raises(TypeError):
            ImagesParams(images="File:Test.png")

    def test_geosearch_params_rejects_string_prop(self):
        with pytest.raises(TypeError):
            GeoSearchParams(coord=GeoPoint(51.5, -0.1), prop="name|country")

    def test_geosearch_params_rejects_string_coord(self):
        with pytest.raises(TypeError):
            GeoSearchParams(coord="51.5|-0.1")

    def test_geosearch_params_rejects_string_bbox(self):
        with pytest.raises(TypeError):
            GeoSearchParams(bbox="52.0|-1.0|51.0|0.0")

    def test_coordinates_params_rejects_string_distance_from_point(self):
        with pytest.raises(TypeError):
            CoordinatesParams(distance_from_point="37.787|-122.4")

    def test_search_params_rejects_string_prop(self):
        with pytest.raises(TypeError):
            SearchParams(query="test", prop="size|wordcount")

    def test_search_params_rejects_string_info(self):
        with pytest.raises(TypeError):
            SearchParams(query="test", info="totalhits|suggestion")

    def test_cache_key_is_hashable(self):
        p = CoordinatesParams()
        key = p.cache_key()
        assert isinstance(key, tuple)
        d = {key: "test"}
        assert d[key] == "test"


class TestTypes:
    def test_coordinate_frozen(self):
        c = wikipediaapi.Coordinate(lat=1.0, lon=2.0, primary=True)
        with pytest.raises(AttributeError):
            c.lat = 3.0  # type: ignore[misc]

    def test_geosearch_meta_frozen(self):
        m = wikipediaapi.GeoSearchMeta(dist=10.0, lat=1.0, lon=2.0, primary=True)
        with pytest.raises(AttributeError):
            m.dist = 20.0  # type: ignore[misc]

    def test_search_meta_frozen(self):
        m = wikipediaapi.SearchMeta(snippet="test", size=100, wordcount=10, timestamp="2024-01-01")
        with pytest.raises(AttributeError):
            m.snippet = "new"  # type: ignore[misc]

    def test_geo_point_defaults(self):
        point = wikipediaapi.GeoPoint()
        assert point.lat == 0.0
        assert point.lon == 0.0

    def test_geo_point_validation(self):
        with pytest.raises(ValueError):
            wikipediaapi.GeoPoint(100.0, 0.0)
        with pytest.raises(ValueError):
            wikipediaapi.GeoPoint(0.0, 200.0)

    def test_geo_box_defaults(self):
        box = wikipediaapi.GeoBox()
        assert box.top_left == wikipediaapi.GeoPoint(0.0, 0.0)
        assert box.bottom_right == wikipediaapi.GeoPoint(0.0, 0.0)

    def test_geo_box_validation(self):
        with pytest.raises(ValueError):
            wikipediaapi.GeoBox(
                top_left=wikipediaapi.GeoPoint(10.0, 0.0),
                bottom_right=wikipediaapi.GeoPoint(20.0, 1.0),
            )
        with pytest.raises(ValueError):
            wikipediaapi.GeoBox(
                top_left=wikipediaapi.GeoPoint(20.0, 5.0),
                bottom_right=wikipediaapi.GeoPoint(10.0, 4.0),
            )


class TestPagesDictClass:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_pages_dict_is_dict(self):
        pd = wikipediaapi.PagesDict()
        assert isinstance(pd, dict)

    def test_pages_dict_with_data(self):
        page = self.wiki.page("Test_1")
        pd = wikipediaapi.PagesDict(wiki=self.wiki, data={"Test_1": page})
        assert len(pd) == 1
        assert "Test_1" in pd

    def test_pages_dict_backward_compatible(self):
        pd = wikipediaapi.PagesDict()
        pd["key"] = "value"
        assert pd["key"] == "value"


class TestSentinel:
    def test_repr(self):
        assert repr(NOT_CACHED) == "<NOT_CACHED>"

    def test_bool(self):
        assert bool(NOT_CACHED) is False

    def test_singleton(self):
        s1 = _Sentinel()
        s2 = _Sentinel()
        assert s1 is s2


class TestBasePageGetattr:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_private_attr_raises(self):
        page = self.wiki.page("Test_1")
        with pytest.raises(AttributeError):
            _ = page._nonexistent_private

    def test_missing_attr_raises(self):
        page = self.wiki.page("Test_1")
        # Force info fetch so __getattr__ doesn't trigger lazy fetch
        page._called["info"] = True
        with pytest.raises(AttributeError):
            _ = page.totally_nonexistent_attr


class TestBatchCoordinates:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_batch_coordinates(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        result = self.wiki.batch_coordinates([p1, p2])
        assert p1 in result
        assert len(result[p1]) == 1
        assert result[p1][0].lat == 51.5074
        # NonExistent should have empty list
        assert p2 in result
        assert result[p2] == []


class TestBatchImages:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_batch_images(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        result = self.wiki.batch_images([p1, p2])
        assert "Test 1" in result
        assert len(result["Test 1"]) == 2
        assert "File:Example.png" in result["Test 1"]
        # NonExistent should have empty PagesDict
        assert "NonExistent" in result
        assert len(result["NonExistent"]) == 0


class TestPagesDictBatchMethods:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_pages_dict_coordinates(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        pd = wikipediaapi.PagesDict(wiki=self.wiki, data={"Test_1": p1, "NonExistent": p2})
        result = pd.coordinates()
        assert p1 in result
        assert len(result[p1]) == 1

    def test_pages_dict_images(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        pd = wikipediaapi.PagesDict(wiki=self.wiki, data={"Test_1": p1, "NonExistent": p2})
        result = pd.images()
        assert "Test 1" in result
        assert len(result["Test 1"]) == 2


class TestParamsToApiExtended:
    def test_geosearch_params(self):
        p = GeoSearchParams(coord=GeoPoint(51.5, -0.1))
        api = p.to_api()
        assert api["gscoord"] == "51.5|-0.1"
        assert api["gsradius"] == "500"

    def test_random_params(self):
        p = RandomParams(limit=5)
        api = p.to_api()
        assert api["rnlimit"] == "5"

    def test_search_params(self):
        p = SearchParams(query="test", namespace=wikipediaapi.Namespace.MAIN)
        api = p.to_api()
        assert api["srsearch"] == "test"
        assert api["srnamespace"] == "0"

    def test_geosearch_params_with_iterable_prop(self):
        p = GeoSearchParams(coord=GeoPoint(51.5, -0.1), prop=["name", "country"])
        api = p.to_api()
        assert api["gsprop"] == "name|country"

    def test_geosearch_params_with_bbox(self):
        p = GeoSearchParams(
            bbox=GeoBox(top_left=GeoPoint(52.0, -1.0), bottom_right=GeoPoint(51.0, 0.0))
        )
        api = p.to_api()
        assert api["gsbbox"] == "52.0|-1.0|51.0|0.0"

    def test_search_params_with_iterable_prop_and_info(self):
        p = SearchParams(
            query="test",
            prop=["size", "wordcount"],
            info=["totalhits", "suggestion"],
        )
        api = p.to_api()
        assert api["srprop"] == "size|wordcount"
        assert api["srinfo"] == "totalhits|suggestion"

    def test_images_params_with_images(self):
        p = ImagesParams(images=["File:Test.png"], direction=Direction.DESCENDING)
        api = p.to_api()
        assert api["imimages"] == "File:Test.png"
        assert api["imdir"] == "descending"

    def test_images_params_accepts_string_direction(self):
        p = ImagesParams(direction="descending")
        api = p.to_api()
        assert api["imdir"] == "descending"

    def test_images_params_rejects_invalid_direction(self):
        with pytest.raises(TypeError):
            ImagesParams(direction=123)  # type: ignore[arg-type]


class TestAsyncPagesDictBatchMethods:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        self.wiki._get = async_wikipedia_api_request(self.wiki)

    async def test_async_pages_dict_constructor(self):
        from wikipediaapi._pages_dict import AsyncPagesDict

        p1 = self.wiki.page("Test_1")
        apd = AsyncPagesDict(wiki=self.wiki, data={"Test_1": p1})
        assert len(apd) == 1
        assert "Test_1" in apd

    async def test_async_pages_dict_coordinates(self):
        from wikipediaapi._pages_dict import AsyncPagesDict

        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        apd = AsyncPagesDict(wiki=self.wiki, data={"Test_1": p1, "NonExistent": p2})
        result = await apd.coordinates()
        assert p1 in result
        assert len(result[p1]) == 1

    async def test_async_pages_dict_images(self):
        from wikipediaapi._pages_dict import AsyncPagesDict

        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        apd = AsyncPagesDict(wiki=self.wiki, data={"Test_1": p1, "NonExistent": p2})
        result = await apd.images()
        assert "Test 1" in result
        assert len(result["Test 1"]) == 2


class TestAsyncQuerySubmodules:
    @pytest.fixture(autouse=True)
    def setup_wiki(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        self.wiki._get = async_wikipedia_api_request(self.wiki)

    async def test_async_coordinates(self):
        page = self.wiki.page("Test_1")
        coords = await self.wiki.coordinates(page)
        assert len(coords) == 1
        assert coords[0].lat == 51.5074

    async def test_async_coordinates_nonexistent(self):
        page = self.wiki.page("NonExistent")
        coords = await self.wiki.coordinates(page)
        assert coords == []

    async def test_async_coordinates_cached(self):
        page = self.wiki.page("Test_1")
        coords1 = await self.wiki.coordinates(page)
        coords2 = await self.wiki.coordinates(page)
        assert coords1 is coords2

    async def test_async_images(self):
        page = self.wiki.page("Test_1")
        imgs = await self.wiki.images(page)
        assert isinstance(imgs, wikipediaapi.PagesDict)
        assert len(imgs) == 2

    async def test_async_images_nonexistent(self):
        page = self.wiki.page("NonExistent")
        imgs = await self.wiki.images(page)
        assert len(imgs) == 0

    async def test_async_images_cached(self):
        page = self.wiki.page("Test_1")
        imgs1 = await self.wiki.images(page)
        imgs2 = await self.wiki.images(page)
        assert imgs1 is imgs2

    async def test_async_geosearch(self):
        results = await self.wiki.geosearch(coord=GeoPoint(51.5074, -0.1278))
        assert isinstance(results, wikipediaapi.PagesDict)
        assert len(results) == 2
        assert "Nearby Page 1" in results

    async def test_async_geosearch_meta(self):
        results = await self.wiki.geosearch(coord=GeoPoint(51.5074, -0.1278))
        p1 = results["Nearby Page 1"]
        assert p1.geosearch_meta is not None
        assert p1.geosearch_meta.dist == 50.3

    async def test_async_random(self):
        results = await self.wiki.random(limit=2)
        assert isinstance(results, wikipediaapi.PagesDict)
        assert len(results) == 2
        assert "Random Page A" in results

    async def test_async_search(self):
        results = await self.wiki.search("Python")
        assert isinstance(results, wikipediaapi.SearchResults)
        assert len(results.pages) == 2
        assert results.totalhits == 5432

    async def test_async_search_meta(self):
        results = await self.wiki.search("Python")
        p = results.pages["Python (programming language)"]
        assert p.search_meta is not None
        assert p.search_meta.size == 123456

    async def test_async_batch_coordinates(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        result = await self.wiki.batch_coordinates([p1, p2])
        assert p1 in result
        assert len(result[p1]) == 1

    async def test_async_batch_images(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        result = await self.wiki.batch_images([p1, p2])
        assert "Test 1" in result
        assert len(result["Test 1"]) == 2

    async def test_async_page_coordinates_property(self):
        page = self.wiki.page("Test_1")
        coords = await page.coordinates
        assert len(coords) == 1
        assert coords[0].lat == 51.5074

    async def test_async_page_images_property(self):
        page = self.wiki.page("Test_1")
        imgs = await page.images
        assert isinstance(imgs, wikipediaapi.PagesDict)
        assert len(imgs) == 2

    async def test_async_page_geosearch_meta_none(self):
        page = self.wiki.page("Test_1")
        assert page.geosearch_meta is None

    async def test_async_page_search_meta_none(self):
        page = self.wiki.page("Test_1")
        assert page.search_meta is None

    async def test_async_page_geosearch_meta_set(self):
        results = await self.wiki.geosearch(coord=GeoPoint(51.5074, -0.1278))
        p1 = results["Nearby Page 1"]
        assert p1.geosearch_meta is not None
        assert p1.geosearch_meta.dist == 50.3

    async def test_async_page_search_meta_set(self):
        results = await self.wiki.search("Python")
        p = results.pages["Python (programming language)"]
        assert p.search_meta is not None
        assert p.search_meta.size == 123456
