"""Integration tests for AsyncPagesDict batch methods using VCR cassettes."""

import pytest

import wikipediaapi
from wikipediaapi import CoordinatesProp, CoordinateType, Direction, GeoPoint


class TestVcrAsyncPagesDictCoordinates:
    """Test AsyncPagesDict.coordinates() with various parameters."""

    @pytest.mark.vcr
    async def test_default(self, async_wiki):
        pages = await async_wiki.pages(["London", "Paris"])
        result = await pages.coordinates()
        assert isinstance(result, dict)
        assert len(result) > 0
        for page, coords in result.items():
            assert isinstance(page, wikipediaapi.AsyncWikipediaPage)
            assert isinstance(coords, list)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "primary",
        [CoordinateType.PRIMARY, CoordinateType.SECONDARY, CoordinateType.ALL],
        ids=["primary", "secondary", "all"],
    )
    async def test_primary(self, async_wiki, primary):
        pages = await async_wiki.pages(["London", "Paris"])
        result = await pages.coordinates(primary=primary)
        assert isinstance(result, dict)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "prop",
        [CoordinatesProp.GLOBE, CoordinatesProp.COUNTRY, CoordinatesProp.NAME],
        ids=["globe", "country", "name"],
    )
    async def test_prop(self, async_wiki, prop):
        pages = await async_wiki.pages(["London", "Paris"])
        result = await pages.coordinates(prop=[prop])
        assert isinstance(result, dict)

    @pytest.mark.vcr
    async def test_distance_from_point(self, async_wiki):
        pages = await async_wiki.pages(["London", "Paris"])
        result = await pages.coordinates(distance_from_point=GeoPoint(51.5074, -0.1278))
        assert isinstance(result, dict)


class TestVcrAsyncPagesDictImages:
    """Test AsyncPagesDict.images() with various parameters."""

    @pytest.mark.vcr
    async def test_default(self, async_wiki):
        pages = await async_wiki.pages(["Earth", "Python_(programming_language)"])
        result = await pages.images()
        assert isinstance(result, dict)
        assert len(result) > 0

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "direction",
        [Direction.ASCENDING, Direction.DESCENDING],
        ids=["ascending", "descending"],
    )
    async def test_direction(self, async_wiki, direction):
        pages = await async_wiki.pages(["Earth", "Python_(programming_language)"])
        result = await pages.images(direction=direction)
        assert isinstance(result, dict)

    @pytest.mark.vcr
    async def test_limit(self, async_wiki):
        pages = await async_wiki.pages(["Earth", "Python_(programming_language)"])
        result = await pages.images(limit=3)
        assert isinstance(result, dict)
