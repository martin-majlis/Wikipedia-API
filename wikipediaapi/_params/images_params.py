"""Parameters for prop=images (prefix im).

Args:
    limit: Maximum number of images to return (1–500).
    images: Specific images as an iterable.
    direction: Sort direction as WikiDirection.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import ClassVar

from .._enums import Direction
from .._enums import WikiDirection
from .._enums import direction2str
from .base_params import _BaseParams


@dataclass(frozen=True)
class ImagesParams(_BaseParams):
    """Parameters for ``prop=images`` (prefix ``im``).

    Args:
        limit: Maximum number of images to return (1–500).
        images: Specific images as an iterable.
        direction: Sort direction as :class:`~wikipediaapi.WikiDirection`.
    """

    limit: int = 10
    images: Iterable[str] | None = None
    direction: WikiDirection = Direction.ASCENDING

    def __post_init__(self) -> None:
        """Normalize iterable image titles and reject string input.

        Converts the iterable ``images`` value into the MediaWiki-required
        pipe-separated string representation when provided.

        Raises:
            TypeError: If ``images`` is passed as a string instead of an iterable.
            TypeError: If ``direction`` is not a :class:`WikiDirection`.
        """
        if not isinstance(self.direction, (Direction, str)):
            raise TypeError("ImagesParams.direction must be Direction or str")
        object.__setattr__(self, "direction", direction2str(self.direction))
        if self.images is None:
            return
        if isinstance(self.images, str):
            raise TypeError("ImagesParams.images must be an iterable of strings, not str")
        object.__setattr__(self, "images", "|".join(self.images))

    PREFIX: ClassVar[str] = "im"
    FIELD_MAP: ClassVar[dict[str, str]] = {
        "limit": "limit",
        "images": "images",
        "direction": "dir",
    }
