"""Parameters for list=geosearch (prefix gs).

At least one of coord, page, or bbox must be provided.

Args:
    coord: Centre point as GeoPoint.
    page: Page whose coordinates to use as centre.
    bbox: Bounding box as GeoBox.
    radius: Search radius in meters (10–10000).
    max_dim: Exclude objects larger than this many meters.
    sort: Sort order: "distance" or "relevance".
    limit: Maximum pages to return (1–500).
    globe: Celestial body: "earth", "mars", "moon", "venus".
    namespace: Restrict to this namespace number.
    prop: Additional coordinate properties as an iterable.
    primary: Which coordinates to consider: "primary", "secondary", or "all".
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import ClassVar

from .._enums import CoordinateType
from .._enums import GeoSearchSort
from .._enums import Globe
from .._enums import Namespace
from .._enums import WikiCoordinatesProp
from .._enums import WikiCoordinateType
from .._enums import WikiGeoSearchSort
from .._enums import WikiGlobe
from .._enums import WikiNamespace
from .._enums import coordinate_type2str
from .._enums import coordinates_prop2str
from .._enums import geosearch_sort2str
from .._enums import globe2str
from .._types import GeoBox
from .._types import GeoPoint
from .base_params import _BaseParams
from .protocols import _HasTitle


@dataclass(frozen=True)
class GeoSearchParams(_BaseParams):
    """Parameters for ``list=geosearch`` (prefix ``gs``).

    At least one of ``coord``, ``page``, or ``bbox`` must be provided.

    Args:
        coord: Centre point as :class:`~wikipediaapi.GeoPoint`.
        page: Page whose coordinates to use as centre.
        bbox: Bounding box as :class:`~wikipediaapi.GeoBox`.
        radius: Search radius in meters (10–10000).
        max_dim: Exclude objects larger than this many meters.
        sort: Sort order: ``"distance"`` or ``"relevance"``.
        limit: Maximum pages to return (1–500).
        globe: Celestial body: ``"earth"``, ``"mars"``, ``"moon"``, ``"venus"``.
        namespace: Restrict to this namespace number.
        prop: Additional coordinate properties as an iterable.
        primary: Which coordinates to consider: ``"primary"``,
            ``"secondary"``, or ``"all"``.
    """

    coord: GeoPoint | None = None
    page: _HasTitle | None = None
    bbox: GeoBox | None = None
    radius: int = 500
    max_dim: int | None = None
    sort: WikiGeoSearchSort = GeoSearchSort.DISTANCE
    limit: int = 10
    globe: WikiGlobe = Globe.EARTH
    namespace: WikiNamespace = Namespace.MAIN
    prop: Iterable[WikiCoordinatesProp] | None = None
    primary: WikiCoordinateType | None = None

    def __post_init__(self) -> None:
        """Normalize iterable geosearch properties and reject string input.

        Converts the iterable ``prop`` value into the MediaWiki-required
        pipe-separated string representation when provided.

        Raises:
            TypeError: If ``prop`` is passed as a string instead of an iterable.
        """
        if not isinstance(self.sort, (GeoSearchSort, str)):
            raise TypeError("GeoSearchParams.sort must be GeoSearchSort or str")
        object.__setattr__(self, "sort", geosearch_sort2str(self.sort))

        if not isinstance(self.globe, (Globe, str)):
            raise TypeError("GeoSearchParams.globe must be Globe or str")
        object.__setattr__(self, "globe", globe2str(self.globe))

        if self.primary is not None:
            if not isinstance(self.primary, (CoordinateType, str)):
                raise TypeError("GeoSearchParams.primary must be CoordinateType or str")
            object.__setattr__(self, "primary", coordinate_type2str(self.primary))

        if self.coord is not None:
            if not isinstance(self.coord, GeoPoint):
                raise TypeError("GeoSearchParams.coord must be GeoPoint or None")
            object.__setattr__(self, "coord", self.coord.to_mediawiki())
        if self.bbox is not None:
            if not isinstance(self.bbox, GeoBox):
                raise TypeError("GeoSearchParams.bbox must be GeoBox or None")
            object.__setattr__(self, "bbox", self.bbox.to_mediawiki())
        if self.page is not None:
            # Convert page object to title string
            if hasattr(self.page, "title"):
                object.__setattr__(self, "page", self.page.title)
            else:
                raise TypeError(
                    "GeoSearchParams.page must be an object with a 'title' attribute or None"
                )
        if self.prop is not None:
            if isinstance(self.prop, str):
                raise TypeError(
                    "GeoSearchParams.prop must be an iterable of WikiCoordinatesProp, not str"
                )
            converted_props = [coordinates_prop2str(p) for p in self.prop]
            object.__setattr__(self, "prop", "|".join(converted_props))

    PREFIX: ClassVar[str] = "gs"
    FIELD_MAP: ClassVar[dict[str, str]] = {
        "coord": "coord",
        "page": "page",
        "bbox": "bbox",
        "radius": "radius",
        "max_dim": "maxdim",
        "sort": "sort",
        "limit": "limit",
        "globe": "globe",
        "namespace": "namespace",
        "prop": "prop",
        "primary": "primary",
    }
