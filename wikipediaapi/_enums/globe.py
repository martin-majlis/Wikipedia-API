"""Globe values for geosearch and coordinates methods.

This enum is used by ``geosearch`` and ``coordinates`` methods
in both sync and async APIs.
"""

from enum import Enum
from typing import Union


class Globe(Enum):
    """Globe values for geosearch and coordinates methods.

    This enum is used by ``geosearch`` and ``coordinates`` methods
    in both sync and async APIs.
    """

    EARTH = "earth"
    MARS = "mars"
    MOON = "moon"
    VENUS = "venus"


#: Type alias for globe arguments accepted by geosearch methods.
#: Accepts either a :class:`Globe` enum member or a raw ``str``.
#: e.g. ``Globe.EARTH`` or simply ``"earth"``.
WikiGlobe = Union[Globe, str]


def globe2str(globe: WikiGlobe) -> str:
    """
    Convert a :class:`WikiGlobe` value to a plain ``str``.

    If *globe* is a :class:`Globe` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    :param globe: globe to convert
    :return: string representation of the globe

    **Examples:**

    .. code-block:: python

        from wikipediaapi import globe2str, Globe

        # Convert enum to string
        assert globe2str(Globe.EARTH) == "earth"

        # String pass-through (unchanged)
        assert globe2str("earth") == "earth"

        # Custom values pass through
        assert globe2str("custom") == "custom"
    """
    if isinstance(globe, Globe):
        return globe.value

    return globe
