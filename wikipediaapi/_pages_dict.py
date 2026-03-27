"""Batch-capable page dictionaries for sync and async contexts.

Replaces the former ``PagesDict = dict[str, WikipediaPage]`` type alias
with a proper ``dict`` subclass that carries a back-reference to the wiki
client and exposes batch-fetching methods for the new query submodules.

Backward compatible: ``PagesDict`` subclasses ``dict``, so all existing
code that treats it as a plain dict continues to work.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, cast, Protocol, TYPE_CHECKING

from ._base_wikipedia_page import BaseWikipediaPage
from ._enums import CoordinatesProp
from ._enums import CoordinateType
from ._enums import Direction
from ._enums import ImageInfoProp
from ._enums import WikiCoordinatesProp
from ._enums import WikiCoordinateType
from ._enums import WikiDirection
from ._enums import WikiImageInfoProp
from .async_wikipedia_image import AsyncWikipediaImage
from .wikipedia_image import WikipediaImage

if TYPE_CHECKING:
    from ._resources import BaseWikipediaResource
    from ._types import Coordinate
    from ._types import GeoPoint
    from .async_wikipedia_page import AsyncWikipediaPage
    from .wikipedia_page import WikipediaPage


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


class PagesDict(dict[str, BaseWikipediaPage[Any]]):
    """Dictionary of :class:`WikipediaPage` objects with batch methods.

    Inherits from ``dict[str, WikipediaPage]`` and adds a reference to
    the wiki client so that batch operations can be dispatched in a
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
        """Initialise the PagesDict with an optional wiki client and data.

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
        """Initialise the AsyncPagesDict with an optional wiki client and data.

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


class ImagesDict(dict[str, WikipediaImage]):
    """Dictionary of WikipediaImage objects with batch operations support.

    Subclass of ``dict`` that carries a back-reference to the wiki client
    and exposes batch-fetching methods for image information operations.

    Backward compatible: ``ImagesDict`` subclasses ``dict``, so all existing
    code that treats it as a plain dict continues to work.
    """

    def __init__(self, wiki: Any, *args: Any, **kwargs: Any) -> None:
        """Initialize ImagesDict with wiki reference.

        Args:
            wiki: The Wikipedia client instance.
            *args: Positional arguments passed to dict.__init__.
            **kwargs: Keyword arguments passed to dict.__init__.
        """
        super().__init__(*args, **kwargs)
        self._wiki: Any = wiki

    def imageinfo(
        self,
        *,
        props: Iterable[WikiImageInfoProp] = (ImageInfoProp.TIMESTAMP, ImageInfoProp.USER),
        iilimit: int = 1,
        iiurlwidth: int = -1,
        iiurlheight: int = -1,
        iistart: str | None = None,
        iiend: str | None = None,
        iimetadataversion: str | None = None,
        iiextmetadatalanguage: str = "en",
        iiextmetadatamultilang: bool = False,
        iiextmetadatafilter: Iterable[str] | None = None,
        iiurlparam: str = "",
        iibadfilecontexttitle: str = "",
        iilocalonly: bool = False,
    ) -> dict[str, dict[str, Any]]:
        """Batch-fetch image information for all images in this dictionary.

        Sends multi-title API requests (up to 50 titles per request)
        and distributes results to each image's cache.

        Args:
            props: Image information properties to get as iterable of :class:`WikiImageInfoProp`.
            iilimit: How many file revisions to return per file (1–500).
            iiurlwidth: If iiprop=url is set, a URL to an image scaled to this width will be returned.
            iiurlheight: Similar to iiurlwidth.
            iistart: Timestamp to start listing from.
            iiend: Timestamp to stop listing at.
            iimetadataversion: Version of metadata to use (1 or latest).
            iiextmetadatalanguage: Language to fetch extmetadata in.
            iiextmetadatamultilang: Fetch all translations if available.
            iiextmetadatafilter: Specific keys to return for iiprop=extmetadata.
            iiurlparam: Handler specific parameter string.
            iibadfilecontexttitle: Page title used when evaluating bad image list.
            iilocalonly: Look only for files in the local repository.

        Returns:
            ``{title: imageinfo_dict}`` for every image in the dictionary.
        """
        return self._wiki.batch_imageinfo(  # type: ignore[no-any-return]
            list(self.values()),
            props=props,
            iilimit=iilimit,
            iiurlwidth=iiurlwidth,
            iiurlheight=iiurlheight,
            iistart=iistart,
            iiend=iiend,
            iimetadataversion=iimetadataversion,
            iiextmetadatalanguage=iiextmetadatalanguage,
            iiextmetadatamultilang=iiextmetadatamultilang,
            iiextmetadatafilter=iiextmetadatafilter,
            iiurlparam=iiurlparam,
            iibadfilecontexttitle=iibadfilecontexttitle,
            iilocalonly=iilocalonly,
        )


