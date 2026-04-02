"""Parameters for prop=coordinates (prefix co).

Args:
    limit: Maximum number of coordinates to return (1–500).
    primary: Which coordinates to return: "primary", "secondary", or "all".
    prop: Additional coordinate properties as an iterable
        (e.g. ["type", "name", "globe"]).
    distance_from_point: Return distance from this geographic point.
    distance_from_page: Return distance from coordinates of this page title.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import ClassVar

from .._enums import CoordinatesProp
from .._enums import CoordinateType
from .._enums import WikiCoordinatesProp
from .._enums import WikiCoordinateType
from .._enums import coordinate_type2str
from .._enums import coordinates_prop2str
from .._types import GeoPoint
from .base_params import _BaseParams
from .protocols import _HasTitle


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
        distance_from_page: Return distance from coordinates of
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
