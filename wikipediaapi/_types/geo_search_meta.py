"""Contextual metadata attached to pages returned by a geosearch query.

Accessible via ``page.geosearch_meta`` on pages produced by
``wiki.geosearch()``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeoSearchMeta:
    """Contextual metadata attached to pages returned by a geosearch query.

    Accessible via ``page.geosearch_meta`` on pages produced by
    ``wiki.geosearch()``.  Contains distance from search centre
    and coordinate that was matched.

    Args:
        dist: Distance in meters from search centre.
        lat: Latitude of matched coordinate.
        lon: Longitude of matched coordinate.
        primary: True if matched coordinate is the primary one.
    """

    dist: float
    lat: float
    lon: float
    primary: bool
