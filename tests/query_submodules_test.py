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
from wikipediaapi._params import ImageInfoParams
from wikipediaapi._params import ImagesParams
from wikipediaapi._params import RandomParams
from wikipediaapi._params import SearchParams
from wikipediaapi._types import GeoBox
from wikipediaapi._types import GeoPoint
from wikipediaapi._types import ImageInfo


class TestCoordinates:
    def setup_method(self):
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
    def setup_method(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_images_default(self):
        page = self.wiki.page("Test_1")
        imgs = self.wiki.images(page)
        assert isinstance(imgs, wikipediaapi.ImagesDict)
        assert len(imgs) == 2
        assert "File:Example.png" in imgs
        assert "File:Logo.svg" in imgs

    def test_images_values_are_wikipedia_image(self):
        page = self.wiki.page("Test_1")
        imgs = self.wiki.images(page)
        for img in imgs.values():
            assert isinstance(img, wikipediaapi.WikipediaImage)

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
        assert isinstance(imgs, wikipediaapi.ImagesDict)
        assert len(imgs) == 2


class TestGeoSearch:
    def setup_method(self):
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
    def setup_method(self):
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
    def setup_method(self):
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
    def setup_method(self):
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
    def setup_method(self):
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
            c.lat = 3.0  # ty: ignore[invalid-assignment]

    def test_geosearch_meta_frozen(self):
        m = wikipediaapi.GeoSearchMeta(dist=10.0, lat=1.0, lon=2.0, primary=True)
        with pytest.raises(AttributeError):
            m.dist = 20.0  # ty: ignore[invalid-assignment]

    def test_search_meta_frozen(self):
        m = wikipediaapi.SearchMeta(snippet="test", size=100, wordcount=10, timestamp="2024-01-01")
        with pytest.raises(AttributeError):
            m.snippet = "new"  # ty: ignore[invalid-assignment]

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
    def setup_method(self):
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
        pd["key"] = "value"  # ty: ignore[invalid-assignment]
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
    def setup_method(self):
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
    def setup_method(self):
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
    def setup_method(self):
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


class TestImageInfo:
    def setup_method(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def _make_image(self, title):
        return wikipediaapi.WikipediaImage(
            self.wiki,
            title=title,
            ns=6,
            language="en",
            variant=None,
        )

    def test_imageinfo_returns_list_of_imageinfo(self):
        img = self._make_image("File:Example.png")
        result = self.wiki.imageinfo(img)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ImageInfo)

    def test_imageinfo_fields_example_png(self):
        img = self._make_image("File:Example.png")
        result = self.wiki.imageinfo(img)
        info = result[0]
        assert info.timestamp == "2023-01-15T10:30:00Z"
        assert info.user == "TestUser"
        assert info.url == "https://upload.wikimedia.org/wikipedia/commons/e/example.png"
        assert info.descriptionurl == "https://commons.wikimedia.org/wiki/File:Example.png"
        assert info.descriptionshorturl == "https://commons.wikimedia.org/w/index.php?curid=12345"
        assert info.size == 102400
        assert info.width == 800
        assert info.height == 600
        assert info.sha1 == "abcdef1234567890abcdef1234567890abcdef12"
        assert info.mime == "image/png"
        assert info.mediatype == "BITMAP"

    def test_imageinfo_fields_logo_svg(self):
        img = self._make_image("File:Logo.svg")
        result = self.wiki.imageinfo(img)
        info = result[0]
        assert info.mime == "image/svg+xml"
        assert info.mediatype == "DRAWING"
        assert info.width == 200
        assert info.height == 200

    def test_imageinfo_missing_file_returns_empty_list(self):
        img = self._make_image("File:NonExistent.png")
        result = self.wiki.imageinfo(img)
        assert result == []

    def test_imageinfo_cached_returns_same_object(self):
        img = self._make_image("File:Example.png")
        result1 = self.wiki.imageinfo(img)
        result2 = self.wiki.imageinfo(img)
        assert result1 is result2

    def test_imageinfo_via_image_property(self):
        img = self._make_image("File:Example.png")
        result = img.imageinfo
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ImageInfo)

    def test_imageinfo_property_cached(self):
        img = self._make_image("File:Example.png")
        result1 = img.imageinfo
        result2 = img.imageinfo
        assert result1 is result2

    def test_imageinfo_missing_file_property_returns_empty(self):
        img = self._make_image("File:NonExistent.png")
        result = img.imageinfo
        assert result == []

    def test_exists_commons_file_returns_true(self):
        img = self._make_image("File:Example.png")
        assert img.exists() is True

    def test_exists_missing_file_returns_false(self):
        img = self._make_image("File:NonExistent.png")
        assert img.exists() is False

    def test_convenience_property_url(self):
        img = self._make_image("File:Example.png")
        assert img.url == "https://upload.wikimedia.org/wikipedia/commons/e/example.png"

    def test_convenience_property_width(self):
        img = self._make_image("File:Example.png")
        assert img.width == 800

    def test_convenience_property_height(self):
        img = self._make_image("File:Example.png")
        assert img.height == 600

    def test_convenience_property_size(self):
        img = self._make_image("File:Example.png")
        assert img.size == 102400

    def test_convenience_property_mime(self):
        img = self._make_image("File:Example.png")
        assert img.mime == "image/png"

    def test_convenience_property_mediatype(self):
        img = self._make_image("File:Example.png")
        assert img.mediatype == "BITMAP"

    def test_convenience_property_sha1(self):
        img = self._make_image("File:Example.png")
        assert img.sha1 == "abcdef1234567890abcdef1234567890abcdef12"

    def test_convenience_property_timestamp(self):
        img = self._make_image("File:Example.png")
        assert img.timestamp == "2023-01-15T10:30:00Z"

    def test_convenience_property_user(self):
        img = self._make_image("File:Example.png")
        assert img.user == "TestUser"

    def test_convenience_property_descriptionurl(self):
        img = self._make_image("File:Example.png")
        assert img.descriptionurl == "https://commons.wikimedia.org/wiki/File:Example.png"

    def test_convenience_property_descriptionshorturl(self):
        img = self._make_image("File:Example.png")
        assert img.descriptionshorturl == "https://commons.wikimedia.org/w/index.php?curid=12345"

    def test_convenience_properties_missing_file_return_none(self):
        img = self._make_image("File:NonExistent.png")
        assert img.url is None
        assert img.width is None
        assert img.height is None
        assert img.size is None
        assert img.mime is None
        assert img.mediatype is None
        assert img.sha1 is None
        assert img.timestamp is None
        assert img.user is None
        assert img.descriptionurl is None
        assert img.descriptionshorturl is None

    def test_images_dict_imageinfo_batch_method(self):
        page = self.wiki.page("Test_1")
        imgs = self.wiki.images(page)
        assert isinstance(imgs, wikipediaapi.ImagesDict)
        result = imgs.imageinfo()
        assert isinstance(result, dict)
        assert "File:Example.png" in result
        assert "File:Logo.svg" in result
        assert isinstance(result["File:Example.png"], list)
        assert isinstance(result["File:Example.png"][0], ImageInfo)

    def test_batch_imageinfo_returns_dict(self):
        img1 = self._make_image("File:Example.png")
        img2 = self._make_image("File:Logo.svg")
        result = self.wiki.batch_imageinfo([img1, img2])
        assert isinstance(result, dict)
        assert "File:Example.png" in result
        assert "File:Logo.svg" in result

    def test_batch_imageinfo_populates_each_image(self):
        img1 = self._make_image("File:Example.png")
        img2 = self._make_image("File:Logo.svg")
        result = self.wiki.batch_imageinfo([img1, img2])
        assert len(result["File:Example.png"]) == 1
        assert result["File:Example.png"][0].mime == "image/png"
        assert len(result["File:Logo.svg"]) == 1
        assert result["File:Logo.svg"][0].mime == "image/svg+xml"

    def test_sections_returns_empty_list(self):
        img = self._make_image("File:Example.png")
        assert img.sections == []

    def test_repr_before_fetch(self):
        img = self._make_image("File:Example.png")
        r = repr(img)
        assert "File:Example.png" in r
        assert "id: ??" in r

    def test_exists_local_file_positive_pageid_returns_true(self):
        img = self._make_image("File:LocalFile.png")
        assert img.exists() is True

    def test_getattr_triggers_info_fetch(self):
        img = self._make_image("File:LocalFile.png")
        # fullurl is stored in _attributes after info fetch
        val = img.fullurl
        assert val == "https://en.wikipedia.org/wiki/File:LocalFile.png"

    def test_getattr_raises_for_missing_attribute(self):
        img = self._make_image("File:LocalFile.png")
        # Trigger info fetch first
        _ = img.fullurl
        with pytest.raises(AttributeError):
            _ = img.totally_nonexistent_field_xyz

    def test_getattr_raises_for_private_attribute(self):
        img = self._make_image("File:Example.png")
        with pytest.raises(AttributeError):
            _ = img._nonexistent_private

    def test_repr_after_info_fetch_includes_pageid(self):
        img = self._make_image("File:LocalFile.png")
        _ = img.fullurl  # triggers _fetch("info") via __getattr__
        r = repr(img)
        assert "File:LocalFile.png" in r
        assert "id: ??" not in r

    def test_imageinfo_params_to_api(self):
        p = ImageInfoParams()
        api = p.to_api()
        assert api["iiprop"] == "url|size|mime|mediatype|sha1|timestamp|user"
        assert api["iilimit"] == "1"

    def test_imageinfo_params_rejects_string_prop(self):
        with pytest.raises(TypeError):
            ImageInfoParams(prop="url|size")

    def test_imageinfo_frozen(self):
        info = ImageInfo(url="http://example.com", width=100)
        with pytest.raises(AttributeError):
            info.url = "http://other.com"  # ty: ignore[invalid-assignment]


