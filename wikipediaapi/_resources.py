from abc import ABC
from collections import defaultdict
from collections.abc import Callable, Iterable
import re
from typing import Any, TYPE_CHECKING, TypeVar, Union
from urllib import parse

from ._base_wikipedia_image import BaseWikipediaImage
from ._base_wikipedia_page import BaseWikipediaPage
from ._base_wikipedia_page import NOT_CACHED
from ._enums import CoordinatesProp
from ._enums import CoordinateType
from ._enums import Direction
from ._enums import GeoSearchSort
from ._enums import Globe
from ._enums import ImageInfoProp
from ._enums import Namespace
from ._enums import RedirectFilter
from ._enums import SearchSort
from ._enums import WikiCoordinatesProp
from ._enums import WikiCoordinateType
from ._enums import WikiDirection
from ._enums import WikiGeoSearchSort
from ._enums import WikiGlobe
from ._enums import WikiImageInfoProp
from ._enums import WikiNamespace
from ._enums import WikiRedirectFilter
from ._enums import WikiSearchInfo
from ._enums import WikiSearchProp
from ._enums import WikiSearchQiProfile
from ._enums import WikiSearchSort
from ._enums import WikiSearchWhat
from ._pages_dict import AsyncImagesDict
from ._pages_dict import AsyncPagesDict
from ._pages_dict import ImagesDict
from ._pages_dict import PagesDict
from ._params import CoordinatesParams
from ._params import GeoSearchParams
from ._params import ImageInfoParams
from ._params import ImagesParams
from ._params import RandomParams
from ._params import SearchParams
from ._types import Coordinate
from ._types import GeoBox
from ._types import GeoPoint
from ._types import GeoSearchMeta
from ._types import SearchMeta
from ._types import SearchResults
from .extract_format import ExtractFormat
from .wikipedia_image import WikipediaImage
from .wikipedia_page import WikipediaPage
from .wikipedia_page_section import WikipediaPageSection

T = TypeVar("T")
_PageP = TypeVar("_PageP", bound=BaseWikipediaPage)


if TYPE_CHECKING:
    from .async_wikipedia_image import AsyncWikipediaImage
    from .async_wikipedia_page import AsyncWikipediaPage

RE_SECTION = {
    ExtractFormat.WIKI: re.compile(r"\n\n *(==+) (.*?) (==+) *\n"),
    ExtractFormat.HTML: re.compile(
        r"\n? *<h([1-9])[^>]*?>(<span[^>]*></span>)? *"
        + "(<span[^>]*>)? *(<span[^>]*></span>)? *(.*?) *"
        + "(</span>)?(<span>Edit</span>)?</h[1-9]>\n?"
        #                  ^^^^
        # Example page with 'Edit' erroneous links: https://bit.ly/2ui4FWs
    ),
    # ExtractFormat.PLAIN.value: re.compile(r'\n\n *(===*) (.*?) (===*) *\n'),
}


