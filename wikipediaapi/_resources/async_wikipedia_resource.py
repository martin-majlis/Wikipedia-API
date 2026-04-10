from collections.abc import Iterable
from typing import TYPE_CHECKING
from typing import Any
from typing import Union
from typing import cast

from .._enums import CoordinatesProp
from .._enums import CoordinateType
from .._enums import Direction
from .._enums import GeoSearchSort
from .._enums import Globe
from .._enums import Namespace
from .._enums import RedirectFilter
from .._enums import SearchSort
from .._enums import WikiCoordinatesProp
from .._enums import WikiCoordinateType
from .._enums import WikiDirection
from .._enums import WikiGeoSearchSort
from .._enums import WikiGlobe
from .._enums import WikiNamespace
from .._enums import WikiRedirectFilter
from .._enums import WikiSearchInfo
from .._enums import WikiSearchProp
from .._enums import WikiSearchQiProfile
from .._enums import WikiSearchSort
from .._enums import WikiSearchWhat
from .._image.async_wikipedia_image import AsyncWikipediaImage
from .._page._base_wikipedia_page import NOT_CACHED
from .._page.async_wikipedia_page import AsyncWikipediaPage
from .._pages_dict import AsyncImagesDict
from .._pages_dict import AsyncPagesDict
from .._params.coordinates_params import CoordinatesParams
from .._params.geo_search_params import GeoSearchParams
from .._params.imageinfo_params import _DEFAULT_PROP
from .._params.imageinfo_params import ImageInfoParams
from .._params.images_params import ImagesParams
from .._params.random_params import RandomParams
from .._params.search_params import SearchParams
from .._types import Coordinate
from .._types import GeoBox
from .._types import GeoPoint
from .._types import ImageInfo
from .._types import SearchResults
from .base_wikipedia_resource import BaseWikipediaResource

if TYPE_CHECKING:
    pass


