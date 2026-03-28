"""Sort direction values for image query methods.

This enum is used by ``images`` and ``batch_images`` methods in both
sync and async APIs.
"""

from enum import Enum
from typing import Union


class Direction(Enum):
    """Sort direction values for image query methods.

    This enum is used by ``images`` and ``batch_images`` methods in both
    sync and async APIs.
    """

    ASCENDING = "ascending"
    DESCENDING = "descending"


#: Type alias for direction arguments accepted throughout the library.
#: Accepts either a :class:`Direction` enum member or a raw ``str`,
#: e.g. ``Direction.ASCENDING`` or simply ``"ascending"``.
WikiDirection = Union[Direction, str]


def direction2str(direction: WikiDirection) -> str:
    """
    Convert a :class:`WikiDirection` value to a plain ``str``.

    If *direction* is a :class:`Direction` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    :param direction: direction to convert
    :return: string representation of the direction

    **Examples:**

    .. code-block:: python

        from wikipediaapi import direction2str, Direction

        # Convert enum to string
        assert direction2str(Direction.ASCENDING) == "ascending"

        # String pass-through (unchanged)
        assert direction2str("ascending") == "ascending"

        # Custom values pass through
        assert direction2str("custom") == "custom"
    """
    if isinstance(direction, Direction):
        return direction.value

    return direction
