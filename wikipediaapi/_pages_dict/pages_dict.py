"""Dictionary of WikipediaPage objects with batch methods.

Inherits from ``dict[str, WikipediaPage]`` and adds a reference to
wiki client so that batch operations can be dispatched in a
single API call per chunk of 50 pages.
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
from .base_pages_dict import _SyncBatchWiki

if TYPE_CHECKING:
    from .._page.wikipedia_page import WikipediaPage
    from .._resources import BaseWikipediaResource
    from .._types import Coordinate
    from .._types import GeoPoint


class PagesDict(dict[str, BaseWikipediaPage[Any]]):
    """Dictionary of :class:`WikipediaPage` objects with batch methods.

    Inherits from ``dict[str, WikipediaPage]`` and adds a reference to
    wiki client so that batch operations can be dispatched in a
    single API call per chunk of 50 pages.

    Args:
        wiki: The :class:`~wikipediaapi.Wikipedia` client instance.
        data: Optional initial mapping of ``{title: WikipediaPage}``.
    """

    def __init__(
        self,
        wiki: BaseWikipediaResource | None = None,
        data: Mapping[str, BaseWikipediaPage[Any]] | None = None,
    ) -> None:
        """Initialise PagesDict with an optional wiki client and data.

        Args:
            wiki: The Wikipedia client instance used for batch API calls.
                May be ``None`` for backward-compatible construction.
            data: Initial ``{title: page}`` mapping.
        """
        super().__init__(data or {})
        self._wiki = wiki

    def coordinates(
        self,
        *,
        limit: int = 10,
        primary: WikiCoordinateType = CoordinateType.PRIMARY,
        prop: Iterable[WikiCoordinatesProp] = (CoordinatesProp.GLOBE,),
        distance_from_point: GeoPoint | None = None,
        distance_from_page: WikipediaPage | None = None,
    ) -> dict[WikipediaPage, list[Coordinate]]:
        """Batch-fetch coordinates for all pages in this dict.

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
        wiki = cast(_SyncBatchWiki, self._wiki)
        pages = cast("list[WikipediaPage]", list(self.values()))
        return wiki.batch_coordinates(
            pages,
            limit=limit,
            primary=primary,
            prop=prop,
            distance_from_point=distance_from_point,
            distance_from_page=distance_from_page,
        )

    def images(
        self,
        *,
        limit: int = 10,
        images: Iterable[str] | None = None,
        direction: WikiDirection = Direction.ASCENDING,
    ) -> dict[str, PagesDict]:
        """Batch-fetch images for all pages in this dict.

        Delegates to ``wiki.batch_images()`` which sends multi-title
        API requests (up to 50 titles per request).

        Args:
            limit: Maximum images per page (1–500).
            images: Specific images as an iterable.
            direction: Sort direction as :class:`WikiDirection`.

        Returns:
            ``{title: PagesDict}`` for every page in this dict.
        """
        wiki = cast(_SyncBatchWiki, self._wiki)
        pages = cast("list[WikipediaPage]", list(self.values()))
        return wiki.batch_images(
            pages,
            limit=limit,
            images=images,
            direction=direction,
        )