class AsyncImagesDict(dict[str, AsyncWikipediaImage]):
    """Asynchronous dictionary of AsyncWikipediaImage objects with batch operations.

    Subclass of ``dict`` that carries a back-reference to the async wiki client
    and exposes async batch-fetching methods for image information operations.

    Backward compatible: ``AsyncImagesDict`` subclasses ``dict``, so all existing
    code that treats it as a plain dict continues to work.
    """

    def __init__(self, wiki: Any, *args: Any, **kwargs: Any) -> None:
        """Initialize AsyncImagesDict with wiki reference.

        Args:
            wiki: The AsyncWikipedia client instance.
            *args: Positional arguments passed to dict.__init__.
            **kwargs: Keyword arguments passed to dict.__init__.
        """
        super().__init__(*args, **kwargs)
        self._wiki: Any = wiki

    async def imageinfo(
        self,
        *,
        props: Iterable[WikiImageInfoProp] = (ImageInfoProp.TIMESTAMP, ImageInfoProp.USER),
        iilimit: int = 1,
        iiurlwidth: int = -1,
        iiurlheight: int = -1,
        iistart: str | None = None,
        iiend: str | None = None,
        iimetadataversion: str | None = None,
        iiextmetadatalanguage: str = "en",
        iiextmetadatamultilang: bool = False,
        iiextmetadatafilter: Iterable[str] | None = None,
        iiurlparam: str = "",
        iibadfilecontexttitle: str = "",
        iilocalonly: bool = False,
    ) -> dict[str, dict[str, Any]]:
        """Asynchronously batch-fetch image information for all images in this dictionary.

        Sends multi-title API requests (up to 50 titles per request)
        and distributes results to each image's cache.

        Args:
            props: Image information properties to get as iterable of :class:`WikiImageInfoProp`.
            iilimit: How many file revisions to return per file (1–500).
            iiurlwidth: If iiprop=url is set, a URL to an image scaled to this width will be returned.
            iiurlheight: Similar to iiurlwidth.
            iistart: Timestamp to start listing from.
            iiend: Timestamp to stop listing at.
            iimetadataversion: Version of metadata to use (1 or latest).
            iiextmetadatalanguage: Language to fetch extmetadata in.
            iiextmetadatamultilang: Fetch all translations if available.
            iiextmetadatafilter: Specific keys to return for iiprop=extmetadata.
            iiurlparam: Handler specific parameter string.
            iibadfilecontexttitle: Page title used when evaluating bad image list.
            iilocalonly: Look only for files in the local repository.

        Returns:
            ``{title: imageinfo_dict}`` for every image in the dictionary.
        """
        return await self._wiki.batch_imageinfo(  # type: ignore[no-any-return]
            list(self.values()),
            props=props,
            iilimit=iilimit,
            iiurlwidth=iiurlwidth,
            iiurlheight=iiurlheight,
            iistart=iistart,
            iiend=iiend,
            iimetadataversion=iimetadataversion,
            iiextmetadatalanguage=iiextmetadatalanguage,
            iiextmetadatamultilang=iiextmetadatamultilang,
            iiextmetadatafilter=iiextmetadatafilter,
            iiurlparam=iiurlparam,
            iibadfilecontexttitle=iibadfilecontexttitle,
            iilocalonly=iilocalonly,
        )
