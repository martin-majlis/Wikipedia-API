"""Coordinate types for coordinates and geosearch methods.

This enum is used by ``coordinates`` and ``geosearch`` methods
in both sync and async APIs.
"""

from enum import Enum
from typing import Union


class CoordinateType(Enum):
    """Coordinate types for coordinates and geosearch methods.

    This enum is used by ``coordinates`` and ``geosearch`` methods
    in both sync and async APIs to specify which type of coordinates to return.
    """

    ALL = "all"
    """Return both primary and secondary coordinates."""
    PRIMARY = "primary"
    """Return only primary coordinates (location of article subject)."""
    SECONDARY = "secondary"
    """Return only secondary coordinates (locations of objects mentioned in article)."""


#: Type alias for primary coordinate arguments.
#: Accepts either a :class:`CoordinateType` enum member or a raw ``str``.
#: e.g. ``CoordinateType.ALL`` or simply ``"all"``.
WikiCoordinateType = Union[CoordinateType, str]


def coordinate_type2str(ctype: WikiCoordinateType) -> str:
    """
    Convert a :class:`WikiCoordinateType` value to a plain ``str``.

    If *ctype* is a :class:`CoordinateType` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    :param ctype: coordinate type to convert
    :return: string representation of the coordinate type

    **Examples:**

    .. code-block:: python

        from wikipediaapi import coordinate_type2str, CoordinateType

        # Convert enum to string
        assert coordinate_type2str(CoordinateType.ALL) == "all"
        assert coordinate_type2str(CoordinateType.PRIMARY) == "primary"
        assert coordinate_type2str(CoordinateType.SECONDARY) == "secondary"

        # String pass-through (unchanged)
        assert coordinate_type2str("all") == "all"
        assert coordinate_type2str("primary") == "primary"
        assert coordinate_type2str("secondary") == "secondary"

        # Custom values pass through
        assert coordinate_type2str("custom") == "custom"
    """
    if isinstance(ctype, CoordinateType):
        return ctype.value

    return ctype
