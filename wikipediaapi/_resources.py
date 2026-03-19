from abc import ABC
from collections import defaultdict
from collections.abc import Callable
import re
from typing import Any, TYPE_CHECKING, TypeVar
from urllib import parse

from ._base_wikipedia_page import BaseWikipediaPage
from .extract_format import ExtractFormat
from .namespace import Namespace
from .namespace import WikiNamespace
from .wikipedia_page import PagesDict
from .wikipedia_page import WikipediaPage
from .wikipedia_page_section import WikipediaPageSection

T = TypeVar("T")
_PageP = TypeVar("_PageP", bound=BaseWikipediaPage)


if TYPE_CHECKING:
    from .async_wikipedia_page import AsyncPagesDict
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
        page does not exist; ``pageid`` is set to ``-1`` and *empty* is
        returned.  Otherwise the first real page entry is passed to *builder*.

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
                page._attributes["pageid"] = -1
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
                page._attributes["pageid"] = -1
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
                page._attributes["pageid"] = -1
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
            the page does not exist (``pageid`` is set to ``-1``)
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
        return self._dispatch_prop(
            page, self._langlinks_params(page, **kwargs), {}, self._build_langlinks
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
        return self._dispatch_prop_paginated(
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
        return self._dispatch_list(
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
        return self._dispatch_prop(
            page, self._categories_params(page, **kwargs), {}, self._build_categories
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
        return self._dispatch_list(
            page,
            {**self._categorymembers_params(page), **kwargs},
            "cmcontinue",
            "categorymembers",
            self._build_categorymembers,
        )


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
        return await self._async_dispatch_prop(
            page, self._langlinks_params(page, **kwargs), {}, self._build_langlinks
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
        return await self._async_dispatch_prop_paginated(
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
        return await self._async_dispatch_list(
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
        return await self._async_dispatch_prop(
            page, self._categories_params(page, **kwargs), {}, self._build_categories
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
        return await self._async_dispatch_list(
            page,
            {**self._categorymembers_params(page), **kwargs},
            "cmcontinue",
            "categorymembers",
            self._build_categorymembers,
        )
