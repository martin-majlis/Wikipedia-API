"""Async dictionary of AsyncWikipediaPage objects with batch methods.

Async mirror of PagesDict. Batch methods are coroutines.
"""

from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Mapping
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from .._enums import CoordinatesProp
from .._enums import CoordinateType
from .._enums import Direction
from .._enums import WikiCoordinatesProp
from .._enums import WikiCoordinateType
from .._enums import WikiDirection
from .._page._base_wikipedia_page import BaseWikipediaPage
from .base_pages_dict import _AsyncBatchWiki
from .pages_dict import PagesDict

if TYPE_CHECKING:
    from .._page.async_wikipedia_page import AsyncWikipediaPage
    from .._resources import BaseWikipediaResource
    from .._types import Coordinate
    from .._types import GeoPoint


class AsyncPagesDict(dict[str, BaseWikipediaPage[Any]]):
    """Async dictionary of :class:`AsyncWikipediaPage` objects with batch methods.

    Async mirror of :class:`PagesDict`.  Batch methods are coroutines.

    Args:
        wiki: The :class:`~wikipediaapi.AsyncWikipedia` client instance.
        data: Optional initial mapping of ``{title: AsyncWikipediaPage}``.
    """

    def __init__(
        self,
        wiki: BaseWikipediaResource | None = None,
        data: Mapping[str, BaseWikipediaPage[Any]] | None = None,
    ) -> None:
        """Initialise AsyncPagesDict with an optional wiki client and data.

        Args:
            wiki: The AsyncWikipedia client instance used for batch API calls.
                May be ``None`` for backward-compatible construction.
            data: Initial ``{title: page}`` mapping.
        """
        super().__init__(data or {})
        self._wiki = wiki

    async def coordinates(
        self,
        *,
        limit: int = 10,
        primary: WikiCoordinateType = CoordinateType.PRIMARY,
        prop: Iterable[WikiCoordinatesProp] = (CoordinatesProp.GLOBE,),
        distance_from_point: GeoPoint | None = None,
        distance_from_page: AsyncWikipediaPage | None = None,
    ) -> dict[AsyncWikipediaPage, list[Coordinate]]:
        """Async batch-fetch coordinates for all pages in this dict.

        Delegates to ``wiki.batch_coordinates()`` which sends multi-title
        API requests (up to 50 titles per request).

        Args:
            limit: Maximum coordinates per page (1–500).
            primary: Which coordinates: ``"primary"``, ``"secondary"``, ``"all"``.
            prop: Additional properties as an iterable.
            distance_from_point: Reference point as :class:`GeoPoint`.
            distance_from_page: Reference page.

        Returns:
            ``{page: [Coordinate, ...]}`` for every page in this dict.
        """
        wiki = cast(_AsyncBatchWiki, self._wiki)
        pages = cast("list[AsyncWikipediaPage]", list(self.values()))
        return await wiki.batch_coordinates(
            pages,
            limit=limit,
            primary=primary,
            prop=prop,
            distance_from_point=distance_from_point,
            distance_from_page=distance_from_page,
        )

    async def images(
        self,
        *,
        limit: int = 10,
        images: Iterable[str] | None = None,
        direction: WikiDirection = Direction.ASCENDING,
    ) -> dict[str, PagesDict]:
        """Async batch-fetch images for all pages in this dict.

        Delegates to ``wiki.batch_images()`` which sends multi-title
        API requests (up to 50 titles per request).

        Args:
            limit: Maximum images per page (1–500).
            images: Specific images as an iterable.
            direction: Sort direction as :class:`WikiDirection`.

        Returns:
            ``{title: PagesDict}`` for every page in this dict.
        """
        wiki = cast(_AsyncBatchWiki, self._wiki)
        pages = cast("list[AsyncWikipediaPage]", list(self.values()))
        return await wiki.batch_images(
            pages,
            limit=limit,
            images=images,
            direction=direction,
        )
