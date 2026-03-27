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
class GeoPoint:
    """A geographic point with latitude/longitude validation.

    Used as pythonic input for API parameters that previously required
    MediaWiki's ``"lat|lon"`` string format.

    Args:
        lat: Latitude in decimal degrees, valid range ``[-90.0, 90.0]``.
        lon: Longitude in decimal degrees, valid range ``[-180.0, 180.0]``.

    Raises:
        ValueError: If ``lat`` is outside ``[-90.0, 90.0]``.
        ValueError: If ``lon`` is outside ``[-180.0, 180.0]``.
    """

    lat: float = 0.0
    lon: float = 0.0

    def __post_init__(self) -> None:
        """Validate latitude and longitude ranges after initialisation.

        Raises:
            ValueError: If ``lat`` is outside ``[-90.0, 90.0]``.
            ValueError: If ``lon`` is outside ``[-180.0, 180.0]``.
        """
        if not -90.0 <= self.lat <= 90.0:
            raise ValueError("GeoPoint.lat must be in range [-90.0, 90.0]")
        if not -180.0 <= self.lon <= 180.0:
            raise ValueError("GeoPoint.lon must be in range [-180.0, 180.0]")

    def to_mediawiki(self) -> str:
        """Convert this point to MediaWiki ``"lat|lon"`` format.

        Returns:
            The ``"lat|lon"`` string expected by MediaWiki query params.
        """
        return f"{self.lat}|{self.lon}"


@dataclass(frozen=True)
class GeoBox:
    """A geographic bounding box defined by two validated corner points.

    Represents MediaWiki's ``gsbbox`` value in a pythonic structured way.

    Args:
        top_left: Top-left corner of the box.
        bottom_right: Bottom-right corner of the box.

    Raises:
        ValueError: If the top-left latitude is smaller than bottom-right latitude.
        ValueError: If the top-left longitude is greater than bottom-right longitude.
    """

    top_left: GeoPoint = GeoPoint(0.0, 0.0)
    bottom_right: GeoPoint = GeoPoint(0.0, 0.0)

    def __post_init__(self) -> None:
        """Validate corner ordering semantics for a north-west/south-east box.

        Raises:
            ValueError: If ``top_left.lat < bottom_right.lat``.
            ValueError: If ``top_left.lon > bottom_right.lon``.
        """
        if self.top_left.lat < self.bottom_right.lat:
            raise ValueError("GeoBox.top_left.lat must be >= GeoBox.bottom_right.lat")
        if self.top_left.lon > self.bottom_right.lon:
            raise ValueError("GeoBox.top_left.lon must be <= GeoBox.bottom_right.lon")

    def to_mediawiki(self) -> str:
        """Convert this box to MediaWiki ``"top|left|bottom|right"`` format.

        Returns:
            The ``"top_lat|left_lon|bottom_lat|right_lon"`` string expected
            by MediaWiki query params.
        """
        return (
            f"{self.top_left.lat}|{self.top_left.lon}|"
            f"{self.bottom_right.lat}|{self.bottom_right.lon}"
        )


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
    :class:`~wikipediaapi.PagesDict` keyed by title; each
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
