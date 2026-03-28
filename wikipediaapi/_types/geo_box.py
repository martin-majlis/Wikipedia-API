"""A geographic bounding box defined by two validated corner points.

Represents MediaWiki's ``gsbbox`` value in a pythonic structured way.
"""

from __future__ import annotations

from dataclasses import dataclass

from .geo_point import GeoPoint


@dataclass(frozen=True)
class GeoBox:
    """A geographic bounding box defined by two validated corner points.

    Represents MediaWiki's ``gsbbox`` value in a pythonic structured way.

    Args:
        top_left: Top-left corner of box.
        bottom_right: Bottom-right corner of box.

    Raises:
        ValueError: If top-left latitude is smaller than bottom-right latitude.
        ValueError: If top-left longitude is greater than bottom-right longitude.
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
