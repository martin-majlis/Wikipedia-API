"""Async dictionary of AsyncWikipediaImage objects with batch imageinfo method.

Async mirror of ImagesDict. Batch methods are coroutines.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from .._page._base_wikipedia_page import BaseWikipediaPage
from .._params.imageinfo_params import _DEFAULT_PROP
from .base_pages_dict import _AsyncImageWiki

if TYPE_CHECKING:
    from .._image.async_wikipedia_image import AsyncWikipediaImage
    from .._resources import BaseWikipediaResource
    from .._types import ImageInfo


class AsyncImagesDict(dict[str, BaseWikipediaPage[Any]]):
    """Async dictionary of :class:`~wikipediaapi.AsyncWikipediaImage` objects.

    Async mirror of :class:`ImagesDict`.  Batch methods are coroutines.

    Args:
        wiki: The :class:`~wikipediaapi.AsyncWikipedia` client instance.
        data: Optional initial mapping of ``{title: AsyncWikipediaImage}``.
    """

    def __init__(
        self,
        wiki: BaseWikipediaResource | None = None,
        data: Mapping[str, BaseWikipediaPage[Any]] | None = None,
    ) -> None:
        """Initialise AsyncImagesDict with an optional wiki client and data.

        Args:
            wiki: The AsyncWikipedia client instance used for batch API calls.
                May be ``None`` for backward-compatible construction.
            data: Initial ``{title: image}`` mapping.
        """
        super().__init__(data or {})
        self._wiki = wiki

    async def imageinfo(
        self,
        *,
        prop: tuple[str, ...] = _DEFAULT_PROP,
        limit: int = 1,
    ) -> dict[str, list[ImageInfo]]:
        """Async batch-fetch imageinfo for all images in this dict.

        Delegates to ``wiki.batch_imageinfo()`` which sends multi-title
        API requests (up to 50 titles per request).

        Args:
            prop: Tuple of ``iiprop`` field names controlling which fields
                are returned.
            limit: Maximum number of file revisions to return (1–500).

        Returns:
            ``{title: [ImageInfo, ...]}`` for every image in this dict.
        """
        wiki = cast(_AsyncImageWiki, self._wiki)
        images = cast("list[AsyncWikipediaImage]", list(self.values()))
        return await wiki.batch_imageinfo(images, prop=prop, limit=limit)