class BaseWikipediaResource(ABC):
    """
    Mixin providing shared Wikipedia API logic for both sync and async subclasses.

    This class contains all parameter builders, response parsers, and dispatch
    helpers. It has no HTTP transport of its own; subclasses must supply a
    ``_get(language, params)`` method (sync or async) and the instance
    attributes ``extract_format`` and ``_extra_api_params``.

    Subclassing convention:

    * Synchronous clients inherit :class:`WikipediaResource` and
      :class:`~wikipediaapi._http_client.SyncHTTPClient`.
    * Asynchronous clients inherit :class:`AsyncWikipediaResource` and
      :class:`~wikipediaapi._http_client.AsyncHTTPClient`.
    """

    def _construct_params(
        self,
        page: "BaseWikipediaPage[Any] | BaseWikipediaImage[Any]",
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Merge caller-supplied params with mandatory API defaults.

        Adds ``format=json``, ``redirects=1``, an optional ``variant`` (when
        set on *page*), and any instance-level ``_extra_api_params``.  Caller
        params take precedence over defaults; ``_extra_api_params`` take
        precedence over everything.

        :param page: source page or image, used to read ``page.variant``
        :param params: API-specific parameters produced by a ``_*_params`` method
        :return: fully merged parameter dict ready to pass to ``_get``
        """
        used_params: dict[str, Any] = {}
        if page.variant:
            used_params["variant"] = page.variant
        used_params["format"] = "json"
        used_params["redirects"] = 1
        used_params.update(params)
        if self._extra_api_params:  # type: ignore[attr-defined]
            used_params.update(self._extra_api_params)  # type: ignore[attr-defined]
        return used_params

    def _make_page(
        self,
        title: str,
        ns: WikiNamespace,
        language: str,
        variant: str | None = None,
        url: str | None = None,
    ) -> "BaseWikipediaPage[Any]":
        """
        Create a stub :class:`WikipediaPage` bound to this resource instance.

        The returned page is *not* yet populated with API data; it will fetch
        lazily when its properties are accessed.  Overridden in
        :class:`AsyncWikipediaResource` to return :class:`AsyncWikipediaPage`.

        :param title: page title exactly as it appears in Wikipedia URLs
        :param ns: namespace constant from :class:`~wikipediaapi.Namespace`
        :param language: two-letter language code (e.g. ``"en"``)
        :param variant: optional language variant (e.g. ``"zh-tw"``);
            ``None`` means no variant conversion
        :param url: optional canonical URL; used for lang-link pages
        :return: uninitialised :class:`WikipediaPage` instance
        """
        return WikipediaPage(
            wiki=self,  # type: ignore[arg-type]
            title=title,
            ns=ns,
            language=language,
            variant=variant,
            url=url,
        )

    def _make_image(
        self,
        title: str,
        ns: WikiNamespace,
        language: str,
        variant: str | None = None,
    ) -> WikipediaImage:
        """
        Create a stub :class:`WikipediaImage` bound to this resource instance.

        The returned image is *not* yet populated with API data; it will fetch
        lazily when its properties are accessed.  Overridden in
        :class:`AsyncWikipediaResource` to return :class:`AsyncWikipediaImage`.

        :param title: image title exactly as it appears in Wikipedia URLs
        :param ns: namespace constant from :class:`~wikipediaapi.Namespace`
        :param language: two-letter language code (e.g. ``"en"``)
        :param variant: optional language variant (e.g. ``"zh-tw"``);
            ``None`` means no variant conversion
        :return: uninitialised :class:`WikipediaImage` instance
        """
        return WikipediaImage(
            wiki=self,  # type: ignore[arg-type]
            title=title,
            ns=ns,
            language=language,
            variant=variant,
        )

    @staticmethod
    def _build_normalization_map(raw: dict[str, Any]) -> dict[str, str]:
        """Build a mapping from normalized titles back to original titles.

        MediaWiki normalizes titles (e.g. ``Test_1`` → ``Test 1``).
        This method reads the ``normalized`` block from a raw API response
        and returns ``{normalized_title: original_title}``.

        Args:
            raw: Full raw API response dict.

        Returns:
            Mapping from normalized title to original title.
        """
        norm_map: dict[str, str] = {}
        for entry in raw.get("query", {}).get("normalized", []):
            norm_map[entry["to"]] = entry["from"]
        return norm_map

    @staticmethod
    def _missing_pageid(page: "BaseWikipediaPage[Any]") -> int:
        """Build a deterministic negative page ID for a missing page.

        Args:
            page: Page object representing a missing page.

        Returns:
            A negative integer derived from page identity and stable within
            the current Python process.
        """
        pageid = hash((page.language, page.title, page.ns))
        if pageid >= 0:
            pageid = -(pageid + 1)
        if pageid == -1:
            return -2
        return pageid

    @staticmethod
    def _common_attributes(extract: Any, page: "BaseWikipediaPage[Any]") -> None:
        """
        Copy standard API response fields into ``page._attributes``.

        Reads ``title``, ``pageid``, ``ns``, and ``redirects`` from *extract*
        (if present) and stores them on the page.  Safe to call multiple times;
        later calls overwrite earlier values for the same keys.

        :param extract: dict from the API response (a ``query`` block or
            a single page entry within ``query["pages"]``)
        :param page: page whose ``_attributes`` dict is updated in-place
        """
        common_attributes = ["title", "pageid", "ns", "redirects"]
        for attr in common_attributes:
            if attr in extract:
                page._attributes[attr] = extract[attr]

    def _create_section(self, match: Any) -> WikipediaPageSection:
        """
        Build a :class:`WikipediaPageSection` from a regex section-header match.

        Interprets *match* differently depending on ``self.extract_format``:

        * :attr:`ExtractFormat.WIKI` — group 2 is the title, group 1 gives
          the heading depth via ``len()``.
        * :attr:`ExtractFormat.HTML` — group 5 is the title, group 1 is the
          ``<hN>`` level as a digit string.

        :param match: regex match object from :data:`RE_SECTION`
        :return: new :class:`WikipediaPageSection` with title and level set
        :invariant: ``self.extract_format`` must be ``WIKI`` or ``HTML``
        """
        sec_title = ""
        sec_level = 2
        if self.extract_format == ExtractFormat.WIKI:  # type: ignore[attr-defined]
            sec_title = match.group(2).strip()
            sec_level = len(match.group(1))
        elif self.extract_format == ExtractFormat.HTML:  # type: ignore[attr-defined]
            sec_title = match.group(5).strip()
            sec_level = int(match.group(1).strip())

        section = WikipediaPageSection(self, sec_title, sec_level - 1)  # type: ignore[arg-type]
        return section

    def _build_extracts(self, extract: Any, page: "BaseWikipediaPage[Any]") -> str:
        """
        Parse an ``extracts`` API response and populate page text structures.

        Splits the raw extract string on section-header patterns (wiki markup
        ``==Title==`` or HTML ``<h2>…</h2>``), builds the nested
        :class:`WikipediaPageSection` tree, populates ``page._summary`` with
        the introductory text that precedes the first section, and fills
        ``page._section_mapping`` with a title-to-sections index.

        For pages that have no sections the entire extract becomes the summary.

        :param extract: single page entry from ``raw["query"]["pages"]``;
            must contain an ``"extract"`` key
        :param page: page object to populate in-place
        :return: the introductory summary string (also stored on ``page._summary``)
        :invariant: ``self.extract_format`` must be ``WIKI`` or ``HTML``
        """
        page._summary = ""
        page._section_mapping = defaultdict(list)

        self._common_attributes(extract, page)

        section_stack: list[Any] = [page]
        section = None
        prev_pos = 0

        for match in re.finditer(
            RE_SECTION[self.extract_format], extract["extract"]  # type: ignore[attr-defined]
        ):
            if len(page._section_mapping) == 0:
                page._summary = extract["extract"][0 : match.start()].strip()
            elif section is not None:
                section._text = (extract["extract"][prev_pos : match.start()]).strip()

            section = self._create_section(match)
            sec_level = section.level + 1

            if sec_level > len(section_stack):
                section_stack.append(section)
            elif sec_level == len(section_stack):
                section_stack.pop()
                section_stack.append(section)
            else:
                for _ in range(len(section_stack) - sec_level + 1):
                    section_stack.pop()
                section_stack.append(section)

            section_stack[len(section_stack) - 2]._section.append(section)
            # section_stack[sec_level - 1]._section.append(section)

            prev_pos = match.end()
            page._section_mapping[section.title].append(section)

        # pages without sections have only summary
        if page._summary == "":
            page._summary = extract["extract"].strip()

        if prev_pos > 0 and section is not None:
            section._text = extract["extract"][prev_pos:]

        return page._summary

    def _build_info(self, extract: Any, page: _PageP) -> _PageP:
        """
        Populate a page from an ``info`` API response.

        Copies every key–value pair from *extract* (the per-page dict returned
        under ``raw["query"]["pages"]``) directly into ``page._attributes``,
        which makes them accessible as page properties.  Common attributes
        (title, pageid, ns, redirects) are also applied via
        :meth:`_common_attributes`.

        :param extract: single page entry from ``raw["query"]["pages"]``
        :param page: page object to populate in-place
        :return: the same *page* instance (now populated)
        """
        self._common_attributes(extract, page)
        for k, v in extract.items():
            page._attributes[k] = v
        return page

    def _build_langlinks(self, extract: Any, page: "BaseWikipediaPage[Any]") -> dict[str, Any]:
        """
        Build the language-link map from a ``langlinks`` API response.

        Creates a stub :class:`WikipediaPage` (or :class:`AsyncWikipediaPage`)
        for each language link, keyed by the two-letter language code.  The
        canonical URL returned by the API is preserved on each stub page.
        Resets ``page._langlinks`` before filling it.

        :param extract: single page entry from ``raw["query"]["pages"]``;
            may contain a ``"langlinks"`` list
        :param page: page object whose ``_langlinks`` dict is replaced
        :return: ``page._langlinks`` mapping ``{language_code: WikipediaPage}``
        """
        page._langlinks = {}
        self._common_attributes(extract, page)
        for langlink in extract.get("langlinks", []):
            p = self._make_page(
                title=langlink["*"],
                ns=Namespace.MAIN,
                language=langlink["lang"],
                url=langlink["url"],
            )
            page._langlinks[p.language] = p
        return page._langlinks

    def _build_links(self, extract: Any, page: "BaseWikipediaPage[Any]") -> dict[str, Any]:
        """
        Build the outgoing-links map from a ``links`` API response.

        Creates a stub page for each linked article, keyed by title.  The
        stub pages inherit the source page's language and variant so that
        lazy fetching works transparently.  Resets ``page._links`` before
        filling it.

        :param extract: single page entry from ``raw["query"]["pages"]``;
            may contain a ``"links"`` list
        :param page: page object whose ``_links`` dict is replaced
        :return: ``page._links`` mapping ``{title: WikipediaPage}``
        """
        page._links = {}
        self._common_attributes(extract, page)
        for link in extract.get("links", []):
            page._links[link["title"]] = self._make_page(
                title=link["title"],
                ns=int(link["ns"]),
                language=page.language,
                variant=page.variant,
            )
        return page._links

    def _build_backlinks(self, extract: Any, page: "BaseWikipediaPage[Any]") -> dict[str, Any]:
        """
        Build the backlinks map from a ``backlinks`` API response.

        Creates a stub page for each page that links *to* this page, keyed by
        title.  Unlike prop-based responses the raw data lives under
        ``raw["query"]["backlinks"]`` (top-level list), not inside a pages
        dict.  Resets ``page._backlinks`` before filling it.

        :param extract: ``raw["query"]`` dict (not a single pages entry);
            may contain a ``"backlinks"`` list
        :param page: page object whose ``_backlinks`` dict is replaced
        :return: ``page._backlinks`` mapping ``{title: WikipediaPage}``
        """
        page._backlinks = {}
        self._common_attributes(extract, page)
        for backlink in extract.get("backlinks", []):
            page._backlinks[backlink["title"]] = self._make_page(
                title=backlink["title"],
                ns=int(backlink["ns"]),
                language=page.language,
                variant=page.variant,
            )
        return page._backlinks

    def _build_categories(self, extract: Any, page: "BaseWikipediaPage[Any]") -> dict[str, Any]:
        """
        Build the categories map from a ``categories`` API response.

        Creates a stub page for each category the source page belongs to,
        keyed by the full category title (including the ``Category:`` prefix).
        Resets ``page._categories`` before filling it.

        :param extract: single page entry from ``raw["query"]["pages"]``;
            may contain a ``"categories"`` list
        :param page: page object whose ``_categories`` dict is replaced
        :return: ``page._categories`` mapping ``{title: WikipediaPage}``
        """
        page._categories = {}
        self._common_attributes(extract, page)
        for category in extract.get("categories", []):
            page._categories[category["title"]] = self._make_page(
                title=category["title"],
                ns=int(category["ns"]),
                language=page.language,
                variant=page.variant,
            )
        return page._categories

    def _build_categorymembers(
        self, extract: Any, page: "BaseWikipediaPage[Any]"
    ) -> dict[str, Any]:
        """
        Build the category-members map from a ``categorymembers`` API response.

        Creates a stub page for each member of the category, keyed by title.
        Unlike most prop responses, the raw data lives under
        ``raw["query"]["categorymembers"]``.  Each stub has its ``pageid``
        pre-set from the API response.  Resets ``page._categorymembers``
        before filling it.

        :param extract: ``raw["query"]`` dict (not a single pages entry);
            may contain a ``"categorymembers"`` list
        :param page: page object whose ``_categorymembers`` dict is replaced
        :return: ``page._categorymembers`` mapping ``{title: WikipediaPage}``
        """
        page._categorymembers = {}
        self._common_attributes(extract, page)
        for member in extract.get("categorymembers", []):
            p = self._make_page(
                title=member["title"],
                ns=int(member["ns"]),
                language=page.language,
                variant=page.variant,
            )
            p._attributes["pageid"] = member["pageid"]
            page._categorymembers[member["title"]] = p
        return page._categorymembers

    def _process_prop_response(
        self,
        raw: dict[str, Any],
        page: "BaseWikipediaPage[Any]",
        empty: T,
        builder: Callable[[Any, Any], T],
    ) -> T:
        """
        Process a standard single-fetch prop-query response.

        Updates common page attributes from the ``query`` block, then iterates
        over ``raw["query"]["pages"]``.  If the only page key is ``"-1"`` the
        page does not exist; ``pageid`` is set to a deterministic negative
        value and *empty* is returned.  Otherwise the first real page entry
        is passed to *builder*.

        Called by :meth:`_dispatch_prop` and :meth:`_async_dispatch_prop`.

        :param raw: full API JSON response (must contain ``raw["query"]["pages"]``)
        :param page: page object to update in-place
        :param empty: sentinel value returned for missing pages
        :param builder: ``_build_*`` method that parses one pages-entry and
            returns the same type as *empty*
        :return: result of *builder* for existing pages; *empty* otherwise
        """
        self._common_attributes(raw["query"], page)
        for k, v in raw["query"]["pages"].items():
            if k == "-1":
                page._attributes["pageid"] = self._missing_pageid(page)
                return empty
            return builder(v, page)
        return empty

    def _dispatch_prop(
        self,
        page: "BaseWikipediaPage[Any]",
        params: dict[str, Any],
        empty: T,
        builder: Callable[[Any, Any], T],
    ) -> T:
        """
        Execute a single-fetch prop-query and return the parsed result.

        Calls ``self._get`` (provided by :class:`SyncHTTPClient`) with the
        fully merged params, then delegates response processing to
        :meth:`_process_prop_response`.  Use for API props that fit in one
        page of results (e.g. ``extracts``, ``info``, ``langlinks``,
        ``categories``).

        :param page: source page; its language drives the API endpoint URL
        :param params: pre-built API params from a ``_*_params`` method
        :param empty: value to return when the page does not exist
        :param builder: ``_build_*`` method to call on the raw response
        :return: result of *builder*, or *empty* for missing pages
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        :invariant: must only be called on a :class:`WikipediaResource`
            instance (needs synchronous ``_get``)
        """
        raw = self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, params)
        )
        return self._process_prop_response(raw, page, empty, builder)

    async def _async_dispatch_prop(
        self,
        page: "BaseWikipediaPage[Any]",
        params: dict[str, Any],
        empty: T,
        builder: Callable[[Any, Any], T],
    ) -> T:
        """
        Async version of :meth:`_dispatch_prop`.

        Awaits ``self._get`` (provided by :class:`AsyncHTTPClient`), then
        delegates to :meth:`_process_prop_response`.  Semantics and parameters
        are identical to :meth:`_dispatch_prop`.

        :param page: source page; its language drives the API endpoint URL
        :param params: pre-built API params from a ``_*_params`` method
        :param empty: value to return when the page does not exist
        :param builder: ``_build_*`` method to call on the raw response
        :return: result of *builder*, or *empty* for missing pages
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        :invariant: must only be called on an :class:`AsyncWikipediaResource`
            instance (needs asynchronous ``_get``)
        """
        raw = await self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, params)
        )
        return self._process_prop_response(raw, page, empty, builder)

    def _dispatch_prop_paginated(
        self,
        page: "BaseWikipediaPage[Any]",
        params: dict[str, Any],
        continue_key: str,
        list_key: str,
        builder: Callable[[Any, Any], dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Execute a prop-query that may span multiple pages via inner-loop pagination.

        Used for props like ``links`` where the continuation cursor lives inside
        ``raw["continue"]`` and the accumulated data is under
        ``raw["query"]["pages"][page_id][list_key]``.  Issues repeated ``_get``
        calls until ``"continue"`` is absent from the response, appending
        each batch to the first page's list in-place.

        Returns ``{}`` immediately if the page does not exist (API key ``"-1"``)
        or if the pages dict is empty.

        :param page: source page
        :param params: initial API params (mutated in-place to add the
            continuation key on subsequent requests)
        :param continue_key: API continuation parameter name (e.g.
            ``"plcontinue"``)
        :param list_key: key within the page entry that holds the list to
            accumulate (e.g. ``"links"``)
        :param builder: ``_build_*`` method called once all pages are fetched
        :return: result of *builder*, or ``{}`` for missing pages
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        :invariant: must only be called on a :class:`WikipediaResource`
            instance (needs synchronous ``_get``)
        """
        raw = self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, params)
        )
        self._common_attributes(raw["query"], page)
        for k, v in raw["query"]["pages"].items():
            if k == "-1":
                page._attributes["pageid"] = self._missing_pageid(page)
                return {}
            while "continue" in raw:
                params[continue_key] = raw["continue"][continue_key]
                raw = self._get(  # type: ignore[attr-defined]
                    page.language, self._construct_params(page, params)
                )
                v[list_key] += raw["query"]["pages"][k][list_key]
            return builder(v, page)
        return {}

    async def _async_dispatch_prop_paginated(
        self,
        page: "BaseWikipediaPage[Any]",
        params: dict[str, Any],
        continue_key: str,
        list_key: str,
        builder: Callable[[Any, Any], dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Async version of :meth:`_dispatch_prop_paginated`.

        Semantics and parameters are identical to
        :meth:`_dispatch_prop_paginated`; awaits ``self._get`` on every
        request.

        :param page: source page
        :param params: initial API params (mutated in-place to add the
            continuation key on subsequent requests)
        :param continue_key: API continuation parameter name
        :param list_key: key within the page entry that holds the list
        :param builder: ``_build_*`` method called once all pages are fetched
        :return: result of *builder*, or ``{}`` for missing pages
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        :invariant: must only be called on an :class:`AsyncWikipediaResource`
            instance (needs asynchronous ``_get``)
        """
        raw = await self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, params)
        )
        self._common_attributes(raw["query"], page)
        for k, v in raw["query"]["pages"].items():
            if k == "-1":
                page._attributes["pageid"] = self._missing_pageid(page)
                return {}
            while "continue" in raw:
                params[continue_key] = raw["continue"][continue_key]
                raw = await self._get(  # type: ignore[attr-defined]
                    page.language, self._construct_params(page, params)
                )
                v[list_key] += raw["query"]["pages"][k][list_key]
            return builder(v, page)
        return {}

    def _dispatch_list(
        self,
        page: "BaseWikipediaPage[Any]",
        params: dict[str, Any],
        continue_key: str,
        list_key: str,
        builder: Callable[[Any, Any], dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Execute a list-query that may span multiple pages via top-level pagination.

        Used for list-style queries like ``backlinks`` and ``categorymembers``
        where the result list lives directly under ``raw["query"][list_key]``
        (not nested inside a pages dict).  Issues repeated ``_get`` calls
        until ``"continue"`` is absent, merging each batch by concatenating
        ``raw["query"][list_key]`` lists in-place.

        :param page: source page
        :param params: initial API params (mutated in-place to add the
            continuation key on subsequent requests)
        :param continue_key: API continuation parameter name (e.g.
            ``"blcontinue"``, ``"cmcontinue"``)
        :param list_key: top-level key under ``raw["query"]`` holding the
            list to accumulate (e.g. ``"backlinks"``, ``"categorymembers"``)
        :param builder: ``_build_*`` method called once all pages are fetched
        :return: result of *builder*
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        :invariant: must only be called on a :class:`WikipediaResource`
            instance (needs synchronous ``_get``)
        """
        raw = self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, params)
        )
        self._common_attributes(raw["query"], page)
        v = raw["query"]
        while "continue" in raw:
            params[continue_key] = raw["continue"][continue_key]
            raw = self._get(  # type: ignore[attr-defined]
                page.language, self._construct_params(page, params)
            )
            v[list_key] += raw["query"][list_key]
        return builder(v, page)

    async def _async_dispatch_list(
        self,
        page: "BaseWikipediaPage[Any]",
        params: dict[str, Any],
        continue_key: str,
        list_key: str,
        builder: Callable[[Any, Any], dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Async version of :meth:`_dispatch_list`.

        Semantics and parameters are identical to :meth:`_dispatch_list`;
        awaits ``self._get`` on every request.

        :param page: source page
        :param params: initial API params (mutated in-place to add the
            continuation key on subsequent requests)
        :param continue_key: API continuation parameter name
        :param list_key: top-level key under ``raw["query"]`` holding the list
        :param builder: ``_build_*`` method called once all pages are fetched
        :return: result of *builder*
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        :invariant: must only be called on an :class:`AsyncWikipediaResource`
            instance (needs asynchronous ``_get``)
        """
        raw = await self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, params)
        )
        self._common_attributes(raw["query"], page)
        v = raw["query"]
        while "continue" in raw:
            params[continue_key] = raw["continue"][continue_key]
            raw = await self._get(  # type: ignore[attr-defined]
                page.language, self._construct_params(page, params)
            )
            v[list_key] += raw["query"][list_key]
        return builder(v, page)

    def _extracts_params(self, page: "BaseWikipediaPage[Any]", **kwargs: Any) -> dict[str, Any]:
        """
        Build params for the ``extracts`` prop query.

        Sets ``explaintext=1`` and ``exsectionformat=wiki`` when
        ``extract_format`` is :attr:`ExtractFormat.WIKI`; leaves those params
        absent for HTML so the API returns HTML markup.  Any *kwargs* are
        merged in last and override the defaults (e.g. ``exsentences=1``).

        :param page: source page (provides ``title``)
        :param kwargs: extra API parameters forwarded verbatim
        :return: params dict ready for :meth:`_dispatch_prop`
        :invariant: ``self.extract_format`` must be ``WIKI`` or ``HTML``
        """
        params: dict[str, Any] = {
            "action": "query",
            "prop": "extracts",
            "titles": page.title,
        }
        if self.extract_format == ExtractFormat.HTML:  # type: ignore[attr-defined]
            pass
        elif self.extract_format == ExtractFormat.WIKI:  # type: ignore[attr-defined]
            params["explaintext"] = 1
            params["exsectionformat"] = "wiki"
        params.update(kwargs)
        return params

    def _info_params(self, page: "BaseWikipediaPage[Any]") -> dict[str, Any]:
        """
        Build params for the ``info`` prop query.

        Requests a fixed comprehensive set of ``inprop`` sub-properties
        (protection, talkid, watched, watchers, visitingwatchers,
        notificationtimestamp, subjectid, url, readable, preload,
        displaytitle, varianttitles) in one API call.

        :param page: source page (provides ``title``)
        :return: params dict ready for :meth:`_dispatch_prop`
        """
        return {
            "action": "query",
            "prop": "info",
            "titles": page.title,
            "inprop": "|".join(
                [
                    "protection",
                    "talkid",
                    "watched",
                    "watchers",
                    "visitingwatchers",
                    "notificationtimestamp",
                    "subjectid",
                    "url",
                    "readable",
                    "preload",
                    "displaytitle",
                    "varianttitles",
                ]
            ),
        }

    def _langlinks_params(self, page: "BaseWikipediaPage[Any]", **kwargs: Any) -> dict[str, Any]:
        """
        Build params for the ``langlinks`` prop query.

        Requests up to 500 language links per page together with their
        canonical URLs (``llprop=url``).  Any *kwargs* are merged last and
        override defaults (e.g. pass ``lllang="de"`` to filter by language).

        :param page: source page (provides ``title``)
        :param kwargs: extra API parameters forwarded verbatim
        :return: params dict ready for :meth:`_dispatch_prop`
        """
        params: dict[str, Any] = {
            "action": "query",
            "prop": "langlinks",
            "titles": page.title,
            "lllimit": 500,
            "llprop": "url",
        }
        params.update(kwargs)
        return params

    def _links_params(self, page: "BaseWikipediaPage[Any]") -> dict[str, Any]:
        """
        Build params for the ``links`` prop query.

        Requests up to 500 outgoing links per API response page.
        Pagination is handled automatically by
        :meth:`_dispatch_prop_paginated` using the ``plcontinue`` cursor.

        :param page: source page (provides ``title``)
        :return: base params dict; do **not** pass kwargs here — merge them
            at the call site as ``{**self._links_params(page), **kwargs}``
        """
        return {
            "action": "query",
            "prop": "links",
            "titles": page.title,
            "pllimit": 500,
        }

    def _backlinks_params(self, page: "BaseWikipediaPage[Any]") -> dict[str, Any]:
        """
        Build params for the ``backlinks`` list query.

        Requests up to 500 backlinks per API response page.  Pagination is
        handled automatically by :meth:`_dispatch_list` using the
        ``blcontinue`` cursor.

        :param page: source page (provides ``title`` as ``bltitle``)
        :return: base params dict; merge kwargs at the call site
        """
        return {
            "action": "query",
            "list": "backlinks",
            "bltitle": page.title,
            "bllimit": 500,
        }

    def _categories_params(self, page: "BaseWikipediaPage[Any]", **kwargs: Any) -> dict[str, Any]:
        """
        Build params for the ``categories`` prop query.

        Requests up to 500 categories per page.  Any *kwargs* are merged last
        (e.g. pass ``clshow="!hidden"`` to exclude hidden categories).

        :param page: source page (provides ``title``)
        :param kwargs: extra API parameters forwarded verbatim
        :return: params dict ready for :meth:`_dispatch_prop`
        """
        params: dict[str, Any] = {
            "action": "query",
            "prop": "categories",
            "titles": page.title,
            "cllimit": 500,
        }
        params.update(kwargs)
        return params

    def _categorymembers_params(self, page: "BaseWikipediaPage[Any]") -> dict[str, Any]:
        """
        Build params for the ``categorymembers`` list query.

        Requests up to 500 members per API response page.  Pagination is
        handled automatically by :meth:`_dispatch_list` using the
        ``cmcontinue`` cursor.

        :param page: source page (provides ``title`` as ``cmtitle``;
            must be in the ``Category:`` namespace)
        :return: base params dict; merge kwargs at the call site
        """
        return {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": page.title,
            "cmlimit": 500,
        }

    def _construct_params_standalone(self, params: dict[str, Any]) -> dict[str, Any]:
        """Merge caller-supplied params with mandatory API defaults (no page needed).

        Used for list queries (geosearch, random, search) that are not tied
        to a specific page.  Reads ``variant`` from the wiki client directly.

        Args:
            params: API-specific parameters produced by a ``_*_params`` method.

        Returns:
            Fully merged parameter dict ready to pass to ``_get``.
        """
        used_params: dict[str, Any] = {}
        if self.variant:  # type: ignore[attr-defined]
            used_params["variant"] = self.variant  # type: ignore[attr-defined]
        used_params["format"] = "json"
        used_params["redirects"] = 1
        used_params.update(params)
        if self._extra_api_params:  # type: ignore[attr-defined]
            used_params.update(self._extra_api_params)  # type: ignore[attr-defined]
        return used_params

    def _coordinates_api_params(
        self,
        page: "BaseWikipediaPage[Any]",
        params: CoordinatesParams,
    ) -> dict[str, Any]:
        """Build API params for ``prop=coordinates``.

        Args:
            page: Source page (provides ``title``).
            params: Clean-named coordinate parameters.

        Returns:
            Params dict ready for dispatch.
        """
        api_params: dict[str, Any] = {
            "action": "query",
            "prop": "coordinates",
            "titles": page.title,
        }
        api_params.update(params.to_api())
        return api_params

    def _images_api_params(
        self,
        page: "BaseWikipediaPage[Any]",
        params: ImagesParams,
    ) -> dict[str, Any]:
        """Build API params for ``prop=images``.

        Args:
            page: Source page (provides ``title``).
            params: Clean-named image parameters.

        Returns:
            Params dict ready for dispatch.
        """
        api_params: dict[str, Any] = {
            "action": "query",
            "prop": "images",
            "titles": page.title,
        }
        api_params.update(params.to_api())
        return api_params

    def _geosearch_api_params(self, params: GeoSearchParams) -> dict[str, Any]:
        """Build API params for ``list=geosearch``.

        Args:
            params: Clean-named geosearch parameters.

        Returns:
            Params dict ready for standalone dispatch.
        """
        api_params: dict[str, Any] = {
            "action": "query",
            "list": "geosearch",
        }
        api_params.update(params.to_api())
        return api_params

    def _random_api_params(self, params: RandomParams) -> dict[str, Any]:
        """Build API params for ``list=random``.

        Args:
            params: Clean-named random parameters.

        Returns:
            Params dict ready for standalone dispatch.
        """
        api_params: dict[str, Any] = {
            "action": "query",
            "list": "random",
        }
        api_params.update(params.to_api())
        return api_params

    def _search_api_params(self, params: SearchParams) -> dict[str, Any]:
        """Build API params for ``list=search``.

        Args:
            params: Clean-named search parameters.

        Returns:
            Params dict ready for standalone dispatch.
        """
        api_params: dict[str, Any] = {
            "action": "query",
            "list": "search",
        }
        api_params.update(params.to_api())
        return api_params

    def _build_coordinates_for_page(
        self,
        extract: dict[str, Any],
        page: "BaseWikipediaPage[Any]",
        params: CoordinatesParams,
    ) -> list[Coordinate]:
        """Parse coordinates from a single page API response entry.

        Builds :class:`Coordinate` objects from ``extract["coordinates"]``
        and stores them in the page's per-param cache.

        Args:
            extract: Single page entry from ``raw["query"]["pages"]``.
            page: Page object to populate in-place.
            params: The parameters used for this fetch (for cache key).

        Returns:
            List of :class:`Coordinate` objects.
        """
        self._common_attributes(extract, page)
        coords: list[Coordinate] = []
        for raw_coord in extract.get("coordinates", []):
            coords.append(
                Coordinate(
                    lat=float(raw_coord["lat"]),
                    lon=float(raw_coord["lon"]),
                    primary=raw_coord.get("primary", "") == "",
                    globe=raw_coord.get("globe", "earth"),
                    type=raw_coord.get("type"),
                    name=raw_coord.get("name"),
                    dim=raw_coord.get("dim"),
                    country=raw_coord.get("country"),
                    region=raw_coord.get("region"),
                    dist=raw_coord.get("dist"),
                )
            )
        page._set_cached("coordinates", params.cache_key(), coords)
        return coords

    def _build_images_for_page(
        self,
        extract: dict[str, Any],
        page: "BaseWikipediaPage[Any]",
        params: ImagesParams,
    ) -> ImagesDict:
        """Parse images from a single page API response entry.

        Builds a :class:`ImagesDict` of stub images from ``extract["images"]``
        and stores it in the page's per-param cache.

        Args:
            extract: Single page entry from ``raw["query"]["pages"]``.
            page: Page object to populate in-place.
            params: The parameters used for this fetch (for cache key).

        Returns:
            :class:`ImagesDict` keyed by image title.
        """
        self._common_attributes(extract, page)
        result = ImagesDict(wiki=self)
        for img in extract.get("images", []):
            result[img["title"]] = self._make_image(
                title=img["title"],
                ns=int(img.get("ns", 6)),
                language=page.language,
                variant=page.variant,
            )
        page._set_cached("images", params.cache_key(), result)
        return result  # type: ignore[no-any-return]

    def _build_geosearch_results(self, raw_query: dict[str, Any]) -> PagesDict:
        """Parse geosearch list results into a PagesDict.

        Creates :class:`WikipediaPage` stubs with pre-cached coordinates
        and :class:`GeoSearchMeta` sub-objects.

        Args:
            raw_query: The ``raw["query"]`` dict containing ``"geosearch"`` list.

        Returns:
            :class:`PagesDict` keyed by page title.
        """
        result = PagesDict(wiki=self)
        default_coords_key = CoordinatesParams().cache_key()
        for entry in raw_query.get("geosearch", []):
            p = self._make_page(
                title=entry["title"],
                ns=int(entry.get("ns", 0)),
                language=self.language,  # type: ignore[attr-defined]
                variant=self.variant,  # type: ignore[attr-defined]
            )
            p._attributes["pageid"] = entry.get("pageid", -1)
            is_primary = entry.get("primary", "") == ""
            lat = float(entry.get("lat", 0))
            lon = float(entry.get("lon", 0))
            dist = float(entry.get("dist", 0))
            p._geosearch_meta = GeoSearchMeta(dist=dist, lat=lat, lon=lon, primary=is_primary)
            coord = Coordinate(lat=lat, lon=lon, primary=is_primary, globe="earth")
            p._set_cached("coordinates", default_coords_key, [coord])
            result[entry["title"]] = p
        return result  # type: ignore[no-any-return]

    def _build_random_results(self, raw_query: dict[str, Any]) -> PagesDict:
        """Parse random list results into a PagesDict.

        Creates :class:`WikipediaPage` stubs with ``pageid`` pre-set.

        Args:
            raw_query: The ``raw["query"]`` dict containing ``"random"`` list.

        Returns:
            :class:`PagesDict` keyed by page title.
        """
        result = PagesDict(wiki=self)
        for entry in raw_query.get("random", []):
            p = self._make_page(
                title=entry["title"],
                ns=int(entry.get("ns", 0)),
                language=self.language,  # type: ignore[attr-defined]
                variant=self.variant,  # type: ignore[attr-defined]
            )
            p._attributes["pageid"] = entry.get("id", -1)
            result[entry["title"]] = p
        return result  # type: ignore[no-any-return]

    def _build_search_results(
        self,
        raw: dict[str, Any],
    ) -> SearchResults:
        """Parse search list results into a SearchResults wrapper.

        Creates :class:`WikipediaPage` stubs with :class:`SearchMeta`
        sub-objects and extracts aggregate metadata (totalhits, suggestion).

        Args:
            raw: The full API response dict.

        Returns:
            :class:`SearchResults` with pages, totalhits, and suggestion.
        """
        pages = PagesDict(wiki=self)
        raw_query = raw.get("query", {})
        for entry in raw_query.get("search", []):
            p = self._make_page(
                title=entry["title"],
                ns=int(entry.get("ns", 0)),
                language=self.language,  # type: ignore[attr-defined]
                variant=self.variant,  # type: ignore[attr-defined]
            )
            p._attributes["pageid"] = entry.get("pageid", -1)
            p._search_meta = SearchMeta(
                snippet=entry.get("snippet", ""),
                size=int(entry.get("size", 0)),
                wordcount=int(entry.get("wordcount", 0)),
                timestamp=entry.get("timestamp", ""),
            )
            pages[entry["title"]] = p

        searchinfo = raw_query.get("searchinfo", {})
        totalhits = int(searchinfo.get("totalhits", 0))
        suggestion = searchinfo.get("suggestion")

        return SearchResults(
            pages=pages,
            totalhits=totalhits,
            suggestion=suggestion,
        )

    def _dispatch_standalone_list(
        self,
        language: str,
        params: dict[str, Any],
        continue_key: str,
        list_key: str,
    ) -> dict[str, Any]:
        """Execute a standalone list-query with pagination (synchronous).

        Unlike :meth:`_dispatch_list`, this does not require a page parameter.
        Used for ``geosearch``, ``random``, and ``search``.

        Args:
            language: Language code for the API endpoint URL.
            params: Initial API params (mutated for continuation).
            continue_key: API continuation parameter name.
            list_key: Key under ``raw["query"]`` holding the list.

        Returns:
            The full ``raw["query"]`` dict with all pages merged.

        Raises:
            WikiHttpTimeoutError: If the request times out.
            WikiConnectionError: If a connection cannot be established.
            WikiRateLimitError: If the API returns HTTP 429.
            WikiHttpError: If the API returns a non-success HTTP status.
            WikiInvalidJsonError: If the response is not valid JSON.

        Invariants:
            Must only be called on a :class:`WikipediaResource` instance.
        """
        raw = self._get(  # type: ignore[attr-defined]
            language, self._construct_params_standalone(params)
        )
        v = raw.get("query", {})
        while "continue" in raw:
            params[continue_key] = raw["continue"][continue_key]
            raw = self._get(  # type: ignore[attr-defined]
                language, self._construct_params_standalone(params)
            )
            v[list_key] = v.get(list_key, []) + raw.get("query", {}).get(list_key, [])
        return raw  # type: ignore[no-any-return]

    async def _async_dispatch_standalone_list(
        self,
        language: str,
        params: dict[str, Any],
        continue_key: str,
        list_key: str,
    ) -> dict[str, Any]:
        """Async version of :meth:`_dispatch_standalone_list`.

        Args:
            language: Language code for the API endpoint URL.
            params: Initial API params (mutated for continuation).
            continue_key: API continuation parameter name.
            list_key: Key under ``raw["query"]`` holding the list.

        Returns:
            The full raw API response with all pages merged.

        Raises:
            WikiHttpTimeoutError: If the request times out.
            WikiConnectionError: If a connection cannot be established.
            WikiRateLimitError: If the API returns HTTP 429.
            WikiHttpError: If the API returns a non-success HTTP status.
            WikiInvalidJsonError: If the response is not valid JSON.

        Invariants:
            Must only be called on an :class:`AsyncWikipediaResource` instance.
        """
        raw = await self._get(  # type: ignore[attr-defined]
            language, self._construct_params_standalone(params)
        )
        v = raw.get("query", {})
        while "continue" in raw:
            params[continue_key] = raw["continue"][continue_key]
            raw = await self._get(  # type: ignore[attr-defined]
                language, self._construct_params_standalone(params)
            )
            v[list_key] = v.get(list_key, []) + raw.get("query", {}).get(list_key, [])
        return raw  # type: ignore[no-any-return]


class WikipediaResource(BaseWikipediaResource):
    """
    Synchronous mixin providing the public Wikipedia API surface.

    Combines :class:`BaseWikipediaResource` (parsing & dispatch logic) with
    :class:`~wikipediaapi._http_client.SyncHTTPClient` (blocking HTTP via
    ``httpx``) to form a concrete synchronous client.  Intended to be used
    via multiple inheritance::

        class Wikipedia(WikipediaResource, SyncHTTPClient): ...

    All API methods block until the HTTP response is received and parsed.
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
        attribute set and the canonical URL pre-populated.  Up to 500
        language links are returned in a single request.

        API reference:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blanglinks
        - https://www.mediawiki.org/wiki/API:Langlinks

        :param page: source page
        :param kwargs: extra API parameters (e.g. ``lllang="de"`` to filter
            to a single target language)
        :return: ``{language_code: WikipediaPage}``; ``{}`` if page missing
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return self._dispatch_prop(  # type: ignore[return-value]
            page,
            self._langlinks_params(page, **kwargs),
            {},
            self._build_langlinks,  # type: ignore[arg-type]
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
        :return: ``{title: WikipediaPage}``; ``{}`` if page missing
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return self._dispatch_prop_paginated(  # type: ignore[return-value]
            page, {**self._links_params(page), **kwargs}, "plcontinue", "links", self._build_links
        )

    def backlinks(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Fetch all pages that link to *page* and return them keyed by title.

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
        return self._dispatch_list(  # type: ignore[return-value]
            page,
            {**self._backlinks_params(page), **kwargs},
            "blcontinue",
            "backlinks",
            self._build_backlinks,
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
        :return: ``{title: WikipediaPage}``; ``{}`` if page missing
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return self._dispatch_prop(  # type: ignore[return-value]
            page,
            self._categories_params(page, **kwargs),
            {},
            self._build_categories,  # type: ignore[arg-type]
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
        return self._dispatch_list(  # type: ignore[return-value]
            page,
            {**self._categorymembers_params(page), **kwargs},
            "cmcontinue",
            "categorymembers",
            self._build_categorymembers,
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
        the result per parameter set.  ``page.coordinates`` (the property)
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
            List of :class:`Coordinate` objects; empty list if page missing.

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
        raw = self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, api_params)
        )
        self._common_attributes(raw.get("query", {}), page)
        for k, v in raw.get("query", {}).get("pages", {}).items():
            if k == "-1":
                page._attributes["pageid"] = self._missing_pageid(page)
                page._set_cached("coordinates", params.cache_key(), [])
                return []  # type: ignore[return-value]
            return self._build_coordinates_for_page(v, page, params)
        page._set_cached("coordinates", params.cache_key(), [])
        return []  # type: ignore[return-value]

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
        return result  # type: ignore[no-any-return]

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
        the result per parameter set.

        API reference:

        - https://www.mediawiki.org/wiki/API:Images

        Args:
            page: Page to fetch images for.
            limit: Maximum images to return (1–500).
            images: Specific images as an iterable.
            direction: Sort direction as :class:`WikiDirection`.

        Returns:
            :class:`ImagesDict` keyed by image title; empty if page missing.

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
            return self._build_images_for_page(v, page, params)
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
        return result  # type: ignore[no-any-return]

    def imageinfo(
        self,
        image: WikipediaImage,
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
    ) -> list[dict[str, Any]]:
        """Fetch detailed image information.

        Calls ``prop=imageinfo`` with automatic pagination and caches
        the result per parameter set.

        API reference:

        - https://www.mediawiki.org/wiki/API:Imageinfo

        Args:
            image: Image to fetch information for.
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
            Raw imageinfo data from the API response.

        Raises:
            WikiHttpTimeoutError: If the request times out.
            WikiConnectionError: If a connection cannot be established.
            WikiRateLimitError: If the API returns HTTP 429.
            WikiHttpError: If the API returns a non-success HTTP status.
            WikiInvalidJsonError: If the response is not valid JSON.
        """
        params = ImageInfoParams(
            props=props,  # type: ignore[call-arg]
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
        cache_key = f"imageinfo:{params.cache_key()}"
        cached = image._get_cached("imageinfo", cache_key)
        if not isinstance(cached, type(NOT_CACHED)):
            return cached  # type: ignore[no-any-return]

        api_params: dict[str, Any] = {
            "action": "query",
            "prop": "imageinfo",
            "titles": image.title,
        }
        api_params.update(params.to_api())
        raw = self._get(  # type: ignore[attr-defined]
            image.language, self._construct_params(image, api_params)  # type: ignore[arg-type]
        )

        # Extract imageinfo from response
        query = raw.get("query", {})
        pages = query.get("pages", {})
        for page_id, page_data in pages.items():
            if page_id == "-1":
                # Image doesn't exist
                image._set_cached("imageinfo", cache_key, [])
                return []  # type: ignore[return-value]
            imageinfo_list = page_data.get("imageinfo", [])

            # Handle pagination if needed
            while "continue" in raw:
                api_params["iicontinue"] = raw["continue"]["iicontinue"]
                raw = self._get(  # type: ignore[attr-defined]
                    image.language,
                    self._construct_params(image, api_params),  # type: ignore[arg-type]
                )
                continued_pages = raw.get("query", {}).get("pages", {})
                continued_data = continued_pages.get(page_id, {})
                continued_imageinfo = continued_data.get("imageinfo", [])
                imageinfo_list.extend(continued_imageinfo)

            image._set_cached("imageinfo", cache_key, imageinfo_list)
            return imageinfo_list

        # Fallback if no pages found
        image._set_cached("imageinfo", cache_key, [])
        return []  # type: ignore[return-value]

    def batch_imageinfo(
        self,
        images: list[WikipediaImage],
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
        """Batch-fetch image information for multiple images.

        Sends multi-title API requests (up to 50 titles per request)
        and distributes results to each image's cache.

        Args:
            images: List of images to fetch information for.
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
            ``{title: imageinfo_dict}`` for every image.
        """
        params = ImageInfoParams(
            props=props,  # type: ignore[call-arg]
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
        result: dict[str, dict[str, Any]] = {}
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
                dummy_image.language,  # type: ignore[arg-type]
                self._construct_params(dummy_image, api_params),  # type: ignore[arg-type]
            )

            norm_map = self._build_normalization_map(raw)
            for page_id, page_data in raw.get("query", {}).get("pages", {}).items():
                title = page_data.get("title", "")
                orig = norm_map.get(title, title)
                img = image_map.get(orig) or image_map.get(title)
                if img is not None:
                    imageinfo_list = page_data.get("imageinfo", [])

                    # Handle pagination if needed
                    while "continue" in raw:
                        api_params["iicontinue"] = raw["continue"]["iicontinue"]
                        raw = self._get(  # type: ignore[attr-defined]
                            dummy_image.language,
                            self._construct_params(
                                dummy_image, api_params  # type: ignore[arg-type]
                            ),
                        )
                        continued_pages = raw.get("query", {}).get("pages", {})
                        continued_data = continued_pages.get(page_id, {})
                        continued_imageinfo = continued_data.get("imageinfo", [])
                        imageinfo_list.extend(continued_imageinfo)

                    cache_key = f"imageinfo:{params.cache_key()}"
                    img._set_cached("imageinfo", cache_key, imageinfo_list)
                    result[title] = imageinfo_list[0] if imageinfo_list else {}

        for img in images:
            if img.title not in result:
                result[img.title] = {}

        return result  # type: ignore[no-any-return]

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

        All _build_* methods call _make_page to create stub pages,

                All ``_build_*`` methods call :meth:`_make_page` to create stub pages,
                so stub pages produced in an async context are automatically async.

                :param title: page title exactly as it appears in Wikipedia URLs
                :param ns: namespace constant
                :param language: two-letter language code
                :param variant: optional language variant; ``None`` for none
                :param url: optional canonical URL (used for lang-link stubs)
                :return: uninitialised :class:`AsyncWikipediaPage` instance
        """
        from .async_wikipedia_page import AsyncWikipediaPage

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
        """
        Override of BaseWikipediaResource._make_image that returns AsyncWikipediaImage.

        All _build_* methods call _make_image to create stub images,
        so stub images produced in an async context are automatically async.

        :param title: image title exactly as it appears in Wikipedia URLs
        :param ns: namespace constant
        :param language: two-letter language code
        :param variant: optional language variant; ``None`` for none
        :return: uninitialised :class:`AsyncWikipediaImage` instance
        """
        from .async_wikipedia_image import AsyncWikipediaImage

        return AsyncWikipediaImage(
            wiki=self,  # type: ignore[arg-type]
            title=title,
            ns=ns,
            language=language,
            variant=variant,
        )

    def _build_images_for_page(  # type: ignore[override]
        self,
        extract: dict[str, Any],
        page: "BaseWikipediaPage[Any]",
        params: ImagesParams,
    ) -> AsyncImagesDict:
        """Parse images from a single page API response entry.

        Builds a :class:`AsyncImagesDict` of stub images from ``extract["images"]``
        and stores it in the page's per-param cache.

        Args:
            extract: Single page entry from ``raw["query"]["pages"]``.
            page: Page object to populate in-place.
            params: The parameters used for this fetch (for cache key).

        Returns:
            :class:`AsyncImagesDict` keyed by image title.
        """
        self._common_attributes(extract, page)
        result = AsyncImagesDict(wiki=self)
        for img in extract.get("images", []):
            result[img["title"]] = self._make_image(
                title=img["title"],
                ns=int(img.get("ns", 6)),
                language=page.language,
                variant=page.variant,
            )
        page._set_cached("images", params.cache_key(), result)
        return result  # type: ignore[no-any-return]

    def page(
        self,
        title: str,
        ns: WikiNamespace = Namespace.MAIN,
        unquote: bool = False,
    ) -> "AsyncWikipediaPage":
        """
        Return an :class:`AsyncWikipediaPage` for the given title (lazy, no network call).

        Creates a stub async page bound to this instance.  No HTTP request is
        made at construction time; each property coroutine fetches its data
        on first ``await``.

        :param title: page title as it appears in Wikipedia URLs
        :param ns: namespace; defaults to :attr:`Namespace.MAIN`
        :param unquote: if ``True``, percent-decode *title* before use
        :return: :class:`AsyncWikipediaPage` bound to this instance
        """
        from .async_wikipedia_page import AsyncWikipediaPage

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
        return await self._async_dispatch_prop(  # type: ignore[return-value]
            page,
            self._langlinks_params(page, **kwargs),
            {},  # type: ignore[arg-type]
            self._build_langlinks,  # type: ignore[arg-type]
        )

    async def links(self, page: "AsyncWikipediaPage", **kwargs: Any) -> "AsyncPagesDict":
        """
        Async version of :meth:`WikipediaResource.links`.

        Fetches all outgoing wiki-links with automatic pagination.
        See :meth:`WikipediaResource.links` for full documentation.

        :param page: source page
        :param kwargs: extra API parameters (e.g. ``plnamespace=0``)
        :return: ``{title: AsyncWikipediaPage}``; ``{}`` if page missing
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return await self._async_dispatch_prop_paginated(  # type: ignore[return-value]
            page, {**self._links_params(page), **kwargs}, "plcontinue", "links", self._build_links
        )

    async def backlinks(self, page: "AsyncWikipediaPage", **kwargs: Any) -> "AsyncPagesDict":
        """
        Async version of :meth:`WikipediaResource.backlinks`.

        Fetches all pages linking to *page* with automatic pagination.
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
        return await self._async_dispatch_list(  # type: ignore[return-value]
            page,
            {**self._backlinks_params(page), **kwargs},
            "blcontinue",
            "backlinks",
            self._build_backlinks,
        )

    async def categories(self, page: "AsyncWikipediaPage", **kwargs: Any) -> "AsyncPagesDict":
        """
        Async version of :meth:`WikipediaResource.categories`.

        Fetches all categories this page belongs to, keyed by title.
        See :meth:`WikipediaResource.categories` for full documentation.

        :param page: source page
        :param kwargs: extra API parameters (e.g. ``clshow="!hidden"``)
        :return: ``{title: AsyncWikipediaPage}``; ``{}`` if page missing
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return await self._async_dispatch_prop(  # type: ignore[return-value]
            page,
            self._categories_params(page, **kwargs),
            {},  # type: ignore[arg-type]
            self._build_categories,  # type: ignore[arg-type]
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
        return await self._async_dispatch_list(  # type: ignore[return-value]
            page,
            {**self._categorymembers_params(page), **kwargs},
            "cmcontinue",
            "categorymembers",
            self._build_categorymembers,
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

        Args:
            page: Page to fetch coordinates for.
            limit: Maximum coordinates to return (1–500).
            primary: Which coordinates: ``"primary"``, ``"secondary"``, ``"all"``.
            prop: Additional properties as an iterable.
            distance_from_point: Reference point as :class:`GeoPoint`.
            distance_from_page: Reference page.

        Returns:
            List of :class:`Coordinate` objects; empty list if page missing.
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
                return []  # type: ignore[return-value]
            return self._build_coordinates_for_page(v, page, params)
        page._set_cached("coordinates", params.cache_key(), [])
        return []  # type: ignore[return-value]

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

        Args:
            pages: List of pages to fetch coordinates for.
            limit: Maximum coordinates per page (1–500).
            primary: Which coordinates: ``"primary"``, ``"secondary"``, ``"all"``.
            prop: Additional properties as an iterable.
            distance_from_point: Reference point as ``"lat|lon"``.
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
        result: "dict[AsyncWikipediaPage, list[Coordinate]]" = {}
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
        return result  # type: ignore[no-any-return]

    async def images(
        self,
        page: "AsyncWikipediaPage",
        *,
        limit: int = 10,
        images: Iterable[str] | None = None,
        direction: WikiDirection = Direction.ASCENDING,
    ) -> AsyncImagesDict:
        """Async version of :meth:`WikipediaResource.images`.

        See :meth:`WikipediaResource.images` for full documentation.

        Args:
            page: Page to fetch images for.
            limit: Maximum images to return (1–500).
            images: Specific images as an iterable.
            direction: Sort direction as :class:`WikiDirection`.

        Returns:
            :class:`AsyncImagesDict` keyed by image title; empty if page missing.
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
                empty_pd: AsyncImagesDict = AsyncImagesDict(wiki=self)
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
            return self._build_images_for_page(v, page, params)
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
    ) -> dict[str, AsyncImagesDict]:
        """Async version of :meth:`WikipediaResource.batch_images`.

        See :meth:`WikipediaResource.batch_images` for full documentation.

        Args:
            pages: List of pages to fetch images for.
            limit: Maximum images per page (1–500).
            images: Specific images as an iterable.
            direction: Sort direction as :class:`WikiDirection`.

        Returns:
            ``{title: AsyncImagesDict}`` for every page.
        """
        params = ImagesParams(limit=limit, images=images, direction=direction)
        result: dict[str, AsyncImagesDict] = {}
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
                    result[title] = imgs
        for p in pages:
            if p.title not in result:
                result[p.title] = AsyncImagesDict(wiki=self)
        return result  # type: ignore[no-any-return]

    async def imageinfo(
        self,
        image: "AsyncWikipediaImage",
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
    ) -> dict[str, Any]:
        """Async version of :meth:`WikipediaResource.imageinfo`.

        See :meth:`WikipediaResource.imageinfo` for full documentation.

        Args:
            image: Image to fetch information for.
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
            Raw imageinfo data from the API response.
        """
        params = ImageInfoParams(
            props=props,  # type: ignore[call-arg]
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
        cache_key = f"imageinfo:{params.cache_key()}"
        cached = image._get_cached("imageinfo", cache_key)
        if not isinstance(cached, type(NOT_CACHED)):
            return cached  # type: ignore[no-any-return]

        api_params: dict[str, Any] = {
            "action": "query",
            "prop": "imageinfo",
            "titles": image.title,
        }
        api_params.update(params.to_api())
        raw = await self._get(  # type: ignore[attr-defined]
            image.language, self._construct_params(image, api_params)
        )

        # Extract imageinfo from response
        query = raw.get("query", {})
        pages = query.get("pages", {})
        for page_id, page_data in pages.items():
            if page_id == "-1":
                # Image doesn't exist
                image._set_cached("imageinfo", cache_key, [])
                return []  # type: ignore[return-value]
            imageinfo_list = page_data.get("imageinfo", [])

            # Handle pagination if needed
            while "continue" in raw:
                api_params["iicontinue"] = raw["continue"]["iicontinue"]
                raw = await self._get(  # type: ignore[attr-defined]
                    image.language, self._construct_params(image, api_params)
                )
                continued_pages = raw.get("query", {}).get("pages", {})
                continued_data = continued_pages.get(page_id, {})
                continued_imageinfo = continued_data.get("imageinfo", [])
                imageinfo_list.extend(continued_imageinfo)

            image._set_cached("imageinfo", cache_key, imageinfo_list)
            return imageinfo_list

        # Fallback if no pages found
        image._set_cached("imageinfo", cache_key, [])
        return []  # type: ignore[return-value]

    async def batch_imageinfo(
        self,
        images: list["AsyncWikipediaImage"],
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
        """Async version of :meth:`WikipediaResource.batch_imageinfo`.

        See :meth:`WikipediaResource.batch_imageinfo` for full documentation.

        Args:
            images: List of images to fetch information for.
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
            ``{title: imageinfo_dict}`` for every image.
        """
        params = ImageInfoParams(
            props=props,  # type: ignore[call-arg]
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
        result: dict[str, dict[str, Any]] = {}
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
                dummy_image.language,
                self._construct_params(dummy_image, api_params),  # type: ignore[arg-type]
            )

            norm_map = self._build_normalization_map(raw)
            for page_id, page_data in raw.get("query", {}).get("pages", {}).items():
                title = page_data.get("title", "")
                orig = norm_map.get(title, title)
                img = image_map.get(orig) or image_map.get(title)
                if img is not None:
                    imageinfo_list = page_data.get("imageinfo", [])

                    # Handle pagination if needed
                    while "continue" in raw:
                        api_params["iicontinue"] = raw["continue"]["iicontinue"]
                        raw = await self._get(  # type: ignore[attr-defined]
                            dummy_image.language,
                            self._construct_params(
                                dummy_image, api_params  # type: ignore[arg-type]
                            ),
                        )
                        continued_pages = raw.get("query", {}).get("pages", {})
                        continued_data = continued_pages.get(page_id, {})
                        continued_imageinfo = continued_data.get("imageinfo", [])
                        imageinfo_list.extend(continued_imageinfo)

                    cache_key = f"imageinfo:{params.cache_key()}"
                    img._set_cached("imageinfo", cache_key, imageinfo_list)
                    result[title] = imageinfo_list[0] if imageinfo_list else {}

        for img in images:
            if img.title not in result:
                result[img.title] = {}

        return result  # type: ignore[no-any-return]

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
    ) -> PagesDict:
        """Async version of :meth:`WikipediaResource.geosearch`.

        See :meth:`WikipediaResource.geosearch` for full documentation.

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
        raw = await self._get(  # type: ignore[attr-defined]
            self.language,  # type: ignore[attr-defined]
            self._construct_params_standalone(api_params),
        )
        return self._build_geosearch_results(raw.get("query", {}))

    async def random(
        self,
        *,
        ns: WikiNamespace = Namespace.MAIN,
        filter_redirect: WikiRedirectFilter = RedirectFilter.NONREDIRECTS,
        min_size: int | None = None,
        max_size: int | None = None,
        limit: int = 1,
    ) -> PagesDict:
        """Async version of :meth:`WikipediaResource.random`.

        See :meth:`WikipediaResource.random` for full documentation.

        Args:
            ns: Restrict to this namespace number.
            filter_redirect: Redirect filter.
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
        # _async_dispatch_standalone_list would loop forever.
        raw = await self._get(  # type: ignore[attr-defined]
            self.language,  # type: ignore[attr-defined]
            self._construct_params_standalone(api_params),
        )
        return self._build_random_results(raw.get("query", {}))

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

        Args:
            query: Search string (required).
            ns: Namespace to search in.
            limit: Maximum results to return (1–500).
            prop: Properties as an iterable.
            info: Metadata as an iterable.
            sort: Sort order.
            what: Search type.
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
        raw = await self._get(  # type: ignore[attr-defined]
            self.language,  # type: ignore[attr-defined]
            self._construct_params_standalone(api_params),
        )
        return self._build_search_results(raw)

    def pages(
        self,
        titles: list[str],
        ns: WikiNamespace = Namespace.MAIN,
    ) -> AsyncPagesDict:
        """Create an :class:`AsyncPagesDict` of lazy page stubs.

        No network call is made; each page fetches data on demand.

        Args:
            titles: List of page titles.
            ns: Namespace for all pages; defaults to :attr:`Namespace.MAIN`.

        Returns:
            :class:`AsyncPagesDict` keyed by title.
        """
        data = {t: self.page(t, ns=ns) for t in titles}
        return AsyncPagesDict(wiki=self, data=data)
