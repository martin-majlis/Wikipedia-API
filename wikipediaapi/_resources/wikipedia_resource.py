from collections.abc import Iterable
from typing import TYPE_CHECKING
from typing import Any
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
from .._page.wikipedia_page import WikipediaPage
from .._pages_dict import ImagesDict
from .._pages_dict import PagesDict
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
    from .._image.wikipedia_image import WikipediaImage


class WikipediaResource(BaseWikipediaResource):
    """
    Synchronous mixin providing the public Wikipedia API surface.

    Combines :class:`BaseWikipediaResource` (parsing & dispatch logic) with
    :class:`~wikipediaapi._http_client.SyncHTTPClient` (blocking HTTP via
    ``httpx``) to form a concrete synchronous client.  Intended to be used
    via multiple inheritance::

        class Wikipedia(WikipediaResource, SyncHTTPClient): ...

    All API methods block until HTTP response is received and parsed.
    """

    def page(
        self,
        title: str,
        ns: WikiNamespace = Namespace.MAIN,
        unquote: bool = False,
    ) -> WikipediaPage:
        """
        Return a :class:`WikipediaPage` for the given title (lazy, no network call).

        Creates a stub page bound to this Wikipedia instance.  No HTTP request
        is made at construction time; individual properties (``text``,
        ``summary``, ``links``, ...) fetch their data on first access.

        :param title: page title as it appears in Wikipedia URLs; spaces may
            be replaced by underscores
            (e.g. ``"Python_(programming_language)"``)
        :param ns: namespace; defaults to :attr:`Namespace.MAIN`
        :param unquote: if ``True``, percent-decode *title* before use
        :return: :class:`WikipediaPage` bound to this instance
        """
        from urllib import parse

        if unquote:
            title = parse.unquote(title)
        return WikipediaPage(
            self,  # type: ignore[arg-type]
            title=title,
            ns=ns,
            language=self.language,  # type: ignore[attr-defined]
            variant=self.variant,  # type: ignore[attr-defined]
        )

    def article(
        self, title: str, ns: WikiNamespace = Namespace.MAIN, unquote: bool = False
    ) -> WikipediaPage:
        """
        Alias for :meth:`page`.

        Provided for semantic clarity when the caller knows the target is a
        main-namespace article rather than, e.g., a category or file page.

        :param title: page title as used in Wikipedia URLs
        :param ns: namespace; defaults to :attr:`Namespace.MAIN`
        :param unquote: if ``True``, percent-decode *title* before use
        :return: :class:`WikipediaPage` bound to this instance
        """
        return self.page(title=title, ns=ns, unquote=unquote)

    def extracts(self, page: WikipediaPage, **kwargs: Any) -> str:
        """
        Fetch and return the plain-text or HTML extract for a page.

        Output format (plain-text wiki markup vs. HTML) is controlled by the
        ``extract_format`` argument passed to the
        :class:`~wikipediaapi.Wikipedia` constructor.  Pass additional
        ``extracts`` API parameters via *kwargs* to narrow the result
        (e.g. ``exsentences=2``, ``exintro=True``).

        API reference:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bextracts
        - https://www.mediawiki.org/wiki/Extension:TextExtracts#API

        Example::

            import wikipediaapi
            wiki = wikipediaapi.Wikipedia('MyBot/1.0', 'en')
            page = wiki.page('Python_(programming_language)')
            print(wiki.extracts(page, exsentences=1))

        :param page: page whose extract to fetch
        :param kwargs: extra ``extracts`` API parameters forwarded verbatim
        :return: introductory summary string
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return self._dispatch_prop(
            page, self._extracts_params(page, **kwargs), "", self._build_extracts
        )

    def info(self, page: WikipediaPage) -> WikipediaPage:
        """
        Fetch general page metadata and populate the page object in-place.

        Calls the ``info`` prop and copies all returned fields (protection
        level, talk page ID, watcher counts, canonical URL, display title,
        variant titles, ...) into ``page._attributes``.  Returns *page*
        itself so callers can chain calls.

        API reference:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Binfo
        - https://www.mediawiki.org/wiki/API:Info

        :param page: page to fetch metadata for
        :return: *page* populated with info fields; *page* unchanged if
            the page does not exist (``pageid`` is set to a negative value)
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return self._dispatch_prop(page, self._info_params(page), page, self._build_info)

    def langlinks(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Fetch inter-language links and return them keyed by language code.

        Each value is a stub :class:`WikipediaPage` with its ``language``
        attribute set and canonical URL pre-populated.  Up to 500
        language links are returned in a single request.

        API reference:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blanglinks
        - https://www.mediawiki.org/wiki/API:Langlinks

        :param page: source page
        :param kwargs: extra API parameters (e.g. ``lllang="de"`` to filter
            to a single target language)
        :return: ``{language_code: WikipediaPage}``; ``{}`` if the page is missing
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return cast(
            PagesDict,
            self._dispatch_prop(
                page,
                self._langlinks_params(page, **kwargs),
                {},
                self._build_langlinks,  # type: ignore[arg-type]
            ),
        )

    def links(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Fetch all outgoing wiki-links and return them keyed by title.

        Follows API pagination automatically (``plcontinue`` cursor) so the
        returned dict always contains the complete set of links regardless of
        how many round-trips were required.  Each value is a stub
        :class:`WikipediaPage` for lazy expansion.

        API reference:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blinks
        - https://www.mediawiki.org/wiki/API:Links

        :param page: source page
        :param kwargs: extra API parameters (e.g. ``plnamespace=0``)
        :return: ``{title: WikipediaPage}``; ``{}`` if the page is missing
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return cast(
            PagesDict,
            self._dispatch_prop_paginated(
                page,
                {**self._links_params(page), **kwargs},
                "plcontinue",
                "links",
                self._build_links,
            ),
        )

    def backlinks(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Fetch all pages that link *to* the page and return them keyed by title.

        Follows API pagination automatically (``blcontinue`` cursor) so the
        returned dict is always complete.  Each value is a stub
        :class:`WikipediaPage`.

        API reference:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bbacklinks
        - https://www.mediawiki.org/wiki/API:Backlinks

        :param page: target page (backlinks point *to* this page)
        :param kwargs: extra API parameters (e.g. ``blnamespace=0``,
            ``blfilterredir="nonredirects"``)
        :return: ``{title: WikipediaPage}`` for all pages linking here
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return cast(
            PagesDict,
            self._dispatch_list(
                page,
                {**self._backlinks_params(page), **kwargs},
                "blcontinue",
                "backlinks",
                self._build_backlinks,
            ),
        )

    def categories(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Fetch all categories this page belongs to, keyed by category title.

        Each value is a stub :class:`WikipediaPage` in the ``Category:``
        namespace.

        API reference:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategories
        - https://www.mediawiki.org/wiki/API:Categories

        :param page: source page
        :param kwargs: extra API parameters (e.g. ``clshow="!hidden"`` to
            exclude hidden categories)
        :return: ``{title: WikipediaPage}``; ``{}`` if the page is missing
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return cast(
            PagesDict,
            self._dispatch_prop(
                page,
                self._categories_params(page, **kwargs),
                {},
                self._build_categories,  # type: ignore[arg-type]
            ),
        )

    def categorymembers(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Fetch all members of a category page and return them keyed by title.

        Follows API pagination automatically (``cmcontinue`` cursor).
        *page* must be in the ``Category:`` namespace.  Each value is a stub
        :class:`WikipediaPage` with ``pageid`` pre-set.

        API reference:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategorymembers
        - https://www.mediawiki.org/wiki/API:Categorymembers

        :param page: category page (must have ``ns == Namespace.CATEGORY``)
        :param kwargs: extra API parameters (e.g. ``cmtype="subcat"`` to
            list only sub-categories)
        :return: ``{title: WikipediaPage}`` for all category members
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return cast(
            PagesDict,
            self._dispatch_list(
                page,
                {**self._categorymembers_params(page), **kwargs},
                "cmcontinue",
                "categorymembers",
                self._build_categorymembers,
            ),
        )

    def coordinates(
        self,
        page: WikipediaPage,
        *,
        limit: int = 10,
        primary: WikiCoordinateType = CoordinateType.PRIMARY,
        prop: Iterable[WikiCoordinatesProp] = (CoordinatesProp.GLOBE,),
        distance_from_point: GeoPoint | None = None,
        distance_from_page: WikipediaPage | None = None,
    ) -> list[Coordinate]:
        """Fetch geographic coordinates for a page.

        Calls ``prop=coordinates`` with the given parameters and caches
        result per parameter set.  ``page.coordinates`` (the property)
        calls this with defaults.

        API reference:

        - https://www.mediawiki.org/wiki/Extension:GeoData#prop.3Dcoordinates

        Args:
            page: Page to fetch coordinates for.
            limit: Maximum coordinates to return (1–500).
            primary: Which coordinates: ``"primary"``, ``"secondary"``, ``"all"``.
            prop: Additional properties as an iterable.
            distance_from_point: Reference point as :class:`GeoPoint`.
            distance_from_page: Reference page.

        Returns:
            List of :class:`Coordinate` objects; empty list if the page is missing.

        Raises:
            WikiHttpTimeoutError: If the request times out.
            WikiConnectionError: If a connection cannot be established.
            WikiRateLimitError: If the API returns HTTP 429.
            WikiHttpError: If the API returns a non-success HTTP status.
            WikiInvalidJsonError: If the response is not valid JSON.
        """
        from .._page._base_wikipedia_page import NOT_CACHED

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
        raw = self._get(  # type: ignore[attr-defined]
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

    def batch_coordinates(
        self,
        pages: list[WikipediaPage],
        *,
        limit: int = 10,
        primary: WikiCoordinateType = CoordinateType.PRIMARY,
        prop: Iterable[WikiCoordinatesProp] = (CoordinatesProp.GLOBE,),
        distance_from_point: GeoPoint | None = None,
        distance_from_page: WikipediaPage | None = None,
    ) -> dict[WikipediaPage, list[Coordinate]]:
        """Batch-fetch coordinates for multiple pages.

        Sends multi-title API requests (up to 50 titles per request)
        and distributes results to each page's cache.

        Args:
            pages: List of pages to fetch coordinates for.
            limit: Maximum coordinates per page (1–500).
            primary: Which coordinates: ``"primary"``, ``"secondary"``, ``"all"``.
            prop: Additional properties as an iterable.
            distance_from_point: Reference point as :class:`GeoPoint`.
            distance_from_page: Reference page.

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
        result: dict[WikipediaPage, list[Coordinate]] = {}
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
            raw = self._get(  # type: ignore[attr-defined]
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

    def images(
        self,
        page: WikipediaPage,
        *,
        limit: int = 10,
        images: Iterable[str] | None = None,
        direction: WikiDirection = Direction.ASCENDING,
    ) -> ImagesDict:
        """Fetch images (files) used on a page.

        Calls ``prop=images`` with automatic pagination and caches
        result per parameter set.

        API reference:

        - https://www.mediawiki.org/wiki/API:Images

        Args:
            page: Page to fetch images for.
            limit: Maximum images to return (1–500).
            images: Specific images as an iterable.
            direction: Sort direction as :class:`WikiDirection`.

        Returns:
            :class:`ImagesDict` keyed by image title; empty if the page is missing.

        Raises:
            WikiHttpTimeoutError: If the request times out.
            WikiConnectionError: If a connection cannot be established.
            WikiRateLimitError: If the API returns HTTP 429.
            WikiHttpError: If the API returns a non-success HTTP status.
            WikiInvalidJsonError: If the response is not valid JSON.
        """
        from .._page._base_wikipedia_page import NOT_CACHED

        params = ImagesParams(limit=limit, images=images, direction=direction)
        cached = page._get_cached("images", params.cache_key())
        if not isinstance(cached, type(NOT_CACHED)):
            return cached  # type: ignore[no-any-return]
        api_params = self._images_api_params(page, params)
        raw = self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, api_params)
        )
        self._common_attributes(raw.get("query", {}), page)
        for k, v in raw.get("query", {}).get("pages", {}).items():
            if k == "-1":
                page._attributes["pageid"] = self._missing_pageid(page)
                empty = ImagesDict(wiki=self)
                page._set_cached("images", params.cache_key(), empty)
                return empty
            while "continue" in raw:
                api_params["imcontinue"] = raw["continue"]["imcontinue"]
                raw = self._get(  # type: ignore[attr-defined]
                    page.language, self._construct_params(page, api_params)
                )
                v["images"] = v.get("images", []) + (
                    raw.get("query", {}).get("pages", {}).get(k, {}).get("images", [])
                )
            return self._build_images_for_page(v, page, params)  # type: ignore[return-value]
        empty = ImagesDict(wiki=self)
        page._set_cached("images", params.cache_key(), empty)
        return empty

    def batch_images(
        self,
        pages: list[WikipediaPage],
        *,
        limit: int = 10,
        images: Iterable[str] | None = None,
        direction: WikiDirection = Direction.ASCENDING,
    ) -> dict[str, ImagesDict]:
        """Batch-fetch images for multiple pages.

        Sends multi-title API requests (up to 50 titles per request)
        and distributes results to each page's cache.

        Args:
            pages: List of pages to fetch images for.
            limit: Maximum images per page (1–500).
            images: Specific images as an iterable.
            direction: Sort direction as :class:`WikiDirection`.

        Returns:
            ``{title: ImagesDict}`` for every page.
        """
        params = ImagesParams(limit=limit, images=images, direction=direction)
        result: dict[str, ImagesDict] = {}
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
            raw = self._get(  # type: ignore[attr-defined]
                dummy_page.language, self._construct_params(dummy_page, api_params)
            )
            norm_map = self._build_normalization_map(raw)
            for _k, v in raw.get("query", {}).get("pages", {}).items():
                title = v.get("title", "")
                orig = norm_map.get(title, title)
                p = page_map.get(orig) or page_map.get(title)
                if p is not None:
                    imgs = self._build_images_for_page(v, p, params)
                    result[title] = imgs
        for p in pages:
            if p.title not in result:
                result[p.title] = ImagesDict(wiki=self)
        return result

    def imageinfo(
        self,
        image: "WikipediaImage",
        *,
        prop: tuple[str, ...] = _DEFAULT_PROP,
        limit: int = 1,
    ) -> list[ImageInfo]:
        """Fetch metadata for a single file page.

        Calls ``prop=imageinfo`` and caches the result per parameter set.

        API reference:

        - https://www.mediawiki.org/wiki/API:Imageinfo

        Args:
            image: File page to fetch metadata for.
            prop: Tuple of ``iiprop`` field names.
            limit: Maximum number of file revisions to return (1–500).

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
        from .._page._base_wikipedia_page import NOT_CACHED

        params = ImageInfoParams(prop=prop, limit=limit)
        cached = image._get_cached("imageinfo", params.cache_key())
        if not isinstance(cached, type(NOT_CACHED)):
            return cached  # type: ignore[no-any-return]
        api_params = self._imageinfo_api_params(image, params)
        raw = self._get(  # type: ignore[attr-defined]
            image.language, self._construct_params(image, api_params)
        )
        for k, v in raw.get("query", {}).get("pages", {}).items():
            if k == "-1" and "known" not in v:
                # Truly missing file — no imageinfo key, no known key
                image._attributes["pageid"] = self._missing_pageid(image)
                image._set_cached("imageinfo", params.cache_key(), [])
                return []
            return self._build_imageinfo_for_image(v, image, params)
        image._set_cached("imageinfo", params.cache_key(), [])
        return []

    def batch_imageinfo(
        self,
        images: "list[WikipediaImage]",
        *,
        prop: tuple[str, ...] = _DEFAULT_PROP,
        limit: int = 1,
    ) -> dict[str, list[ImageInfo]]:
        """Batch-fetch imageinfo for multiple file pages.

        Sends multi-title API requests (up to 50 titles per request)
        and distributes results to each image's cache.

        Args:
            images: List of file pages to fetch metadata for.
            prop: Tuple of ``iiprop`` field names.
            limit: Maximum number of file revisions to return (1–500).

        Returns:
            ``{title: [ImageInfo, ...]}`` for every image.
        """
        from .._page._base_wikipedia_page import NOT_CACHED

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
            raw = self._get(  # type: ignore[attr-defined]
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

    def geosearch(
        self,
        *,
        coord: GeoPoint | None = None,
        page: WikipediaPage | None = None,
        bbox: GeoBox | None = None,
        radius: int = 500,
        max_dim: int | None = None,
        sort: WikiGeoSearchSort = GeoSearchSort.DISTANCE,
        limit: int = 10,
        globe: WikiGlobe = Globe.EARTH,
        ns: WikiNamespace = Namespace.MAIN,
        prop: Iterable[WikiCoordinatesProp] | None = None,
        primary: WikiCoordinateType | None = None,
    ) -> PagesDict:
        """Search for pages with coordinates near a location.

        Calls ``list=geosearch`` and returns :class:`WikipediaPage` stubs
        with pre-cached coordinates and :class:`GeoSearchMeta` sub-objects.

        At least one of ``coord``, ``page``, or ``bbox`` must be provided.

        API reference:

        - https://www.mediawiki.org/wiki/Extension:GeoData#list.3Dgeosearch

        Args:
            coord: Centre point as :class:`GeoPoint`.
            page: Title of page whose coordinates to use as centre.
            bbox: Bounding box as :class:`GeoBox`.
            radius: Search radius in meters (10–10000).
            max_dim: Exclude objects larger than this many meters.
            sort: Sort order: ``"distance"`` or ``"relevance"``.
            limit: Maximum pages to return (1–500).
            globe: Celestial body.
            ns: Restrict to this namespace number.
            prop: Additional properties as an iterable.
            primary: Which coordinates to consider.

        Returns:
            :class:`PagesDict` keyed by page title.
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
        raw = self._get(  # type: ignore[attr-defined]
            self.language,  # type: ignore[attr-defined]
            self._construct_params_standalone(api_params),
        )
        return self._build_geosearch_results(raw.get("query", {}))

    def random(
        self,
        *,
        ns: WikiNamespace = Namespace.MAIN,
        filter_redirect: WikiRedirectFilter = RedirectFilter.NONREDIRECTS,
        min_size: int | None = None,
        max_size: int | None = None,
        limit: int = 1,
    ) -> PagesDict:
        """Fetch a set of random pages.

        Calls ``list=random`` and returns :class:`WikipediaPage` stubs
        with ``pageid`` pre-set.

        API reference:

        - https://www.mediawiki.org/wiki/API:Random

        Args:
            ns: Restrict to this namespace number.
            filter_redirect: Redirect filter: ``"all"``, ``"nonredirects"``,
                or ``"redirects"``.
            min_size: Minimum page size in bytes.
            max_size: Maximum page size in bytes.
            limit: Number of random pages to return (1–500).

        Returns:
            :class:`PagesDict` keyed by page title.
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
        # _dispatch_standalone_list would loop forever.
        raw = self._get(  # type: ignore[attr-defined]
            self.language,  # type: ignore[attr-defined]
            self._construct_params_standalone(api_params),
        )
        return self._build_random_results(raw.get("query", {}))

    def search(
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
        """Perform a full-text search.

        Calls ``list=search`` and returns a :class:`SearchResults` wrapper
        containing :class:`WikipediaPage` stubs with :class:`SearchMeta`
        sub-objects, plus aggregate metadata.

        API reference:

        - https://www.mediawiki.org/wiki/API:Search

        Args:
            query: Search string (required).
            ns: Namespace to search in.
            limit: Maximum results to return (1–500).
            prop: Properties as an iterable (deprecated upstream).
            info: Metadata as an iterable.
            sort: Sort order.
            what: Search type: ``"title"``, ``"text"``, or ``"nearmatch"``.
            interwiki: Include interwiki results.
            enable_rewrites: Allow the backend to rewrite the query.
            qi_profile: Query-independent ranking profile.

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
        raw = self._get(  # type: ignore[attr-defined]
            self.language,  # type: ignore[attr-defined]
            self._construct_params_standalone(api_params),
        )
        return self._build_search_results(raw)

    def pages(
        self,
        titles: list[str],
        ns: WikiNamespace = Namespace.MAIN,
    ) -> PagesDict:
        """Create a :class:`PagesDict` of lazy page stubs.

        No network call is made; each page fetches data on demand.

        Args:
            titles: List of page titles.
            ns: Namespace for all pages; defaults to :attr:`Namespace.MAIN`.

        Returns:
            :class:`PagesDict` keyed by title.
        """
        data = {t: self.page(t, ns=ns) for t in titles}
        return PagesDict(wiki=self, data=data)
