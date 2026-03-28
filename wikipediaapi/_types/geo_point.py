"""A geographic point with latitude/longitude validation.

Used as pythonic input for API parameters that previously required
MediaWiki's ``"lat|lon"`` string format.
"""

from __future__ import annotations

from dataclasses import dataclass


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
