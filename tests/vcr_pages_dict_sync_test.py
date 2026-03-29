"""Integration tests for PagesDict batch methods using VCR cassettes."""

import pytest

import wikipediaapi
from wikipediaapi import CoordinatesProp
from wikipediaapi import CoordinateType
from wikipediaapi import Direction
from wikipediaapi import GeoPoint


class TestVcrPagesDictCoordinates:
    """Test PagesDict.coordinates() with various parameters."""

    @pytest.mark.vcr
    def test_default(self, sync_wiki):
        pages = sync_wiki.pages(["London", "Paris"])
        result = pages.coordinates()
        assert isinstance(result, dict)
        assert len(result) > 0
        for page, coords in result.items():
            assert isinstance(page, wikipediaapi.WikipediaPage)
            assert isinstance(coords, list)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "primary",
        [CoordinateType.PRIMARY, CoordinateType.SECONDARY, CoordinateType.ALL],
        ids=["primary", "secondary", "all"],
    )
    def test_primary(self, sync_wiki, primary):
        pages = sync_wiki.pages(["London", "Paris"])
        result = pages.coordinates(primary=primary)
        assert isinstance(result, dict)

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "prop",
        [CoordinatesProp.GLOBE, CoordinatesProp.COUNTRY, CoordinatesProp.NAME],
        ids=["globe", "country", "name"],
    )
    def test_prop(self, sync_wiki, prop):
        pages = sync_wiki.pages(["London", "Paris"])
        result = pages.coordinates(prop=[prop])
        assert isinstance(result, dict)

    @pytest.mark.vcr
    def test_distance_from_point(self, sync_wiki):
        pages = sync_wiki.pages(["London", "Paris"])
        result = pages.coordinates(distance_from_point=GeoPoint(51.5074, -0.1278))
        assert isinstance(result, dict)


class TestVcrPagesDictImages:
    """Test PagesDict.images() with various parameters."""

    @pytest.mark.vcr
    def test_default(self, sync_wiki):
        pages = sync_wiki.pages(["Earth", "Python_(programming_language)"])
        result = pages.images()
        assert isinstance(result, dict)
        assert len(result) > 0

    @pytest.mark.vcr
    @pytest.mark.parametrize(
        "direction",
        [Direction.ASCENDING, Direction.DESCENDING],
        ids=["ascending", "descending"],
    )
    def test_direction(self, sync_wiki, direction):
        pages = sync_wiki.pages(["Earth", "Python_(programming_language)"])
        result = pages.images(direction=direction)
        assert isinstance(result, dict)

    @pytest.mark.vcr
    def test_limit(self, sync_wiki):
        pages = sync_wiki.pages(["Earth", "Python_(programming_language)"])
        result = pages.images(limit=3)
        assert isinstance(result, dict)
