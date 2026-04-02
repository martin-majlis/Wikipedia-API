"""Typed dataclasses for structured API responses.

This module defines immutable data containers returned by the new query
submodule methods (coordinates, geosearch, search, etc.).  Each class
maps directly to a subset of MediaWiki API JSON response and provides
typed attribute access with sensible defaults.
"""

from .coordinate import Coordinate
from .geo_box import GeoBox
from .geo_point import GeoPoint
from .geo_search_meta import GeoSearchMeta
from .image_info import ImageInfo
from .search_meta import SearchMeta
from .search_results import SearchResults

__all__ = [
    "GeoPoint",
    "GeoBox",
    "Coordinate",
    "GeoSearchMeta",
    "ImageInfo",
    "SearchMeta",
    "SearchResults",
]
