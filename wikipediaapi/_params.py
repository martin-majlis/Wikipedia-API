"""Internal parameter dataclasses for MediaWiki query submodules.

Each dataclass maps clean Python parameter names to their MediaWiki
API equivalents (which use module-specific prefixes like ``co``, ``gs``,
``im``, ``rn``, ``sr``).  The :meth:`to_api` method produces a dict
ready to merge into an API request.

These classes are **not** part of the public API; they are used internally
by ``_resources.py`` to convert explicit method signatures into API params.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import fields
from typing import Any, ClassVar


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


@dataclass(frozen=True)
class CoordinatesParams(_BaseParams):
    """Parameters for ``prop=coordinates`` (prefix ``co``).

    Args:
        limit: Maximum number of coordinates to return (1–500).
        primary: Which coordinates to return: ``"primary"``,
            ``"secondary"``, or ``"all"``.
        prop: Additional coordinate properties to include, pipe-separated
            (e.g. ``"type|name|dim|country|region|globe"``).
        distance_from_point: Return distance from this point; format
            ``"lat|lon"`` (e.g. ``"37.787|-122.4"``).
        distance_from_page: Return distance from the coordinates of
            this page title.
    """

    limit: int = 10
    primary: str = "primary"
    prop: str = "globe"
    distance_from_point: str | None = None
    distance_from_page: str | None = None

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
        images: Only list these specific images (pipe-separated titles).
        direction: Sort direction: ``"ascending"`` or ``"descending"``.
    """

    limit: int = 10
    images: str | None = None
    direction: str = "ascending"

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
        coord: Centre point as ``"lat|lon"`` (e.g. ``"37.787|-122.4"``).
        page: Title of page whose coordinates to use as centre.
        bbox: Bounding box as ``"top_lat|left_lon|bottom_lat|right_lon"``.
        radius: Search radius in meters (10–10000).
        max_dim: Exclude objects larger than this many meters.
        sort: Sort order: ``"distance"`` or ``"relevance"``.
        limit: Maximum pages to return (1–500).
        globe: Celestial body: ``"earth"``, ``"mars"``, ``"moon"``, ``"venus"``.
        namespace: Restrict to this namespace number.
        prop: Additional properties, pipe-separated.
        primary: Which coordinates to consider: ``"primary"``,
            ``"secondary"``, or ``"all"``.
    """

    coord: str | None = None
    page: str | None = None
    bbox: str | None = None
    radius: int = 500
    max_dim: int | None = None
    sort: str = "distance"
    limit: int = 10
    globe: str = "earth"
    namespace: int | None = None
    prop: str | None = None
    primary: str | None = None

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

    namespace: int | None = None
    filter_redirect: str = "nonredirects"
    min_size: int | None = None
    max_size: int | None = None
    limit: int = 1

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
        prop: Properties to include, pipe-separated (deprecated upstream).
        info: Metadata to return, pipe-separated
            (e.g. ``"totalhits|suggestion|rewrittenquery"``).
        sort: Sort order (e.g. ``"relevance"``, ``"last_edit_desc"``).
        what: Search type: ``"title"``, ``"text"``, or ``"nearmatch"``.
        interwiki: Include interwiki results.
        enable_rewrites: Allow the backend to rewrite the query.
        qi_profile: Query-independent ranking profile.
    """

    query: str = ""
    namespace: int = 0
    limit: int = 10
    prop: str | None = None
    info: str | None = None
    sort: str = "relevance"
    what: str | None = None
    interwiki: bool = False
    enable_rewrites: bool = False
    qi_profile: str | None = None

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
