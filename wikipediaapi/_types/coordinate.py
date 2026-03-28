"""A single geographic coordinate associated with a Wikipedia page.

Represents one entry from ``prop=coordinates`` API response.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinate:
    """A single geographic coordinate associated with a Wikipedia page.

    Represents one entry from ``prop=coordinates`` API response.
    Always contains ``lat``, ``lon``, and ``primary``; additional fields
    are populated when requested via ``prop`` parameter.

    Args:
        lat: Latitude in decimal degrees.
        lon: Longitude in decimal degrees.
        primary: True if this is primary coordinate for page.
        globe: Celestial body coordinates refer to.
        type: Type of geographic object (e.g. ``"city"``).
        name: Name of geographic object.
        dim: Approximate size of object in meters.
        country: ISO 3166-1 alpha-2 country code.
        region: ISO 3166-2 region code (part after dash).
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
