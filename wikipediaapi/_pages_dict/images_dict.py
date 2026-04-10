"""Dictionary of WikipediaImage objects with batch imageinfo method.

Inherits from ``dict[str, WikipediaImage]`` and adds a reference to the
wiki client so that batch operations can be dispatched in a single API
call per chunk of 50 images.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from .._page._base_wikipedia_page import BaseWikipediaPage
from .._params.imageinfo_params import _DEFAULT_PROP
from .base_pages_dict import _SyncImageWiki

if TYPE_CHECKING:
    from .._image.wikipedia_image import WikipediaImage
    from .._resources import BaseWikipediaResource
    from .._types import ImageInfo


class ImagesDict(dict[str, BaseWikipediaPage[Any]]):
    """Dictionary of :class:`~wikipediaapi.WikipediaImage` objects with batch methods.

    Inherits from ``dict[str, WikipediaImage]`` and adds a reference to
    the wiki client so that batch operations can be dispatched in a
    single API call per chunk of 50 images.

    Args:
        wiki: The :class:`~wikipediaapi.Wikipedia` client instance.
        data: Optional initial mapping of ``{title: WikipediaImage}``.
    """

    def __init__(
        self,
        wiki: BaseWikipediaResource | None = None,
        data: Mapping[str, BaseWikipediaPage[Any]] | None = None,
    ) -> None:
        """Initialise ImagesDict with an optional wiki client and data.

        Args:
            wiki: The Wikipedia client instance used for batch API calls.
                May be ``None`` for backward-compatible construction.
            data: Initial ``{title: image}`` mapping.
        """
        super().__init__(data or {})
        self._wiki = wiki

    def imageinfo(
        self,
        *,
        prop: tuple[str, ...] = _DEFAULT_PROP,
        limit: int = 1,
    ) -> dict[str, list[ImageInfo]]:
        """Batch-fetch imageinfo for all images in this dict.

        Delegates to ``wiki.batch_imageinfo()`` which sends multi-title
        API requests (up to 50 titles per request).

        Args:
            prop: Tuple of ``iiprop`` field names controlling which fields
                are returned.
            limit: Maximum number of file revisions to return (1–500).

        Returns:
            ``{title: [ImageInfo, ...]}`` for every image in this dict.
        """
        wiki = cast(_SyncImageWiki, self._wiki)
        images = cast("list[WikipediaImage]", list(self.values()))
        return wiki.batch_imageinfo(images, prop=prop, limit=limit)
