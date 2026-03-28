"""Property values for coordinates query methods.

This enum is used by ``coordinates`` and ``batch_coordinates`` methods
in both sync and async APIs to specify which additional coordinate properties
to return from the MediaWiki API.
"""

from enum import Enum
from typing import Union


class CoordinatesProp(Enum):
    """Property values for coordinates query methods.

    This enum is used by ``coordinates`` and ``batch_coordinates`` methods
    in both sync and async APIs to specify which additional coordinate properties
    to return from the MediaWiki API.
    """

    COUNTRY = "country"
    """ISO 3166-1 alpha-2 country code (e.g. US or RU)."""
    DIM = "dim"
    """Approximate size of the object in meters."""
    GLOBE = "globe"
    """Which terrestrial body coordinates are relative to (e.g. moon or pluto)."""
    NAME = "name"
    """Name of the object the coordinates point to."""
    REGION = "region"
    """ISO 3166-2 region code (the part after the dash; e.g. FL or MOS)."""
    TYPE = "type"
    """Type of the object the coordinates point to."""


#: Type alias for coordinates property arguments.
#: Accepts either a :class:`CoordinatesProp` enum member or a raw ``str``.
#: e.g. ``CoordinatesProp.GLOBE`` or simply ``"globe"``.
WikiCoordinatesProp = Union[CoordinatesProp, str]


def coordinates_prop2str(prop: WikiCoordinatesProp) -> str:
    """
    Convert a :class:`WikiCoordinatesProp` value to a plain ``str``.

    If *prop* is a :class:`CoordinatesProp` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    :param prop: coordinates property to convert
    :return: string representation of the coordinates property

    **Examples:**

    .. code-block:: python

        from wikipediaapi import coordinates_prop2str, CoordinatesProp

        # Convert enum to string
        assert coordinates_prop2str(CoordinatesProp.GLOBE) == "globe"
        assert coordinates_prop2str(CoordinatesProp.COUNTRY) == "country"
        assert coordinates_prop2str(CoordinatesProp.DIM) == "dim"
        assert coordinates_prop2str(CoordinatesProp.NAME) == "name"
        assert coordinates_prop2str(CoordinatesProp.REGION) == "region"
        assert coordinates_prop2str(CoordinatesProp.TYPE) == "type"

        # String pass-through (unchanged)
        assert coordinates_prop2str("globe") == "globe"
        assert coordinates_prop2str("country") == "country"
        assert coordinates_prop2str("dim") == "dim"
        assert coordinates_prop2str("name") == "name"
        assert coordinates_prop2str("region") == "region"
        assert coordinates_prop2str("type") == "type"

        # Custom values pass through
        assert coordinates_prop2str("custom") == "custom"
    """
    if isinstance(prop, CoordinatesProp):
        return prop.value

    return prop
