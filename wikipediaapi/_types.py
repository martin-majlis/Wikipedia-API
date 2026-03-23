"""Typed dataclasses for structured API responses.

This module defines immutable data containers returned by the new query
submodule methods (coordinates, geosearch, search, etc.).  Each class
maps directly to a subset of the MediaWiki API JSON response and provides
typed attribute access with sensible defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._pages_dict import PagesDict


@dataclass(frozen=True)
class Coordinate:
    """A single geographic coordinate associated with a Wikipedia page.

    Represents one entry from the ``prop=coordinates`` API response.
    Always contains ``lat``, ``lon``, and ``primary``; additional fields
    are populated when requested via the ``prop`` parameter.

    Args:
        lat: Latitude in decimal degrees.
        lon: Longitude in decimal degrees.
        primary: True if this is the primary coordinate for the page.
        globe: Celestial body the coordinates refer to.
        type: Type of the geographic object (e.g. ``"city"``).
        name: Name of the geographic object.
        dim: Approximate size of the object in meters.
        country: ISO 3166-1 alpha-2 country code.
        region: ISO 3166-2 region code (part after the dash).
        dist: Distance in meters from a reference point, set only when
            ``distance_from_point`` or ``distance_from_page`` is used.
    """

    lat: float
    lon: float
    primary: bool
    globe: str = "earth"
    type: str | None = None
    name: str | None = None
    dim: int | None = None
    country: str | None = None
    region: str | None = None
    dist: float | None = None


@dataclass(frozen=True)
class GeoSearchMeta:
    """Contextual metadata attached to pages returned by a geosearch query.

    Accessible via ``page.geosearch_meta`` on pages produced by
    ``wiki.geosearch()``.  Contains the distance from the search centre
    and the coordinate that was matched.

    Args:
        dist: Distance in meters from the search centre.
        lat: Latitude of the matched coordinate.
        lon: Longitude of the matched coordinate.
        primary: True if the matched coordinate is the primary one.
    """

    dist: float
    lat: float
    lon: float
    primary: bool


@dataclass(frozen=True)
class SearchMeta:
    """Contextual metadata attached to pages returned by a search query.

    Accessible via ``page.search_meta`` on pages produced by
    ``wiki.search()``.  Contains search-specific fields like the
    highlighted snippet.

    Args:
        snippet: HTML snippet with query-term highlighting.
        size: Page size in bytes.
        wordcount: Word count of the page.
        timestamp: ISO 8601 timestamp of the last edit.
    """

    snippet: str = ""
    size: int = 0
    wordcount: int = 0
    timestamp: str = ""


@dataclass
class SearchResults:
    """Wrapper for search results combining pages with aggregate metadata.

    Returned by ``wiki.search()``.  The ``pages`` attribute is a
    :class:`~wikipediaapi._pages_dict.PagesDict` keyed by title; each
    page carries a :class:`SearchMeta` sub-object accessible via
    ``page.search_meta``.

    Args:
        pages: Dictionary of matching pages keyed by title.
        totalhits: Total number of matches reported by the API.
        suggestion: Spelling suggestion from the search backend, or None.
    """

    pages: PagesDict
    totalhits: int = 0
    suggestion: str | None = None
