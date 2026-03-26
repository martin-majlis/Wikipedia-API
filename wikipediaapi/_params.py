"""Internal parameter dataclasses for MediaWiki query submodules.

Each dataclass maps clean Python parameter names to their MediaWiki
API equivalents (which use module-specific prefixes like ``co``, ``gs``,
``im``, ``rn``, ``sr``).  The :meth:`to_api` method produces a dict
ready to merge into an API request.

These classes are **not** part of the public API; they are used internally
by ``_resources.py`` to convert explicit method signatures into API params.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import fields
from enum import Enum
from typing import Any, ClassVar, Protocol

from ._enums import coordinate_type2str
from ._enums import coordinates_prop2str
from ._enums import CoordinatesProp
from ._enums import CoordinateType
from ._enums import Direction
from ._enums import direction2str
from ._enums import geosearch_sort2str
from ._enums import GeoSearchSort
from ._enums import Globe
from ._enums import globe2str
from ._enums import redirect_filter2str
from ._enums import RedirectFilter
from ._enums import search_sort2str
from ._enums import SearchSort
from ._enums import WikiCoordinatesProp
from ._enums import WikiCoordinateType
from ._enums import WikiDirection
from ._enums import WikiGeoSearchSort
from ._enums import WikiGlobe
from ._enums import WikiRedirectFilter
from ._enums import WikiSearchSort
from ._types import GeoBox
from ._types import GeoPoint
from .namespace import Namespace
from .namespace import WikiNamespace


class _BaseParams:
    """Mixin providing the ``to_api()`` and ``cache_key()`` methods.

    Subclasses must define ``PREFIX`` and ``FIELD_MAP`` class attributes.

    Invariants:
        - ``PREFIX`` is the MediaWiki module prefix (e.g. ``"co"``).
        - ``FIELD_MAP`` maps Python field names to MW suffixes
          (e.g. ``{"limit": "limit", "distance_from_point": "distancefrompoint"}``).
    """

    PREFIX: ClassVar[str] = ""
    FIELD_MAP: ClassVar[dict[str, str]] = {}

    def to_api(self) -> dict[str, str]:
        """Convert clean Python params to prefixed MediaWiki API params.

        Iterates over ``FIELD_MAP``, reads the corresponding attribute
        value, and emits ``{PREFIX}{suffix}: str(value)}`` for every
        non-None field.  Boolean ``False`` values are skipped.

        Returns:
            Dictionary of ``{api_param_name: string_value}`` pairs ready
            to merge into an API request.
        """
        result: dict[str, str] = {}
        for field_name, api_suffix in self.FIELD_MAP.items():
            val = getattr(self, field_name)
            if val is None:
                continue
            if isinstance(val, bool):
                if val:
                    result[f"{self.PREFIX}{api_suffix}"] = "1"
                continue
            if isinstance(val, Enum):
                result[f"{self.PREFIX}{api_suffix}"] = str(val.value)
                continue
            result[f"{self.PREFIX}{api_suffix}"] = str(val)
        return result

    def cache_key(self) -> tuple[tuple[str, Any], ...]:
        """Return a hashable key representing this parameter set.

        Used by the per-param cache on page objects to distinguish
        results fetched with different parameters.

        Returns:
            Tuple of ``(field_name, value)`` pairs, sorted by field name.
        """
        return tuple(
            sorted((f.name, getattr(self, f.name)) for f in fields(self))  # type: ignore[arg-type]
        )


class _HasTitle(Protocol):
    @property
    def title(self) -> str: ...


@dataclass(frozen=True)
class CoordinatesParams(_BaseParams):
    """Parameters for ``prop=coordinates`` (prefix ``co``).

    Args:
        limit: Maximum number of coordinates to return (1–500).
        primary: Which coordinates to return: ``"primary"``,
            ``"secondary"``, or ``"all"``.
        prop: Additional coordinate properties as an iterable
            (e.g. ``["type", "name", "globe"]``).
        distance_from_point: Return distance from this geographic point.
        distance_from_page: Return distance from the coordinates of
            this page title.
    """

    limit: int = 10
    primary: WikiCoordinateType = CoordinateType.PRIMARY
    prop: Iterable[WikiCoordinatesProp] = (CoordinatesProp.GLOBE,)
    distance_from_point: GeoPoint | None = None
    distance_from_page: _HasTitle | None = None

    def __post_init__(self) -> None:
        """Normalize iterable props and reject string input.

        Converts the iterable ``prop`` value into the MediaWiki-required
        pipe-separated string representation.

        Raises:
            TypeError: If ``prop`` is passed as a string instead of an iterable.
        """
        if not isinstance(self.primary, (CoordinateType, str)):
            raise TypeError("CoordinatesParams.primary must be CoordinateType or str")
        object.__setattr__(self, "primary", coordinate_type2str(self.primary))

        if isinstance(self.prop, str):
            raise TypeError(
                "CoordinatesParams.prop must be an iterable of WikiCoordinatesProp, not str"
            )
        converted_props = [coordinates_prop2str(p) for p in self.prop]
        object.__setattr__(self, "prop", "|".join(converted_props))
        if self.distance_from_point is not None:
            if not isinstance(self.distance_from_point, GeoPoint):
                raise TypeError("CoordinatesParams.distance_from_point must be GeoPoint or None")
            object.__setattr__(
                self,
                "distance_from_point",
                self.distance_from_point.to_mediawiki(),
            )
        if self.distance_from_page is not None:
            object.__setattr__(self, "distance_from_page", self.distance_from_page.title)

    PREFIX: ClassVar[str] = "co"
    FIELD_MAP: ClassVar[dict[str, str]] = {
        "limit": "limit",
        "primary": "primary",
        "prop": "prop",
        "distance_from_point": "distancefrompoint",
        "distance_from_page": "distancefrompage",
    }


@dataclass(frozen=True)
class ImagesParams(_BaseParams):
    """Parameters for ``prop=images`` (prefix ``im``).

    Args:
        limit: Maximum number of images to return (1–500).
        images: Specific images as an iterable.
        direction: Sort direction as :class:`~wikipediaapi.WikiDirection`.
    """

    limit: int = 10
    images: Iterable[str] | None = None
    direction: WikiDirection = Direction.ASCENDING

    def __post_init__(self) -> None:
        """Normalize iterable image titles and reject string input.

        Converts the iterable ``images`` value into the MediaWiki-required
        pipe-separated string representation when provided.

        Raises:
            TypeError: If ``images`` is passed as a string instead of an iterable.
            TypeError: If ``direction`` is not a :class:`WikiDirection`.
        """
        if not isinstance(self.direction, (Direction, str)):
            raise TypeError("ImagesParams.direction must be Direction or str")
        object.__setattr__(self, "direction", direction2str(self.direction))
        if self.images is None:
            return
        if isinstance(self.images, str):
            raise TypeError("ImagesParams.images must be an iterable of strings, not str")
        object.__setattr__(self, "images", "|".join(self.images))

    PREFIX: ClassVar[str] = "im"
    FIELD_MAP: ClassVar[dict[str, str]] = {
        "limit": "limit",
        "images": "images",
        "direction": "dir",
    }


@dataclass(frozen=True)
class GeoSearchParams(_BaseParams):
    """Parameters for ``list=geosearch`` (prefix ``gs``).

    At least one of ``coord``, ``page``, or ``bbox`` must be provided.

    Args:
        coord: Centre point as :class:`~wikipediaapi.GeoPoint`.
        page: Title of page whose coordinates to use as centre.
        bbox: Bounding box as :class:`~wikipediaapi.GeoBox`.
        radius: Search radius in meters (10–10000).
        max_dim: Exclude objects larger than this many meters.
        sort: Sort order: ``"distance"`` or ``"relevance"``.
        limit: Maximum pages to return (1–500).
        globe: Celestial body: ``"earth"``, ``"mars"``, ``"moon"``, ``"venus"``.
        namespace: Restrict to this namespace number.
        prop: Additional properties as an iterable.
        primary: Which coordinates to consider: ``"primary"``,
            ``"secondary"``, or ``"all"``.
    """

    coord: GeoPoint | None = None
    page: str | None = None
    bbox: GeoBox | None = None
    radius: int = 500
    max_dim: int | None = None
    sort: WikiGeoSearchSort = GeoSearchSort.DISTANCE
    limit: int = 10
    globe: WikiGlobe = Globe.EARTH
    namespace: WikiNamespace = Namespace.MAIN
    prop: Iterable[str] | None = None
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
        if self.prop is not None:
            if isinstance(self.prop, str):
                raise TypeError("GeoSearchParams.prop must be an iterable of strings, not str")
            object.__setattr__(self, "prop", "|".join(self.prop))

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


@dataclass(frozen=True)
class RandomParams(_BaseParams):
    """Parameters for ``list=random`` (prefix ``rn``).

    Args:
        namespace: Restrict to this namespace number.
        filter_redirect: Redirect filter: ``"all"``, ``"nonredirects"``,
            or ``"redirects"``.
        min_size: Minimum page size in bytes.
        max_size: Maximum page size in bytes.
        limit: Number of random pages to return (1–500).
    """

    namespace: WikiNamespace = Namespace.MAIN
    filter_redirect: WikiRedirectFilter = RedirectFilter.NONREDIRECTS
    min_size: int | None = None
    max_size: int | None = None
    limit: int = 1

    def __post_init__(self) -> None:
        """Normalize filter_redirect properly.

        Raises:
            TypeError: If ``filter_redirect`` is not a RedirectFilter or str.
        """
        if not isinstance(self.filter_redirect, (RedirectFilter, str)):
            raise TypeError("RandomParams.filter_redirect must be RedirectFilter or str")
        object.__setattr__(self, "filter_redirect", redirect_filter2str(self.filter_redirect))

    PREFIX: ClassVar[str] = "rn"
    FIELD_MAP: ClassVar[dict[str, str]] = {
        "namespace": "namespace",
        "filter_redirect": "filterredir",
        "min_size": "minsize",
        "max_size": "maxsize",
        "limit": "limit",
    }


@dataclass(frozen=True)
class SearchParams(_BaseParams):
    """Parameters for ``list=search`` (prefix ``sr``).

    Args:
        query: Search string (required).
        namespace: Namespace to search in.
        limit: Maximum results to return (1–500).
        prop: Properties as an iterable (deprecated upstream).
        info: Metadata as an iterable
            (e.g. ``["totalhits", "suggestion", "rewrittenquery"]``).
        sort: Sort order (e.g. ``"relevance"``, ``"last_edit_desc"``).
        what: Search type: ``"title"``, ``"text"``, or ``"nearmatch"``.
        interwiki: Include interwiki results.
        enable_rewrites: Allow the backend to rewrite the query.
        qi_profile: Query-independent ranking profile.
    """

    query: str = ""
    namespace: WikiNamespace = Namespace.MAIN
    limit: int = 10
    prop: Iterable[str] | None = None
    info: Iterable[str] | None = None
    sort: WikiSearchSort = SearchSort.RELEVANCE
    what: str | None = None
    interwiki: bool = False
    enable_rewrites: bool = False
    qi_profile: str | None = None

    def __post_init__(self) -> None:
        """Normalize iterable search properties and reject string input.

        Converts iterable ``prop`` and ``info`` values into MediaWiki-required
        pipe-separated string representations when provided.

        Raises:
            TypeError: If ``prop`` or ``info`` is passed as a string instead
                of an iterable.
        """
        if not isinstance(self.sort, (SearchSort, str)):
            raise TypeError("SearchParams.sort must be SearchSort or str")
        object.__setattr__(self, "sort", search_sort2str(self.sort))

        if self.prop is not None:
            if isinstance(self.prop, str):
                raise TypeError("SearchParams.prop must be an iterable of strings, not str")
            object.__setattr__(self, "prop", "|".join(self.prop))
        if self.info is not None:
            if isinstance(self.info, str):
                raise TypeError("SearchParams.info must be an iterable of strings, not str")
            object.__setattr__(self, "info", "|".join(self.info))

    PREFIX: ClassVar[str] = "sr"
    FIELD_MAP: ClassVar[dict[str, str]] = {
        "query": "search",
        "namespace": "namespace",
        "limit": "limit",
        "prop": "prop",
        "info": "info",
        "sort": "sort",
        "what": "what",
        "interwiki": "interwiki",
        "enable_rewrites": "enablerewrites",
        "qi_profile": "qiprofile",
    }