class TestPagesDictBatchMethods:
    def setup_method(self):
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
            ImagesParams(direction=123)  # ty: ignore[invalid-argument-type]


class TestAsyncPagesDictBatchMethods:
    def setup_method(self):
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
    def setup_method(self):
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
        assert isinstance(imgs, wikipediaapi.AsyncImagesDict)
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
        assert isinstance(results, wikipediaapi.AsyncPagesDict)
        assert len(results) == 2
        assert "Nearby Page 1" in results

    async def test_async_geosearch_meta(self):
        results = await self.wiki.geosearch(coord=GeoPoint(51.5074, -0.1278))
        p1 = results["Nearby Page 1"]
        assert p1.geosearch_meta is not None
        assert p1.geosearch_meta.dist == 50.3

    async def test_async_random(self):
        results = await self.wiki.random(limit=2)
        assert isinstance(results, wikipediaapi.AsyncPagesDict)
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
        assert isinstance(imgs, wikipediaapi.AsyncImagesDict)
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

    def _make_async_image(self, title):
        return wikipediaapi.AsyncWikipediaImage(
            self.wiki,
            title=title,
            ns=6,
            language="en",
            variant=None,
        )

    async def test_async_imageinfo_returns_list(self):
        img = self._make_async_image("File:Example.png")
        result = await self.wiki.imageinfo(img)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ImageInfo)

    async def test_async_imageinfo_fields(self):
        img = self._make_async_image("File:Example.png")
        result = await self.wiki.imageinfo(img)
        info = result[0]
        assert info.url == "https://upload.wikimedia.org/wikipedia/commons/e/example.png"
        assert info.width == 800
        assert info.height == 600
        assert info.mime == "image/png"
        assert info.mediatype == "BITMAP"

    async def test_async_imageinfo_missing_returns_empty(self):
        img = self._make_async_image("File:NonExistent.png")
        result = await self.wiki.imageinfo(img)
        assert result == []

    async def test_async_imageinfo_cached(self):
        img = self._make_async_image("File:Example.png")
        result1 = await self.wiki.imageinfo(img)
        result2 = await self.wiki.imageinfo(img)
        assert result1 is result2

    async def test_async_imageinfo_via_property(self):
        img = self._make_async_image("File:Example.png")
        result = await img.imageinfo
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].mime == "image/png"

    async def test_async_imageinfo_property_cached(self):
        img = self._make_async_image("File:Example.png")
        result1 = await img.imageinfo
        result2 = await img.imageinfo
        assert result1 is result2

    async def test_async_exists_commons_file(self):
        img = self._make_async_image("File:Example.png")
        assert await img.exists() is True

    async def test_async_exists_missing_file(self):
        img = self._make_async_image("File:NonExistent.png")
        assert await img.exists() is False

    async def test_async_convenience_property_url(self):
        img = self._make_async_image("File:Example.png")
        assert await img.url == "https://upload.wikimedia.org/wikipedia/commons/e/example.png"

    async def test_async_convenience_property_width(self):
        img = self._make_async_image("File:Example.png")
        assert await img.width == 800

    async def test_async_convenience_property_height(self):
        img = self._make_async_image("File:Example.png")
        assert await img.height == 600

    async def test_async_convenience_property_mime(self):
        img = self._make_async_image("File:Example.png")
        assert await img.mime == "image/png"

    async def test_async_convenience_property_mediatype(self):
        img = self._make_async_image("File:Example.png")
        assert await img.mediatype == "BITMAP"

    async def test_async_convenience_property_sha1(self):
        img = self._make_async_image("File:Example.png")
        assert await img.sha1 == "abcdef1234567890abcdef1234567890abcdef12"

    async def test_async_convenience_property_timestamp(self):
        img = self._make_async_image("File:Example.png")
        assert await img.timestamp == "2023-01-15T10:30:00Z"

    async def test_async_convenience_property_user(self):
        img = self._make_async_image("File:Example.png")
        assert await img.user == "TestUser"

    async def test_async_convenience_property_descriptionurl(self):
        img = self._make_async_image("File:Example.png")
        assert await img.descriptionurl == "https://commons.wikimedia.org/wiki/File:Example.png"

    async def test_async_convenience_property_descriptionshorturl(self):
        img = self._make_async_image("File:Example.png")
        assert (
            await img.descriptionshorturl == "https://commons.wikimedia.org/w/index.php?curid=12345"
        )

    async def test_async_convenience_properties_missing_return_none(self):
        img = self._make_async_image("File:NonExistent.png")
        assert await img.url is None
        assert await img.width is None
        assert await img.height is None
        assert await img.mime is None
        assert await img.mediatype is None

    async def test_async_images_dict_imageinfo_batch(self):
        page = self.wiki.page("Test_1")
        imgs = await self.wiki.images(page)
        assert isinstance(imgs, wikipediaapi.AsyncImagesDict)
        result = await imgs.imageinfo()
        assert isinstance(result, dict)
        assert "File:Example.png" in result
        assert isinstance(result["File:Example.png"][0], ImageInfo)

    async def test_async_batch_imageinfo(self):
        img1 = self._make_async_image("File:Example.png")
        img2 = self._make_async_image("File:Logo.svg")
        result = await self.wiki.batch_imageinfo([img1, img2])
        assert isinstance(result, dict)
        assert "File:Example.png" in result
        assert "File:Logo.svg" in result
        assert result["File:Example.png"][0].mime == "image/png"
        assert result["File:Logo.svg"][0].mime == "image/svg+xml"

    async def test_async_image_sections_returns_empty_list(self):
        img = self._make_async_image("File:Example.png")
        assert img.sections == []

    async def test_async_convenience_property_size(self):
        img = self._make_async_image("File:Example.png")
        assert await img.size == 102400

    async def test_async_exists_local_file_positive_pageid(self):
        img = self._make_async_image("File:LocalFile.png")
        assert await img.exists() is True

    async def test_async_getattr_triggers_info_fetch(self):
        img = self._make_async_image("File:LocalFile.png")
        val = await img.fullurl
        assert val == "https://en.wikipedia.org/wiki/File:LocalFile.png"

    async def test_async_getattr_raises_for_private_attribute(self):
        img = self._make_async_image("File:Example.png")
        with pytest.raises(AttributeError):
            _ = img._nonexistent_private

    async def test_async_repr_after_info_fetch_includes_pageid(self):
        img = self._make_async_image("File:LocalFile.png")
        _ = await img.fullurl  # triggers _fetch("info") via __getattr__ -> _info_attr
        r = repr(img)
        assert "File:LocalFile.png" in r
        assert "id: ??" not in r
