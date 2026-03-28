"""Sort values for geosearch method.

This enum is used by the ``geosearch`` method in both sync and async APIs.
"""

from enum import Enum
from typing import Union


class GeoSearchSort(Enum):
    """Sort values for ``geosearch`` method."""

    DISTANCE = "distance"
    RELEVANCE = "relevance"


#: Type alias for geosearch sort arguments accepted by ``geosearch``.
#: Accepts either a :class:`GeoSearchSort` enum member or a raw ``str``.
#: e.g. ``GeoSearchSort.DISTANCE`` or simply ``"distance"``.
WikiGeoSearchSort = Union[GeoSearchSort, str]


def geosearch_sort2str(sort: WikiGeoSearchSort) -> str:
    """
    Convert a :class:`WikiGeoSearchSort` value to a plain ``str``.

    If *sort* is a :class:`GeoSearchSort` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    :param sort: geosearch sort direction to convert
    :return: string representation of the sort direction

    **Examples:**

    .. code-block:: python

        from wikipediaapi import geosearch_sort2str, GeoSearchSort

        # Convert enum to string
        assert geosearch_sort2str(GeoSearchSort.DISTANCE) == "distance"

        # String pass-through (unchanged)
        assert geosearch_sort2str("distance") == "distance"

        # Custom values pass through
        assert geosearch_sort2str("custom") == "custom"
    """
    if isinstance(sort, GeoSearchSort):
        return sort.value

    return sort
