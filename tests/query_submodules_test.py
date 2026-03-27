# flake8: noqa
import unittest

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


class TestCoordinates(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_coordinates_default(self):
        page = self.wiki.page("Test_1")
        coords = self.wiki.coordinates(page)
        self.assertEqual(len(coords), 1)
        self.assertAlmostEqual(coords[0].lat, 51.5074)
        self.assertAlmostEqual(coords[0].lon, -0.1278)
        self.assertTrue(coords[0].primary)
        self.assertEqual(coords[0].globe, "earth")

    def test_coordinates_primary_all(self):
        page = self.wiki.page("Test_1")
        coords = self.wiki.coordinates(page, primary="all")
        self.assertEqual(len(coords), 2)
        self.assertAlmostEqual(coords[0].lat, 51.5074)
        self.assertAlmostEqual(coords[1].lat, 48.8566)

    def test_coordinates_nonexistent_page(self):
        page = self.wiki.page("NonExistent")
        coords = self.wiki.coordinates(page)
        self.assertEqual(coords, [])

    def test_coordinates_cached(self):
        page = self.wiki.page("Test_1")
        coords1 = self.wiki.coordinates(page)
        coords2 = self.wiki.coordinates(page)
        self.assertIs(coords1, coords2)

    def test_coordinates_per_param_cache(self):
        page1 = self.wiki.page("Test_1")
        page2 = self.wiki.page("Test_1")
        coords_default = self.wiki.coordinates(page1)
        coords_all = self.wiki.coordinates(page2, primary="all")
        self.assertEqual(len(coords_default), 1)
        self.assertEqual(len(coords_all), 2)

    def test_coordinates_with_iterable_prop(self):
        page = self.wiki.page("Test_1")
        coords = self.wiki.coordinates(page, prop=["globe"])
        self.assertEqual(len(coords), 1)

    def test_page_coordinates_property(self):
        page = self.wiki.page("Test_1")
        coords = page.coordinates
        self.assertEqual(len(coords), 1)
        self.assertAlmostEqual(coords[0].lat, 51.5074)

    def test_page_coordinates_property_cached(self):
        page = self.wiki.page("Test_1")
        _ = page.coordinates
        coords = page.coordinates
        self.assertEqual(len(coords), 1)


class TestImages(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_images_default(self):
        page = self.wiki.page("Test_1")
        imgs = self.wiki.images(page)
        self.assertIsInstance(imgs, wikipediaapi.ImagesDict)
        self.assertEqual(len(imgs), 2)
        self.assertIn("File:Example.png", imgs)
        self.assertIn("File:Logo.svg", imgs)

    def test_images_nonexistent_page(self):
        page = self.wiki.page("NonExistent")
        imgs = self.wiki.images(page)
        self.assertEqual(len(imgs), 0)

    def test_images_cached(self):
        page = self.wiki.page("Test_1")
        imgs1 = self.wiki.images(page)
        imgs2 = self.wiki.images(page)
        self.assertIs(imgs1, imgs2)

    def test_page_images_property(self):
        page = self.wiki.page("Test_1")
        imgs = page.images
        self.assertIsInstance(imgs, wikipediaapi.ImagesDict)
        self.assertEqual(len(imgs), 2)


class TestGeoSearch(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_geosearch(self):
        # Test geosearch using a page as the center point
        center_page = self.wiki.page("Test_1")
        results = self.wiki.geosearch(page=center_page)
        self.assertIsInstance(results, wikipediaapi.PagesDict)
        self.assertEqual(len(results), 2)
        self.assertIn("Nearby Page 1", results)
        self.assertIn("Nearby Page 2", results)

    def test_geosearch_with_coordinates(self):
        # Test geosearch using direct coordinates (alternative to page-based)
        results = self.wiki.geosearch(coord=GeoPoint(51.5074, -0.1278))
        self.assertIsInstance(results, wikipediaapi.PagesDict)
        self.assertEqual(len(results), 2)
        self.assertIn("Nearby Page 1", results)
        self.assertIn("Nearby Page 2", results)

    def test_geosearch_meta(self):
        # Test geosearch metadata using page as center
        center_page = self.wiki.page("Test_1")
        results = self.wiki.geosearch(page=center_page)
        p1 = results["Nearby Page 1"]
        self.assertIsNotNone(p1.geosearch_meta)
        self.assertAlmostEqual(p1.geosearch_meta.dist, 50.3)
        self.assertAlmostEqual(p1.geosearch_meta.lat, 51.508)
        self.assertTrue(p1.geosearch_meta.primary)

    def test_geosearch_precaches_coordinates(self):
        # Test that geosearch precaches coordinates using page as center
        center_page = self.wiki.page("Test_1")
        results = self.wiki.geosearch(page=center_page)
        p1 = results["Nearby Page 1"]
        default_key = CoordinatesParams().cache_key()
        cached = p1._get_cached("coordinates", default_key)
        self.assertNotIsInstance(cached, type(NOT_CACHED))
        self.assertEqual(len(cached), 1)
        self.assertAlmostEqual(cached[0].lat, 51.508)

    def test_geosearch_pageid_preset(self):
        # Test pageid preset using page as center
        center_page = self.wiki.page("Test_1")
        results = self.wiki.geosearch(page=center_page)
        p1 = results["Nearby Page 1"]
        self.assertEqual(p1._attributes["pageid"], 100)


class TestRandom(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_random(self):
        results = self.wiki.random(limit=2)
        self.assertIsInstance(results, wikipediaapi.PagesDict)
        self.assertEqual(len(results), 2)
        self.assertIn("Random Page A", results)
        self.assertIn("Random Page B", results)

    def test_random_pageid_preset(self):
        results = self.wiki.random(limit=2)
        self.assertEqual(results["Random Page A"]._attributes["pageid"], 200)
        self.assertEqual(results["Random Page B"]._attributes["pageid"], 201)


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_search(self):
        results = self.wiki.search("Python")
        self.assertIsInstance(results, wikipediaapi.SearchResults)
        self.assertEqual(len(results.pages), 2)
        self.assertIn("Python (programming language)", results.pages)
        self.assertIn("Python (mythology)", results.pages)

    def test_search_totalhits(self):
        results = self.wiki.search("Python")
        self.assertEqual(results.totalhits, 5432)

    def test_search_suggestion(self):
        results = self.wiki.search("Python")
        self.assertEqual(results.suggestion, "python programming")

    def test_search_meta(self):
        results = self.wiki.search("Python")
        p = results.pages["Python (programming language)"]
        self.assertIsNotNone(p.search_meta)
        self.assertEqual(p.search_meta.size, 123456)
        self.assertEqual(p.search_meta.wordcount, 15000)
        self.assertIn("Python", p.search_meta.snippet)
        self.assertEqual(p.search_meta.timestamp, "2024-01-01T00:00:00Z")

    def test_search_pageid_preset(self):
        results = self.wiki.search("Python")
        p = results.pages["Python (programming language)"]
        self.assertEqual(p._attributes["pageid"], 300)


class TestPages(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_pages_creates_pages_dict(self):
        pd = self.wiki.pages(["Test_1", "NonExistent"])
        self.assertIsInstance(pd, wikipediaapi.PagesDict)
        self.assertEqual(len(pd), 2)
        self.assertIn("Test_1", pd)
        self.assertIn("NonExistent", pd)

    def test_pages_lazy(self):
        pd = self.wiki.pages(["Test_1"])
        page = pd["Test_1"]
        self.assertFalse(any(page._called.values()))


class TestParamCache(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_get_cached_miss(self):
        page = self.wiki.page("Test_1")
        result = page._get_cached("coordinates", CoordinatesParams().cache_key())
        self.assertIs(result, NOT_CACHED)

    def test_set_and_get_cached(self):
        page = self.wiki.page("Test_1")
        key = CoordinatesParams().cache_key()
        page._set_cached("coordinates", key, ["test_value"])
        result = page._get_cached("coordinates", key)
        self.assertEqual(result, ["test_value"])

    def test_different_params_different_cache(self):
        page = self.wiki.page("Test_1")
        key1 = CoordinatesParams().cache_key()
        key2 = CoordinatesParams(primary="all").cache_key()
        self.assertNotEqual(key1, key2)
        page._set_cached("coordinates", key1, ["default"])
        page._set_cached("coordinates", key2, ["all"])
        self.assertEqual(page._get_cached("coordinates", key1), ["default"])
        self.assertEqual(page._get_cached("coordinates", key2), ["all"])


class TestParamsToApi(unittest.TestCase):
    def test_coordinates_params(self):
        p = CoordinatesParams()
        api = p.to_api()
        self.assertEqual(api["colimit"], "10")
        self.assertEqual(api["coprimary"], "primary")
        self.assertEqual(api["coprop"], "globe")
        self.assertNotIn("codistancefrompoint", api)

    def test_coordinates_params_with_distance(self):
        p = CoordinatesParams(distance_from_point=GeoPoint(37.787, -122.4))
        api = p.to_api()
        self.assertEqual(api["codistancefrompoint"], "37.787|-122.4")

    def test_images_params(self):
        p = ImagesParams()
        api = p.to_api()
        self.assertEqual(api["imlimit"], "10")
        self.assertEqual(api["imdir"], "ascending")
        self.assertNotIn("imimages", api)

    def test_coordinates_params_with_iterable_prop(self):
        p = CoordinatesParams(prop=["name", "globe"])
        api = p.to_api()
        self.assertEqual(api["coprop"], "name|globe")

    def test_images_params_with_iterable_images(self):
        p = ImagesParams(images=["File:Test.png", "File:Logo.svg"])
        api = p.to_api()
        self.assertEqual(api["imimages"], "File:Test.png|File:Logo.svg")

    def test_coordinates_params_rejects_string_prop(self):
        with self.assertRaises(TypeError):
            CoordinatesParams(prop="globe")

    def test_images_params_rejects_string_images(self):
        with self.assertRaises(TypeError):
            ImagesParams(images="File:Test.png")

    def test_geosearch_params_rejects_string_prop(self):
        with self.assertRaises(TypeError):
            GeoSearchParams(coord=GeoPoint(51.5, -0.1), prop="name|country")

    def test_geosearch_params_rejects_string_coord(self):
        with self.assertRaises(TypeError):
            GeoSearchParams(coord="51.5|-0.1")

    def test_geosearch_params_rejects_string_bbox(self):
        with self.assertRaises(TypeError):
            GeoSearchParams(bbox="52.0|-1.0|51.0|0.0")

    def test_coordinates_params_rejects_string_distance_from_point(self):
        with self.assertRaises(TypeError):
            CoordinatesParams(distance_from_point="37.787|-122.4")

    def test_search_params_rejects_string_prop(self):
        with self.assertRaises(TypeError):
            SearchParams(query="test", prop="size|wordcount")

    def test_search_params_rejects_string_info(self):
        with self.assertRaises(TypeError):
            SearchParams(query="test", info="totalhits|suggestion")

    def test_cache_key_is_hashable(self):
        p = CoordinatesParams()
        key = p.cache_key()
        self.assertIsInstance(key, tuple)
        d = {key: "test"}
        self.assertEqual(d[key], "test")


class TestTypes(unittest.TestCase):
    def test_coordinate_frozen(self):
        c = wikipediaapi.Coordinate(lat=1.0, lon=2.0, primary=True)
        with self.assertRaises(AttributeError):
            c.lat = 3.0  # type: ignore[misc]

    def test_geosearch_meta_frozen(self):
        m = wikipediaapi.GeoSearchMeta(dist=10.0, lat=1.0, lon=2.0, primary=True)
        with self.assertRaises(AttributeError):
            m.dist = 20.0  # type: ignore[misc]

    def test_search_meta_frozen(self):
        m = wikipediaapi.SearchMeta(snippet="test", size=100, wordcount=10, timestamp="2024-01-01")
        with self.assertRaises(AttributeError):
            m.snippet = "new"  # type: ignore[misc]

    def test_geo_point_defaults(self):
        point = wikipediaapi.GeoPoint()
        self.assertEqual(point.lat, 0.0)
        self.assertEqual(point.lon, 0.0)

    def test_geo_point_validation(self):
        with self.assertRaises(ValueError):
            wikipediaapi.GeoPoint(100.0, 0.0)
        with self.assertRaises(ValueError):
            wikipediaapi.GeoPoint(0.0, 200.0)

    def test_geo_box_defaults(self):
        box = wikipediaapi.GeoBox()
        self.assertEqual(box.top_left, wikipediaapi.GeoPoint(0.0, 0.0))
        self.assertEqual(box.bottom_right, wikipediaapi.GeoPoint(0.0, 0.0))

    def test_geo_box_validation(self):
        with self.assertRaises(ValueError):
            wikipediaapi.GeoBox(
                top_left=wikipediaapi.GeoPoint(10.0, 0.0),
                bottom_right=wikipediaapi.GeoPoint(20.0, 1.0),
            )
        with self.assertRaises(ValueError):
            wikipediaapi.GeoBox(
                top_left=wikipediaapi.GeoPoint(20.0, 5.0),
                bottom_right=wikipediaapi.GeoPoint(10.0, 4.0),
            )


class TestPagesDictClass(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_pages_dict_is_dict(self):
        pd = wikipediaapi.PagesDict()
        self.assertIsInstance(pd, dict)

    def test_pages_dict_with_data(self):
        page = self.wiki.page("Test_1")
        pd = wikipediaapi.PagesDict(wiki=self.wiki, data={"Test_1": page})
        self.assertEqual(len(pd), 1)
        self.assertIn("Test_1", pd)

    def test_pages_dict_backward_compatible(self):
        pd = wikipediaapi.PagesDict()
        pd["key"] = "value"
        self.assertEqual(pd["key"], "value")


class TestSentinel(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(repr(NOT_CACHED), "<NOT_CACHED>")

    def test_bool(self):
        self.assertFalse(bool(NOT_CACHED))

    def test_singleton(self):
        s1 = _Sentinel()
        s2 = _Sentinel()
        self.assertIs(s1, s2)


class TestBasePageGetattr(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_private_attr_raises(self):
        page = self.wiki.page("Test_1")
        with self.assertRaises(AttributeError):
            _ = page._nonexistent_private

    def test_missing_attr_raises(self):
        page = self.wiki.page("Test_1")
        # Force info fetch so __getattr__ doesn't trigger lazy fetch
        page._called["info"] = True
        with self.assertRaises(AttributeError):
            _ = page.totally_nonexistent_attr


class TestBatchCoordinates(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_batch_coordinates(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        result = self.wiki.batch_coordinates([p1, p2])
        self.assertIn(p1, result)
        self.assertEqual(len(result[p1]), 1)
        self.assertAlmostEqual(result[p1][0].lat, 51.5074)
        # NonExistent should have empty list
        self.assertIn(p2, result)
        self.assertEqual(result[p2], [])


class TestBatchImages(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_batch_images(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        result = self.wiki.batch_images([p1, p2])
        self.assertIn("Test 1", result)
        self.assertEqual(len(result["Test 1"]), 2)
        self.assertIn("File:Example.png", result["Test 1"])
        # NonExistent should have empty PagesDict
        self.assertIn("NonExistent", result)
        self.assertEqual(len(result["NonExistent"]), 0)


class TestPagesDictBatchMethods(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_pages_dict_coordinates(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        pd = wikipediaapi.PagesDict(wiki=self.wiki, data={"Test_1": p1, "NonExistent": p2})
        result = pd.coordinates()
        self.assertIn(p1, result)
        self.assertEqual(len(result[p1]), 1)

    def test_pages_dict_images(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        pd = wikipediaapi.PagesDict(wiki=self.wiki, data={"Test_1": p1, "NonExistent": p2})
        result = pd.images()
        self.assertIn("Test 1", result)
        self.assertEqual(len(result["Test 1"]), 2)


class TestParamsToApiExtended(unittest.TestCase):
    def test_geosearch_params(self):
        p = GeoSearchParams(coord=GeoPoint(51.5, -0.1))
        api = p.to_api()
        self.assertEqual(api["gscoord"], "51.5|-0.1")
        self.assertEqual(api["gsradius"], "500")

    def test_random_params(self):
        p = RandomParams(limit=5)
        api = p.to_api()
        self.assertEqual(api["rnlimit"], "5")

    def test_search_params(self):
        p = SearchParams(query="test", namespace=wikipediaapi.Namespace.MAIN)
        api = p.to_api()
        self.assertEqual(api["srsearch"], "test")
        self.assertEqual(api["srnamespace"], "0")

    def test_geosearch_params_with_iterable_prop(self):
        p = GeoSearchParams(coord=GeoPoint(51.5, -0.1), prop=["name", "country"])
        api = p.to_api()
        self.assertEqual(api["gsprop"], "name|country")

    def test_geosearch_params_with_bbox(self):
        p = GeoSearchParams(
            bbox=GeoBox(top_left=GeoPoint(52.0, -1.0), bottom_right=GeoPoint(51.0, 0.0))
        )
        api = p.to_api()
        self.assertEqual(api["gsbbox"], "52.0|-1.0|51.0|0.0")

    def test_search_params_with_iterable_prop_and_info(self):
        p = SearchParams(
            query="test",
            prop=["size", "wordcount"],
            info=["totalhits", "suggestion"],
        )
        api = p.to_api()
        self.assertEqual(api["srprop"], "size|wordcount")
        self.assertEqual(api["srinfo"], "totalhits|suggestion")

    def test_images_params_with_images(self):
        p = ImagesParams(images=["File:Test.png"], direction=Direction.DESCENDING)
        api = p.to_api()
        self.assertEqual(api["imimages"], "File:Test.png")
        self.assertEqual(api["imdir"], "descending")

    def test_images_params_accepts_string_direction(self):
        p = ImagesParams(direction="descending")
        api = p.to_api()
        self.assertEqual(api["imdir"], "descending")

    def test_images_params_rejects_invalid_direction(self):
        with self.assertRaises(TypeError):
            ImagesParams(direction=123)  # type: ignore[arg-type]


class TestAsyncPagesDictBatchMethods(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        self.wiki._get = async_wikipedia_api_request(self.wiki)

    async def test_async_pages_dict_constructor(self):
        from wikipediaapi._pages_dict import AsyncPagesDict

        p1 = self.wiki.page("Test_1")
        apd = AsyncPagesDict(wiki=self.wiki, data={"Test_1": p1})
        self.assertEqual(len(apd), 1)
        self.assertIn("Test_1", apd)

    async def test_async_pages_dict_coordinates(self):
        from wikipediaapi._pages_dict import AsyncPagesDict

        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        apd = AsyncPagesDict(wiki=self.wiki, data={"Test_1": p1, "NonExistent": p2})
        result = await apd.coordinates()
        self.assertIn(p1, result)
        self.assertEqual(len(result[p1]), 1)

    async def test_async_pages_dict_images(self):
        from wikipediaapi._pages_dict import AsyncPagesDict

        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        apd = AsyncPagesDict(wiki=self.wiki, data={"Test_1": p1, "NonExistent": p2})
        result = await apd.images()
        self.assertIn("Test 1", result)
        self.assertEqual(len(result["Test 1"]), 2)


class TestAsyncQuerySubmodules(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        self.wiki._get = async_wikipedia_api_request(self.wiki)

    async def test_async_coordinates(self):
        page = self.wiki.page("Test_1")
        coords = await self.wiki.coordinates(page)
        self.assertEqual(len(coords), 1)
        self.assertAlmostEqual(coords[0].lat, 51.5074)

    async def test_async_coordinates_nonexistent(self):
        page = self.wiki.page("NonExistent")
        coords = await self.wiki.coordinates(page)
        self.assertEqual(coords, [])

    async def test_async_coordinates_cached(self):
        page = self.wiki.page("Test_1")
        coords1 = await self.wiki.coordinates(page)
        coords2 = await self.wiki.coordinates(page)
        self.assertIs(coords1, coords2)

    async def test_async_images(self):
        page = self.wiki.page("Test_1")
        imgs = await self.wiki.images(page)
        self.assertIsInstance(imgs, wikipediaapi.AsyncImagesDict)
        self.assertEqual(len(imgs), 2)

    async def test_async_images_nonexistent(self):
        page = self.wiki.page("NonExistent")
        imgs = await self.wiki.images(page)
        self.assertEqual(len(imgs), 0)

    async def test_async_images_cached(self):
        page = self.wiki.page("Test_1")
        imgs1 = await self.wiki.images(page)
        imgs2 = await self.wiki.images(page)
        self.assertIs(imgs1, imgs2)

    async def test_async_geosearch(self):
        results = await self.wiki.geosearch(coord=GeoPoint(51.5074, -0.1278))
        self.assertIsInstance(results, wikipediaapi.PagesDict)
        self.assertEqual(len(results), 2)
        self.assertIn("Nearby Page 1", results)

    async def test_async_geosearch_meta(self):
        results = await self.wiki.geosearch(coord=GeoPoint(51.5074, -0.1278))
        p1 = results["Nearby Page 1"]
        self.assertIsNotNone(p1.geosearch_meta)
        self.assertAlmostEqual(p1.geosearch_meta.dist, 50.3)

    async def test_async_random(self):
        results = await self.wiki.random(limit=2)
        self.assertIsInstance(results, wikipediaapi.PagesDict)
        self.assertEqual(len(results), 2)
        self.assertIn("Random Page A", results)

    async def test_async_search(self):
        results = await self.wiki.search("Python")
        self.assertIsInstance(results, wikipediaapi.SearchResults)
        self.assertEqual(len(results.pages), 2)
        self.assertEqual(results.totalhits, 5432)

    async def test_async_search_meta(self):
        results = await self.wiki.search("Python")
        p = results.pages["Python (programming language)"]
        self.assertIsNotNone(p.search_meta)
        self.assertEqual(p.search_meta.size, 123456)

    async def test_async_batch_coordinates(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        result = await self.wiki.batch_coordinates([p1, p2])
        self.assertIn(p1, result)
        self.assertEqual(len(result[p1]), 1)

    async def test_async_batch_images(self):
        p1 = self.wiki.page("Test_1")
        p2 = self.wiki.page("NonExistent")
        result = await self.wiki.batch_images([p1, p2])
        self.assertIn("Test 1", result)
        self.assertEqual(len(result["Test 1"]), 2)

    async def test_async_page_coordinates_property(self):
        page = self.wiki.page("Test_1")
        coords = await page.coordinates
        self.assertEqual(len(coords), 1)
        self.assertAlmostEqual(coords[0].lat, 51.5074)

    async def test_async_page_images_property(self):
        page = self.wiki.page("Test_1")
        imgs = await page.images
        self.assertIsInstance(imgs, wikipediaapi.AsyncImagesDict)
        self.assertEqual(len(imgs), 2)

    async def test_async_page_geosearch_meta_none(self):
        page = self.wiki.page("Test_1")
        self.assertIsNone(page.geosearch_meta)

    async def test_async_page_search_meta_none(self):
        page = self.wiki.page("Test_1")
        self.assertIsNone(page.search_meta)

    async def test_async_page_geosearch_meta_set(self):
        results = await self.wiki.geosearch(coord=GeoPoint(51.5074, -0.1278))
        p1 = results["Nearby Page 1"]
        self.assertIsNotNone(p1.geosearch_meta)
        self.assertAlmostEqual(p1.geosearch_meta.dist, 50.3)

    async def test_async_page_search_meta_set(self):
        results = await self.wiki.search("Python")
        p = results.pages["Python (programming language)"]
        self.assertIsNotNone(p.search_meta)
        self.assertEqual(p.search_meta.size, 123456)


if __name__ == "__main__":
    unittest.main()
