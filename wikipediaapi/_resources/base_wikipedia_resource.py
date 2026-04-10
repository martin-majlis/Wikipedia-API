import re
from abc import ABC
from collections import defaultdict
from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeVar

from .._enums import Namespace
from .._enums import WikiNamespace
from .._page._base_wikipedia_page import BaseWikipediaPage
from .._page.wikipedia_page import WikipediaPage
from .._page.wikipedia_page_section import WikipediaPageSection
from .._pages_dict import PagesDict
from .._params.coordinates_params import CoordinatesParams
from .._params.geo_search_params import GeoSearchParams
from .._params.imageinfo_params import ImageInfoParams
from .._params.images_params import ImagesParams
from .._params.random_params import RandomParams
from .._params.search_params import SearchParams
from .._types import Coordinate
from .._types import GeoSearchMeta
from .._types import ImageInfo
from .._types import SearchMeta
from .._types import SearchResults
from ..extract_format import ExtractFormat

if TYPE_CHECKING:
    from .._pages_dict import ImagesDict

T = TypeVar("T")
_PageP = TypeVar("_PageP", bound=BaseWikipediaPage)

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
    ``_get(language, params)`` method (sync or async) and instance
    attributes ``extract_format`` and ``_extra_api_params``.

    Subclassing convention:

    * Synchronous clients inherit :class:`WikipediaResource` and
      :class:`~wikipediaapi._http_client.SyncHTTPClient`.
    * Asynchronous clients inherit :class:`AsyncWikipediaResource` and
      :class:`~wikipediaapi._http_client.AsyncHTTPClient`.
    """

    # Attributes provided by BaseHTTPClient via multiple inheritance in concrete subclasses
    language: str
    variant: str | None
    extract_format: "ExtractFormat"
    _extra_api_params: dict[str, Any] | None

    if TYPE_CHECKING:

        def _get(self, language: str, params: dict[str, Any]) -> Any: ...

    def _construct_params(
        self, page: "BaseWikipediaPage[Any]", params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Merge caller-supplied params with mandatory API defaults.

        Adds ``format=json``, ``redirects=1``, an optional ``variant`` (when
        set on *page*), and any instance-level ``_extra_api_params``.  Caller
        params take precedence over defaults; ``_extra_api_params`` take
        precedence over everything.

        :param page: source page, used to read ``page.variant``
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
    ) -> "BaseWikipediaPage[Any]":
        """Create a stub :class:`WikipediaImage` bound to this resource instance.

        The returned image is *not* yet populated with API data; it will fetch
        lazily when its properties are accessed.  Overridden in
        :class:`AsyncWikipediaResource` to return :class:`AsyncWikipediaImage`.

        :param title: file title including the ``File:`` prefix
        :param ns: namespace constant (typically 6 for files)
        :param language: two-letter language code (e.g. ``"en"``)
        :param variant: optional language variant; ``None`` for none
        :return: uninitialised :class:`WikipediaImage` instance
        """
        from .._image.wikipedia_image import WikipediaImage  # avoid circular import

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
        This method reads ``normalized`` block from a raw API response
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
            current Python process.
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
        (if present) and stores them on page.  Safe to call multiple times;
        later calls overwrite earlier values for same keys.

        :param extract: dict from API response (a ``query`` block or
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

        * :attr:`ExtractFormat.WIKI` — group 2 is title, group 1 gives
          heading depth via ``len()``.
        * :attr:`ExtractFormat.HTML` — group 5 is title, group 1 is
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

        Splits raw extract string on section-header patterns (wiki markup
        ``==Title==`` or HTML ``<h2>…</h2>``), builds nested
        :class:`WikipediaPageSection` tree, populates ``page._summary`` with
        introductory text that precedes first section, and fills
        ``page._section_mapping`` with a title-to-sections index.

        For pages that have no sections entire extract becomes summary.

        :param extract: single page entry from ``raw["query"]["pages"]``;
            must contain an ``"extract"`` key
        :param page: page object to populate in-place
        :return: introductory summary string (also stored on ``page._summary``)
        :invariant: ``self.extract_format`` must be ``WIKI`` or ``HTML``
        """
        page._summary = ""
        page._section_mapping = defaultdict(list)

        self._common_attributes(extract, page)

        section_stack: list[Any] = [page]
        section = None
        prev_pos = 0

        for match in re.finditer(
            RE_SECTION[self.extract_format],
            extract["extract"],  # type: ignore[attr-defined]
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
        :return: same *page* instance (now populated)
        """
        self._common_attributes(extract, page)
        for k, v in extract.items():
            page._attributes[k] = v
        return page

    def _build_langlinks(self, extract: Any, page: "BaseWikipediaPage[Any]") -> dict[str, Any]:
        """
        Build language-link map from a ``langlinks`` API response.

        Creates a stub :class:`WikipediaPage` (or :class:`AsyncWikipediaPage`)
        for each language link, keyed by two-letter language code.  The
        canonical URL returned by API is preserved on each stub page.
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
        Build outgoing-links map from a ``links`` API response.

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
        Build backlinks map from a ``backlinks`` API response.

        Creates a stub page for each page that links *to* this page, keyed by
        title.  Unlike prop-based responses raw data lives under
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
        Build categories map from a ``categories`` API response.

        Creates a stub page for each category the source page belongs to,
        keyed by full category title (including ``Category:`` prefix).
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
        Build category-members map from a ``categorymembers`` API response.

        Creates a stub page for each member of the category, keyed by title.
        Unlike most prop responses, raw data lives under
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

        Updates common page attributes from ``query`` block, then iterates
        over ``raw["query"]["pages"]``.  If only page key is ``"-1"``
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
        Execute a single-fetch prop-query and return parsed result.

        Calls ``self._get`` (provided by :class:`SyncHTTPClient`) with
        fully merged params, then delegates response processing to
        :meth:`_process_prop_response`.  Use for API props that fit in one
        page of results (e.g. ``extracts``, ``info``, ``langlinks``,
        ``categories``).

        :param page: source page; its language drives the API endpoint URL
        :param params: pre-built API params from a ``_*_params`` method
        :param empty: value to return when the page does not exist
        :param builder: ``_build_*`` method to call on raw response
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
        :param builder: ``_build_*`` method to call on raw response
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
        ``raw["continue"]`` and accumulated data is under
        ``raw["query"]["pages"][page_id][list_key]``.  Issues repeated ``_get``
        calls until ``"continue"`` is absent from the response, appending
        each batch to the first page's list in-place.

        Returns ``{}`` immediately if the page does not exist (API key ``"-1"``)
        or if the pages dict is empty.

        :param page: source page
        :param params: initial API params (mutated in-place to add
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
        :param params: initial API params (mutated in-place to add
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
        :param params: initial API params (mutated in-place to add
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
        :param params: initial API params (mutated in-place to add
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
        Build params for ``extracts`` prop query.

        Sets ``explaintext=1`` and ``exsectionformat=wiki`` when
        ``extract_format`` is :attr:`ExtractFormat.WIKI`; leaves those params
        absent for HTML so the API returns HTML markup.  Any *kwargs* are
        merged in last and override defaults (e.g. ``exsentences=1``).

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
        Build params for ``info`` prop query.

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
        Build params for ``langlinks`` prop query.

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
        Build params for ``links`` prop query.

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
        Build params for ``backlinks`` list query.

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
        Build params for ``categories`` prop query.

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
        Build params for ``categorymembers`` list query.

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

    def _imageinfo_api_params(
        self,
        image: "BaseWikipediaPage[Any]",
        params: ImageInfoParams,
    ) -> dict[str, Any]:
        """Build API params for ``prop=imageinfo``.

        Args:
            image: Source image page (provides ``title``).
            params: Clean-named imageinfo parameters.

        Returns:
            Params dict ready for dispatch.
        """
        api_params: dict[str, Any] = {
            "action": "query",
            "prop": "imageinfo",
            "titles": image.title,
        }
        api_params.update(params.to_api())
        return api_params

    def _build_imageinfo_for_image(
        self,
        extract: dict[str, Any],
        image: "BaseWikipediaPage[Any]",
        params: ImageInfoParams,
    ) -> list[ImageInfo]:
        """Parse imageinfo from a single page API response entry.

        Builds a list of :class:`ImageInfo` objects from
        ``extract["imageinfo"]`` and stores it in the image's per-param
        cache.  Also copies the ``known`` key from *extract* into
        ``image._attributes`` so that :meth:`~WikipediaImage.exists` can
        detect Commons-hosted files.

        Args:
            extract: Single page entry from ``raw["query"]["pages"]``.
            image: Image page object to populate in-place.
            params: The parameters used for this fetch (for cache key).

        Returns:
            List of :class:`ImageInfo` objects (may be empty).
        """
        self._common_attributes(extract, image)
        if "known" in extract:
            image._attributes["known"] = extract["known"]
        infos: list[ImageInfo] = []
        for raw_ii in extract.get("imageinfo", []):
            infos.append(
                ImageInfo(
                    timestamp=raw_ii.get("timestamp"),
                    user=raw_ii.get("user"),
                    url=raw_ii.get("url"),
                    descriptionurl=raw_ii.get("descriptionurl"),
                    descriptionshorturl=raw_ii.get("descriptionshorturl"),
                    width=raw_ii.get("width"),
                    height=raw_ii.get("height"),
                    size=raw_ii.get("size"),
                    mime=raw_ii.get("mime"),
                    mediatype=raw_ii.get("mediatype"),
                    sha1=raw_ii.get("sha1"),
                )
            )
        image._set_cached("imageinfo", params.cache_key(), infos)
        return infos

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
    ) -> "ImagesDict":
        """Parse images from a single page API response entry.

        Builds an :class:`ImagesDict` of stub :class:`WikipediaImage` objects
        from ``extract["images"]`` and stores it in the page's per-param cache.

        Args:
            extract: Single page entry from ``raw["query"]["pages"]``.
            page: Page object to populate in-place.
            params: The parameters used for this fetch (for cache key).

        Returns:
            :class:`ImagesDict` keyed by image title.
        """
        from .._pages_dict import ImagesDict  # lazy import to avoid circular dependency

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
        return result

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
        return result

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
        return result

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
