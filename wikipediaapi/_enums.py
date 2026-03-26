"""Shared enum definitions for Wikipedia API options."""

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
#: Accepts either a :class:`Direction` enum member or a raw ``str``,
#: e.g. ``Direction.ASCENDING`` or simply ``"ascending"``.
WikiDirection = Union[Direction, str]


def direction2str(direction: WikiDirection) -> str:
    """
    Convert a :class:`WikiDirection` value to a plain ``str``.

    If *direction* is a :class:`Direction` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    :param direction: direction to convert
    :return: string representation of the direction
    """
    if isinstance(direction, Direction):
        return direction.value

    return direction