class AsyncWikipediaResource(BaseWikipediaResource):
    """
    Asynchronous mixin providing the public Wikipedia API surface.

    Combines :class:`BaseWikipediaResource` (parsing & dispatch logic) with
    :class:`~wikipediaapi._http_client.AsyncHTTPClient` (non-blocking HTTP
    via ``httpx``) to form a concrete async client.  Intended to be used
    via multiple inheritance::

        class AsyncWikipedia(AsyncWikipediaResource, AsyncHTTPClient): ...

    All API methods are coroutines and must be awaited.  Pages are
    represented by :class:`~wikipediaapi.AsyncWikipediaPage` objects whose
    properties are also coroutines.
    """

    def _make_page(  # type: ignore[override]
        self,
        title: str,
        ns: WikiNamespace,
        language: str,
        variant: str | None = None,
        url: str | None = None,
    ) -> "AsyncWikipediaPage":
        """
        Override of BaseWikipediaResource._make_page that returns AsyncWikipediaPage.

        All ``_build_*`` methods call ``_make_page`` to create stub pages,
        so stub pages produced in an async context are automatically async.

        :param title: page title exactly as it appears in Wikipedia URLs
        :param ns: namespace constant
        :param language: two-letter language code
        :param variant: optional language variant; ``None`` for none
        :param url: optional canonical URL (used for lang-link stubs)
        :return: uninitialised :class:`AsyncWikipediaPage` instance
        """
        return AsyncWikipediaPage(
            wiki=self,  # type: ignore[arg-type]
            title=title,
            ns=ns,
            language=language,
            variant=variant,
            url=url,
        )

    def _make_image(  # type: ignore[override]
        self,
        title: str,
        ns: WikiNamespace,
        language: str,
        variant: str | None = None,
    ) -> "AsyncWikipediaImage":
        """Override of BaseWikipediaResource._make_image that returns AsyncWikipediaImage.

        All ``_build_images_for_page`` calls delegate here, so image stubs
        produced in an async context are automatically async.

        :param title: file title including the ``File:`` prefix
        :param ns: namespace constant (typically 6 for files)
        :param language: two-letter language code
        :param variant: optional language variant; ``None`` for none
        :return: uninitialised :class:`AsyncWikipediaImage` instance
        """
        return AsyncWikipediaImage(
            wiki=self,  # type: ignore[arg-type]
            title=title,
            ns=ns,
            language=language,
            variant=variant,
        )

    def page(
        self,
        title: str,
        ns: WikiNamespace = Namespace.MAIN,
        unquote: bool = False,
    ) -> "AsyncWikipediaPage":
        """
        Return an :class:`AsyncWikipediaPage` for the given title (lazy, no network call).

        Creates a stub async page bound to this Wikipedia instance.  No HTTP request
        is made at construction time; each property coroutine fetches its data
        on first ``await``.

        :param title: page title as it appears in Wikipedia URLs
        :param ns: namespace; defaults to :attr:`Namespace.MAIN`
        :param unquote: if ``True``, percent-decode *title* before use
        :return: :class:`AsyncWikipediaPage` bound to this instance
        """
        from urllib import parse

        if unquote:
            title = parse.unquote(title)
        return AsyncWikipediaPage(
            self,  # type: ignore[arg-type]
            title=title,
            ns=ns,
            language=self.language,  # type: ignore[attr-defined]
            variant=self.variant,  # type: ignore[attr-defined]
        )

    def article(
        self, title: str, ns: WikiNamespace = Namespace.MAIN, unquote: bool = False
    ) -> "AsyncWikipediaPage":
        """
        Alias for :meth:`page`.

        Provided for semantic clarity when the caller knows the target is a
        main-namespace article rather than, e.g., a category or file page.

        :param title: page title as used in Wikipedia URLs
        :param ns: namespace; defaults to :attr:`Namespace.MAIN`
        :param unquote: if ``True``, percent-decode *title* before use
        :return: :class:`AsyncWikipediaPage` bound to this instance
        """
        return self.page(title=title, ns=ns, unquote=unquote)

    async def extracts(self, page: "AsyncWikipediaPage", **kwargs: Any) -> str:
        """
        Async version of :meth:`WikipediaResource.extracts`.

        Fetches and returns the plain-text or HTML extract for a page.
        See :meth:`WikipediaResource.extracts` for full documentation.

        :param page: page whose extract to fetch
        :param kwargs: extra ``extracts`` API parameters forwarded verbatim
        :return: introductory summary string
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return await self._async_dispatch_prop(
            page, self._extracts_params(page, **kwargs), "", self._build_extracts
        )

    async def info(self, page: "AsyncWikipediaPage") -> "AsyncWikipediaPage":
        """
        Async version of :meth:`WikipediaResource.info`.

        Fetches general page metadata and populates the page object in-place.
        See :meth:`WikipediaResource.info` for full documentation.

        :param page: page to fetch metadata for
        :return: *page* populated with info fields; *page* unchanged if
            the page does not exist
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return await self._async_dispatch_prop(
            page, self._info_params(page), page, self._build_info
        )

    async def langlinks(self, page: "AsyncWikipediaPage", **kwargs: Any) -> "AsyncPagesDict":
        """
        Async version of :meth:`WikipediaResource.langlinks`.

        Fetches inter-language links keyed by language code.
        See :meth:`WikipediaResource.langlinks` for full documentation.

        :param page: source page
        :param kwargs: extra API parameters (e.g. ``lllang="de"``)
        :return: ``{language_code: AsyncWikipediaPage}``; ``{}`` if missing
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return cast(
            "AsyncPagesDict",
            await self._async_dispatch_prop(
                page,
                self._langlinks_params(page, **kwargs),
                {},  # type: ignore[arg-type]
                self._build_langlinks,  # type: ignore[arg-type]
            ),
        )

    async def links(self, page: "AsyncWikipediaPage", **kwargs: Any) -> "AsyncPagesDict":
        """
        Async version of :meth:`WikipediaResource.links`.

        Fetches all outgoing wiki-links with automatic pagination.
        See :meth:`WikipediaResource.links` for full documentation.

        :param page: source page
        :param kwargs: extra API parameters (e.g. ``plnamespace=0``)
        :return: ``{title: AsyncWikipediaPage}``; ``{}`` if the page is missing
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return cast(
            "AsyncPagesDict",
            await self._async_dispatch_prop_paginated(
                page,
                {**self._links_params(page), **kwargs},
                "plcontinue",
                "links",
                self._build_links,
            ),
        )

    async def backlinks(self, page: "AsyncWikipediaPage", **kwargs: Any) -> "AsyncPagesDict":
        """
        Async version of :meth:`WikipediaResource.backlinks`.

        Fetches all pages linking *to* the page with automatic pagination.
        See :meth:`WikipediaResource.backlinks` for full documentation.

        :param page: target page (backlinks point *to* this page)
        :param kwargs: extra API parameters (e.g. ``blnamespace=0``)
        :return: ``{title: AsyncWikipediaPage}`` for all linking pages
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return cast(
            "AsyncPagesDict",
            await self._async_dispatch_list(
                page,
                {**self._backlinks_params(page), **kwargs},
                "blcontinue",
                "backlinks",
                self._build_backlinks,
            ),
        )

    async def categories(self, page: "AsyncWikipediaPage", **kwargs: Any) -> "AsyncPagesDict":
        """
        Async version of :meth:`WikipediaResource.categories`.

        Fetches all categories this page belongs to, keyed by title.
        See :meth:`WikipediaResource.categories` for full documentation.

        :param page: source page
        :param kwargs: extra API parameters (e.g. ``clshow="!hidden"``)
        :return: ``{title: AsyncWikipediaPage}``; ``{}`` if the page is missing
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return cast(
            "AsyncPagesDict",
            await self._async_dispatch_prop(
                page,
                self._categories_params(page, **kwargs),
                {},  # type: ignore[arg-type]
                self._build_categories,  # type: ignore[arg-type]
            ),
        )

    async def categorymembers(self, page: "AsyncWikipediaPage", **kwargs: Any) -> "AsyncPagesDict":
        """
        Async version of :meth:`WikipediaResource.categorymembers`.

        Fetches all members of a category page with automatic pagination.
        See :meth:`WikipediaResource.categorymembers` for full documentation.

        :param page: category page (must be in the ``Category:`` namespace)
        :param kwargs: extra API parameters (e.g. ``cmtype="subcat"``)
        :return: ``{title: AsyncWikipediaPage}`` for all members
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return cast(
            "AsyncPagesDict",
            await self._async_dispatch_list(
                page,
                {**self._categorymembers_params(page), **kwargs},
                "cmcontinue",
                "categorymembers",
                self._build_categorymembers,
            ),
        )

    async def coordinates(
        self,
        page: "AsyncWikipediaPage",
        *,
        limit: int = 10,
        primary: WikiCoordinateType = CoordinateType.PRIMARY,
        prop: Iterable[WikiCoordinatesProp] = (CoordinatesProp.GLOBE,),
        distance_from_point: GeoPoint | None = None,
        distance_from_page: Union["AsyncWikipediaPage", None] = None,
    ) -> list[Coordinate]:
        """Async version of :meth:`WikipediaResource.coordinates`.

        See :meth:`WikipediaResource.coordinates` for full documentation.

        :param page: Page to fetch coordinates for.
        :param limit: Maximum coordinates to return (1–500).
        :param primary: Which coordinates: ``"primary"``, ``"secondary"``, ``"all"``.
        :param prop: Additional properties as an iterable.
        :param distance_from_point: Reference point as :class:`GeoPoint`.
        :param distance_from_page: Reference page.

        Returns:
            List of :class:`Coordinate` objects; empty list if the page is missing.

        Raises:
            WikiHttpTimeoutError: If the request times out.
            WikiConnectionError: If a connection cannot be established.
            WikiRateLimitError: If the API returns HTTP 429.
            WikiHttpError: If the API returns a non-success HTTP status.
            WikiInvalidJsonError: If the response is not valid JSON.
        """
        params = CoordinatesParams(
            limit=limit,
            primary=primary,
            prop=prop,
            distance_from_point=distance_from_point,
            distance_from_page=distance_from_page,
        )
        cached = page._get_cached("coordinates", params.cache_key())
        if not isinstance(cached, type(NOT_CACHED)):
            return cached  # type: ignore[no-any-return]
        api_params = self._coordinates_api_params(page, params)
        raw = await self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, api_params)
        )
        self._common_attributes(raw.get("query", {}), page)
        for k, v in raw.get("query", {}).get("pages", {}).items():
            if k == "-1":
                page._attributes["pageid"] = self._missing_pageid(page)
                page._set_cached("coordinates", params.cache_key(), [])
                return []
            return self._build_coordinates_for_page(v, page, params)
        page._set_cached("coordinates", params.cache_key(), [])
        return []

    async def batch_coordinates(
        self,
        pages: list["AsyncWikipediaPage"],
        *,
        limit: int = 10,
        primary: WikiCoordinateType = CoordinateType.PRIMARY,
        prop: Iterable[WikiCoordinatesProp] = (CoordinatesProp.GLOBE,),
        distance_from_point: GeoPoint | None = None,
        distance_from_page: Union["AsyncWikipediaPage", None] = None,
    ) -> dict["AsyncWikipediaPage", list[Coordinate]]:
        """Async version of :meth:`WikipediaResource.batch_coordinates`.

        See :meth:`WikipediaResource.batch_coordinates` for full documentation.

        :param pages: List of pages to fetch coordinates for.
        :param limit: Maximum coordinates per page (1–500).
        :param primary: Which coordinates: ``"primary"``, ``"secondary"``, ``"all"``.
        :param prop: Additional properties as an iterable.
        :param distance_from_point: Reference point as :class:`GeoPoint`.
        :param distance_from_page: Reference page.

        Returns:
            ``{page: [Coordinate, ...]}`` for every page.
        """
        params = CoordinatesParams(
            limit=limit,
            primary=primary,
            prop=prop,
            distance_from_point=distance_from_point,
            distance_from_page=distance_from_page,
        )
        result: dict["AsyncWikipediaPage", list[Coordinate]] = {}
        page_map = {p.title: p for p in pages}
        for i in range(0, len(pages), 50):
            chunk = pages[i : i + 50]
            titles = "|".join(p.title for p in chunk)
            api_params: dict[str, Any] = {
                "action": "query",
                "prop": "coordinates",
                "titles": titles,
            }
            api_params.update(params.to_api())
            dummy_page = chunk[0]
            raw = await self._get(  # type: ignore[attr-defined]
                dummy_page.language, self._construct_params(dummy_page, api_params)
            )
            norm_map = self._build_normalization_map(raw)
            for _k, v in raw.get("query", {}).get("pages", {}).items():
                title = v.get("title", "")
                orig = norm_map.get(title, title)
                p = page_map.get(orig) or page_map.get(title)
                if p is not None:
                    if p.title != title:
                        p._attributes["title"] = title
                    coords = self._build_coordinates_for_page(v, p, params)
                    result[p] = coords
        for p in pages:
            if p not in result:
                result[p] = []
        return result

    async def images(
        self,
        page: "AsyncWikipediaPage",
        *,
        limit: int = 10,
        images: Iterable[str] | None = None,
        direction: WikiDirection = Direction.ASCENDING,
    ) -> "AsyncImagesDict":
        """Async version of :meth:`WikipediaResource.images`.

        See :meth:`WikipediaResource.images` for full documentation.

        :param page: Page to fetch images for.
        :param limit: Maximum images to return (1–500).
        :param images: Specific images as an iterable.
        :param direction: Sort direction as :class:`WikiDirection`.

        Returns:
            :class:`AsyncImagesDict` keyed by image title; empty if the page is missing.

        Raises:
            WikiHttpTimeoutError: If the request times out.
            WikiConnectionError: If a connection cannot be established.
            WikiRateLimitError: If the API returns HTTP 429.
            WikiHttpError: If the API returns a non-success HTTP status.
            WikiInvalidJsonError: If the response is not valid JSON.
        """
        params = ImagesParams(limit=limit, images=images, direction=direction)
        cached = page._get_cached("images", params.cache_key())
        if not isinstance(cached, type(NOT_CACHED)):
            return cached  # type: ignore[no-any-return]
        api_params = self._images_api_params(page, params)
        raw = await self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, api_params)
        )
        self._common_attributes(raw.get("query", {}), page)
        for k, v in raw.get("query", {}).get("pages", {}).items():
            if k == "-1":
                page._attributes["pageid"] = self._missing_pageid(page)
                empty_pd = AsyncImagesDict(wiki=self)
                page._set_cached("images", params.cache_key(), empty_pd)
                return empty_pd
            while "continue" in raw:
                api_params["imcontinue"] = raw["continue"]["imcontinue"]
                raw = await self._get(  # type: ignore[attr-defined]
                    page.language, self._construct_params(page, api_params)
                )
                v["images"] = v.get("images", []) + (
                    raw.get("query", {}).get("pages", {}).get(k, {}).get("images", [])
                )
            result = self._build_images_for_page(v, page, params)
            async_pd = AsyncImagesDict(wiki=self, data=dict(result))
            page._set_cached("images", params.cache_key(), async_pd)
            return async_pd
        empty_pd = AsyncImagesDict(wiki=self)
        page._set_cached("images", params.cache_key(), empty_pd)
        return empty_pd

    async def batch_images(
        self,
        pages: list["AsyncWikipediaPage"],
        *,
        limit: int = 10,
        images: Iterable[str] | None = None,
        direction: WikiDirection = Direction.ASCENDING,
    ) -> dict[str, "AsyncImagesDict"]:
        """Async version of :meth:`WikipediaResource.batch_images`.

        See :meth:`WikipediaResource.batch_images` for full documentation.

        :param pages: List of pages to fetch images for.
        :param limit: Maximum images per page (1–500).
        :param images: Specific images as an iterable.
        :param direction: Sort direction as :class:`WikiDirection`.

        Returns:
            ``{title: AsyncImagesDict}`` for every page.
        """
        params = ImagesParams(limit=limit, images=images, direction=direction)
        result: dict[str, "AsyncImagesDict"] = {}
        page_map = {p.title: p for p in pages}
        for i in range(0, len(pages), 50):
            chunk = pages[i : i + 50]
            titles = "|".join(p.title for p in chunk)
            api_params: dict[str, Any] = {
                "action": "query",
                "prop": "images",
                "titles": titles,
            }
            api_params.update(params.to_api())
            dummy_page = chunk[0]
            raw = await self._get(  # type: ignore[attr-defined]
                dummy_page.language, self._construct_params(dummy_page, api_params)
            )
            norm_map = self._build_normalization_map(raw)
            for _k, v in raw.get("query", {}).get("pages", {}).items():
                title = v.get("title", "")
                orig = norm_map.get(title, title)
                p = page_map.get(orig) or page_map.get(title)
                if p is not None:
                    imgs = self._build_images_for_page(v, p, params)
                    result[title] = AsyncImagesDict(wiki=self, data=dict(imgs))
        for p in pages:
            if p.title not in result:
                result[p.title] = AsyncImagesDict(wiki=self)
        return result

    async def imageinfo(
        self,
        image: "AsyncWikipediaImage",
        *,
        prop: tuple[str, ...] = _DEFAULT_PROP,
        limit: int = 1,
    ) -> list[ImageInfo]:
        """Async version of :meth:`WikipediaResource.imageinfo`.

        See :meth:`WikipediaResource.imageinfo` for full documentation.

        :param image: File page to fetch metadata for.
        :param prop: Tuple of ``iiprop`` field names.
        :param limit: Maximum number of file revisions to return (1–500).

        Returns:
            List of :class:`ImageInfo` objects; empty list if the file
            does not exist.

        Raises:
            WikiHttpTimeoutError: If the request times out.
            WikiConnectionError: If a connection cannot be established.
            WikiRateLimitError: If the API returns HTTP 429.
            WikiHttpError: If the API returns a non-success HTTP status.
            WikiInvalidJsonError: If the response is not valid JSON.
        """
        params = ImageInfoParams(prop=prop, limit=limit)
        cached = image._get_cached("imageinfo", params.cache_key())
        if not isinstance(cached, type(NOT_CACHED)):
            return cached  # type: ignore[no-any-return]
        api_params = self._imageinfo_api_params(image, params)
        raw = await self._get(  # type: ignore[attr-defined]
            image.language, self._construct_params(image, api_params)
        )
        for k, v in raw.get("query", {}).get("pages", {}).items():
            if k == "-1" and "known" not in v:
                image._attributes["pageid"] = self._missing_pageid(image)
                image._set_cached("imageinfo", params.cache_key(), [])
                return []
            return self._build_imageinfo_for_image(v, image, params)
        image._set_cached("imageinfo", params.cache_key(), [])
        return []

    async def batch_imageinfo(
        self,
        images: list["AsyncWikipediaImage"],
        *,
        prop: tuple[str, ...] = _DEFAULT_PROP,
        limit: int = 1,
    ) -> dict[str, list[ImageInfo]]:
        """Async version of :meth:`WikipediaResource.batch_imageinfo`.

        See :meth:`WikipediaResource.batch_imageinfo` for full documentation.

        :param images: List of file pages to fetch metadata for.
        :param prop: Tuple of ``iiprop`` field names.
        :param limit: Maximum number of file revisions to return (1–500).

        Returns:
            ``{title: [ImageInfo, ...]}`` for every image.
        """
        params = ImageInfoParams(prop=prop, limit=limit)
        result: dict[str, list[ImageInfo]] = {}
        image_map = {img.title: img for img in images}
        for i in range(0, len(images), 50):
            chunk = images[i : i + 50]
            titles = "|".join(img.title for img in chunk)
            api_params: dict[str, Any] = {
                "action": "query",
                "prop": "imageinfo",
                "titles": titles,
            }
            api_params.update(params.to_api())
            dummy_image = chunk[0]
            raw = await self._get(  # type: ignore[attr-defined]
                dummy_image.language, self._construct_params(dummy_image, api_params)
            )
            norm_map = self._build_normalization_map(raw)
            for k, v in raw.get("query", {}).get("pages", {}).items():
                title = v.get("title", "")
                orig = norm_map.get(title, title)
                img = image_map.get(orig) or image_map.get(title)
                if img is not None:
                    if k == "-1" and "known" not in v:
                        img._attributes["pageid"] = self._missing_pageid(img)
                        img._set_cached("imageinfo", params.cache_key(), [])
                        result[title] = []
                    else:
                        infos = self._build_imageinfo_for_image(v, img, params)
                        result[title] = infos
        for img in images:
            if img.title not in result:
                cached = img._get_cached("imageinfo", params.cache_key())
                result[img.title] = [] if isinstance(cached, type(NOT_CACHED)) else cached
        return result

    async def geosearch(
        self,
        *,
        coord: GeoPoint | None = None,
        page: Union["AsyncWikipediaPage", None] = None,
        bbox: GeoBox | None = None,
        radius: int = 500,
        max_dim: int | None = None,
        sort: WikiGeoSearchSort = GeoSearchSort.DISTANCE,
        limit: int = 10,
        globe: WikiGlobe = Globe.EARTH,
        ns: WikiNamespace = Namespace.MAIN,
        prop: Iterable[WikiCoordinatesProp] | None = None,
        primary: WikiCoordinateType | None = None,
    ) -> "AsyncPagesDict":
        """Async version of :meth:`WikipediaResource.geosearch`.

        See :meth:`WikipediaResource.geosearch` for full documentation.

        :param coord: Centre point as :class:`GeoPoint`.
        :param page: Title of page whose coordinates to use as centre.
        :param bbox: Bounding box as :class:`GeoBox`.
        :param radius: Search radius in meters (10–10000).
        :param max_dim: Exclude objects larger than this many meters.
        :param sort: Sort order: ``"distance"`` or ``"relevance"``.
        :param limit: Maximum pages to return (1–500).
        :param globe: Celestial body.
        :param ns: Restrict to this namespace number.
        :param prop: Additional properties as an iterable.
        :param primary: Which coordinates to consider.

        Returns:
            :class:`AsyncPagesDict` keyed by page title.
        """
        params = GeoSearchParams(
            coord=coord,
            page=page,
            bbox=bbox,
            radius=radius,
            max_dim=max_dim,
            sort=sort,
            limit=limit,
            globe=globe,
            namespace=ns,
            prop=prop,
            primary=primary,
        )
        api_params = self._geosearch_api_params(params)
        # Single request: the caller's limit already controls how many
        # results to return.  Paginating would keep fetching until every
        # nearby page is exhausted.
        raw = await self._get(  # type: ignore[attr-defined]
            self.language,  # type: ignore[attr-defined]
            self._construct_params_standalone(api_params),
        )
        result = self._build_geosearch_results(raw.get("query", {}))
        # Convert PagesDict to AsyncPagesDict
        return AsyncPagesDict(wiki=self, data=dict(result))

    async def random(
        self,
        *,
        ns: WikiNamespace = Namespace.MAIN,
        filter_redirect: WikiRedirectFilter = RedirectFilter.NONREDIRECTS,
        min_size: int | None = None,
        max_size: int | None = None,
        limit: int = 1,
    ) -> "AsyncPagesDict":
        """Async version of :meth:`WikipediaResource.random`.

        See :meth:`WikipediaResource.random` for full documentation.

        :param ns: Restrict to this namespace number.
        :param filter_redirect: Redirect filter.
        :param min_size: Minimum page size in bytes.
        :param max_size: Maximum page size in bytes.
        :param limit: Number of random pages to return (1–500).

        Returns:
            :class:`AsyncPagesDict` keyed by page title.
        """
        params = RandomParams(
            namespace=ns,
            filter_redirect=filter_redirect,
            min_size=min_size,
            max_size=max_size,
            limit=limit,
        )
        api_params = self._random_api_params(params)
        # Random never paginates: the API always returns a continue
        # token (there are always more random pages), so using
        # _async_dispatch_standalone_list would loop forever.
        raw = await self._get(  # type: ignore[attr-defined]
            self.language,  # type: ignore[attr-defined]
            self._construct_params_standalone(api_params),
        )
        result = self._build_random_results(raw.get("query", {}))
        # Convert PagesDict to AsyncPagesDict
        return AsyncPagesDict(wiki=self, data=dict(result))

    async def search(
        self,
        query: str,
        *,
        ns: WikiNamespace = Namespace.MAIN,
        limit: int = 10,
        prop: Iterable[WikiSearchProp] | None = None,
        info: Iterable[WikiSearchInfo] | None = None,
        sort: WikiSearchSort = SearchSort.RELEVANCE,
        what: WikiSearchWhat | None = None,
        interwiki: bool = False,
        enable_rewrites: bool = False,
        qi_profile: WikiSearchQiProfile | None = None,
    ) -> SearchResults:
        """Async version of :meth:`WikipediaResource.search`.

        See :meth:`WikipediaResource.search` for full documentation.

        :param query: Search string (required).
        :param ns: Namespace to search in.
        :param limit: Maximum results to return (1–500).
        :param prop: Properties as an iterable (deprecated upstream).
        :param info: Metadata as an iterable.
        :param sort: Sort order.
        :param what: Search type.
        :param interwiki: Include interwiki results.
        :param enable_rewrites: Allow the backend to rewrite the query.
        :param qi_profile: Query-independent ranking profile.

        Returns:
            :class:`SearchResults` with pages, totalhits, and suggestion.
        """
        params = SearchParams(
            query=query,
            namespace=ns,
            limit=limit,
            prop=prop,
            info=info,
            sort=sort,
            what=what,
            interwiki=interwiki,
            enable_rewrites=enable_rewrites,
            qi_profile=qi_profile,
        )
        api_params = self._search_api_params(params)
        # Single request: the caller's limit already controls how many
        # results to return.  Paginating would keep fetching until every
        # matching page is exhausted (thousands of API calls).
        raw = await self._get(  # type: ignore[attr-defined]
            self.language,  # type: ignore[attr-defined]
            self._construct_params_standalone(api_params),
        )
        return self._build_search_results(raw)

    async def pages(
        self,
        titles: list[str],
        ns: WikiNamespace = Namespace.MAIN,
    ) -> "AsyncPagesDict":
        """Create an :class:`AsyncPagesDict` of lazy page stubs.

        No network call is made; each page fetches data on demand.

        :param titles: List of page titles.
        :param ns: Namespace for all pages; defaults to :attr:`Namespace.MAIN`.

        Returns:
            :class:`AsyncPagesDict` keyed by title.
        """
        data = {t: self.page(t, ns=ns) for t in titles}
        return AsyncPagesDict(wiki=self, data=data)
