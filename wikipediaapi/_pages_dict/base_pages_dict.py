"""Base class for page dictionaries.

Provides the foundation for both sync and async page dictionaries.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Protocol

from .._enums import (
    CoordinatesProp,
    CoordinateType,
    Direction,
    WikiCoordinatesProp,
    WikiCoordinateType,
    WikiDirection,
)

if TYPE_CHECKING:
    from typing import Any, cast  # noqa: F401

    from .._base_wikipedia_page import BaseWikipediaPage  # noqa: F401
    from .._resources import BaseWikipediaResource  # noqa: F401
    from .._types import (
        Coordinate,  # noqa: F401
        GeoPoint,  # noqa: F401
        ImageInfo,  # noqa: F401
    )
    from ..async_wikipedia_image import AsyncWikipediaImage  # noqa: F401
    from ..async_wikipedia_page import AsyncWikipediaPage  # noqa: F401
    from ..wikipedia_image import WikipediaImage  # noqa: F401
    from ..wikipedia_page import WikipediaPage  # noqa: F401
    from .async_pages_dict import AsyncPagesDict  # noqa: F401
    from .pages_dict import PagesDict  # noqa: F401


class _SyncBatchWiki(Protocol):
    def batch_coordinates(
        self,
        pages: list[WikipediaPage],
        *,
        limit: int = 10,
        primary: WikiCoordinateType = CoordinateType.PRIMARY,
        prop: Iterable[WikiCoordinatesProp] = (CoordinatesProp.GLOBE,),
        distance_from_point: GeoPoint | None = None,
        distance_from_page: WikipediaPage | None = None,
    ) -> dict[WikipediaPage, list[Coordinate]]: ...

    def batch_images(
        self,
        pages: list[WikipediaPage],
        *,
        limit: int = 10,
        images: Iterable[str] | None = None,
        direction: WikiDirection = Direction.ASCENDING,
    ) -> dict[str, PagesDict]: ...


class _AsyncBatchWiki(Protocol):
    async def batch_coordinates(
        self,
        pages: list[AsyncWikipediaPage],
        *,
        limit: int = 10,
        primary: WikiCoordinateType = CoordinateType.PRIMARY,
        prop: Iterable[WikiCoordinatesProp] = (CoordinatesProp.GLOBE,),
        distance_from_point: GeoPoint | None = None,
        distance_from_page: AsyncWikipediaPage | None = None,
    ) -> dict[AsyncWikipediaPage, list[Coordinate]]: ...

    async def batch_images(
        self,
        pages: list[AsyncWikipediaPage],
        *,
        limit: int = 10,
        images: Iterable[str] | None = None,
        direction: WikiDirection = Direction.ASCENDING,
    ) -> dict[str, PagesDict]: ...


class _SyncImageWiki(Protocol):
    def batch_imageinfo(
        self,
        images: list[WikipediaImage],
        *,
        prop: tuple[str, ...] = ...,
        limit: int = 1,
    ) -> dict[str, list[ImageInfo]]: ...


class _AsyncImageWiki(Protocol):
    async def batch_imageinfo(
        self,
        images: list[AsyncWikipediaImage],
        *,
        prop: tuple[str, ...] = ...,
        limit: int = 1,
    ) -> dict[str, list[ImageInfo]]: ...
