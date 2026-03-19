"""Asynchronous Wikipedia page representation.

This module defines the AsyncWikipediaPage class which represents a single
Wikipedia page in an asynchronous context. It provides async methods and
awaitable properties for accessing page content, metadata, and related information.
"""

from typing import Any

from ._base_wikipedia_page import BaseWikipediaPage
from .wikipedia_page_section import WikipediaPageSection

AsyncPagesDict = dict[str, "AsyncWikipediaPage"]


class AsyncWikipediaPage(BaseWikipediaPage["AsyncWikipediaPage"]):
    """
    Lazy representation of a Wikipedia page for use with AsyncWikipedia.

    Mirrors WikipediaPage but exposes all

        Mirrors :class:`~wikipediaapi.WikipediaPage` but exposes all
        data-fetching as awaitables instead of blocking properties.  A page
        stub is created by :meth:`~wikipediaapi.AsyncWikipedia.page` with no
        network call; each awaitable fetches its data on the first ``await``.
        and caches the result for subsequent accesses.

        **Named properties** (always available without a network call):

        :attr language: two-letter language code this page belongs to
        :attr variant: language variant used for auto-conversion, or ``None``
        :attr title: page title as passed to
            :meth:`~wikipediaapi.AsyncWikipedia.page`
        :attr ns: integer namespace number (``0`` = main article)

        **Awaitable data properties** (each triggers a network call on the
        first ``await`` and caches the result):

        * ``await page.summary`` — introductory text
        * ``await page.sections`` — top-level sections
        * ``await page.langlinks`` — ``{lang: AsyncWikipediaPage}`` dict
        * ``await page.links`` — ``{title: AsyncWikipediaPage}`` dict
        * ``await page.backlinks`` — ``{title: AsyncWikipediaPage}`` dict
        * ``await page.categories`` — ``{title: AsyncWikipediaPage}`` dict
        * ``await page.categorymembers`` — ``{title: AsyncWikipediaPage}`` dict

        **Awaitable info attributes** (populated via the ``info`` API call;
        see :attr:`ATTRIBUTES_MAPPING`):

        * ``await page.pageid``, ``await page.fullurl``,
          ``await page.canonicalurl``, ``await page.editurl``,
          ``await page.displaytitle``, ``await page.talkid``,
          ``await page.lastrevid``, ``await page.length``,
          ``await page.touched``, ``await page.contentmodel``,
          ``await page.pagelanguage``, ``await page.pagelanguagehtmlcode``,
          ``await page.pagelanguagedir``, ``await page.protection``,
          ``await page.restrictiontypes``, ``await page.watchers``,
          ``await page.visitingwatchers``,
          ``await page.notificationtimestamp``, ``await page.readable``,
          ``await page.preload``, ``await page.varianttitles``
    """

    async def _info_attr(self, name: str) -> Any:
        """Fetch via the ``info`` API call if not yet cached, then return the value."""
        if name not in self._attributes and not self._called["info"]:
            await self._fetch("info")
        return self._attributes.get(name)

    @property
    def pageid(self) -> Any:
        """Awaitable: MediaWiki numeric page ID (``-1`` for missing pages)."""
        return self._info_attr("pageid")

    @property
    def contentmodel(self) -> Any:
        """Awaitable: content model of the page (e.g. ``"wikitext"``)."""
        return self._info_attr("contentmodel")

    @property
    def pagelanguage(self) -> Any:
        """Awaitable: BCP-47 language code of the page content."""
        return self._info_attr("pagelanguage")

    @property
    def pagelanguagehtmlcode(self) -> Any:
        """Awaitable: HTML ``lang`` attribute value for the page language."""
        return self._info_attr("pagelanguagehtmlcode")

    @property
    def pagelanguagedir(self) -> Any:
        """Awaitable: text directionality of the page language."""
        return self._info_attr("pagelanguagedir")

    @property
    def touched(self) -> Any:
        """Awaitable: ISO 8601 timestamp of the last cache invalidation."""
        return self._info_attr("touched")

    @property
    def lastrevid(self) -> Any:
        """Awaitable: revision ID of the most recent edit."""
        return self._info_attr("lastrevid")

    @property
    def length(self) -> Any:
        """Awaitable: page size in bytes."""
        return self._info_attr("length")

    @property
    def protection(self) -> Any:
        """Awaitable: list of active protection descriptors."""
        return self._info_attr("protection")

    @property
    def restrictiontypes(self) -> Any:
        """Awaitable: list of protection types applicable to this page."""
        return self._info_attr("restrictiontypes")

    @property
    def watchers(self) -> Any:
        """Awaitable: number of users watching this page (may be ``None``)."""
        return self._info_attr("watchers")

    @property
    def visitingwatchers(self) -> Any:
        """Awaitable: watchers who recently visited the page (may be ``None``)."""
        return self._info_attr("visitingwatchers")

    @property
    def notificationtimestamp(self) -> Any:
        """Awaitable: timestamp of the last change that triggered a notification."""
        return self._info_attr("notificationtimestamp")

    @property
    def talkid(self) -> Any:
        """Awaitable: page ID of the associated talk page."""
        return self._info_attr("talkid")

    @property
    def fullurl(self) -> Any:
        """Awaitable: canonical read URL of the page."""
        return self._info_attr("fullurl")

    @property
    def editurl(self) -> Any:
        """Awaitable: URL for editing the page in the browser."""
        return self._info_attr("editurl")

    @property
    def canonicalurl(self) -> Any:
        """Awaitable: canonical URL of the page."""
        return self._info_attr("canonicalurl")

    @property
    def readable(self) -> Any:
        """Awaitable: non-empty string if the page is readable by the current user."""
        return self._info_attr("readable")

    @property
    def preload(self) -> Any:
        """Awaitable: preload template name if set, otherwise ``None``."""
        return self._info_attr("preload")

    @property
    def displaytitle(self) -> Any:
        """Awaitable: formatted display title."""
        return self._info_attr("displaytitle")

    @property
    def varianttitles(self) -> Any:
        """Awaitable: dict mapping variant codes to variant-specific titles."""
        return self._info_attr("varianttitles")

    @property
    def summary(self) -> Any:
        """Awaitable: introductory text of this page (before the first section)."""

        async def _get() -> str:
            if not self._called["extracts"]:
                await self._fetch("extracts")
            return self._summary

        return _get()

    @property
    def langlinks(self) -> Any:
        """Awaitable: ``{language_code: AsyncWikipediaPage}`` dict."""

        async def _get() -> AsyncPagesDict:
            if not self._called["langlinks"]:
                await self._fetch("langlinks")
            return self._langlinks

        return _get()

    @property
    def links(self) -> Any:
        """Awaitable: ``{title: AsyncWikipediaPage}`` dict of outbound links."""

        async def _get() -> AsyncPagesDict:
            if not self._called["links"]:
                await self._fetch("links")
            return self._links

        return _get()

    @property
    def backlinks(self) -> Any:
        """Awaitable: ``{title: AsyncWikipediaPage}`` dict of pages linking here."""

        async def _get() -> AsyncPagesDict:
            if not self._called["backlinks"]:
                await self._fetch("backlinks")
            return self._backlinks

        return _get()

    @property
    def categories(self) -> Any:
        """Awaitable: ``{title: AsyncWikipediaPage}`` dict of categories."""

        async def _get() -> AsyncPagesDict:
            if not self._called["categories"]:
                await self._fetch("categories")
            return self._categories

        return _get()

    @property
    def categorymembers(self) -> Any:
        """Awaitable: ``{title: AsyncWikipediaPage}`` dict of category members."""

        async def _get() -> AsyncPagesDict:
            if not self._called["categorymembers"]:
                await self._fetch("categorymembers")
            return self._categorymembers

        return _get()

    @property
    def text(self) -> Any:
        """Awaitable: full page text — summary followed by all sections."""

        async def _get() -> str:
            txt: str = await self.summary
            if len(txt) > 0:
                txt += "\n\n"
            for sec in await self.sections:
                txt += sec.full_text(level=2)
            return txt.strip()

        return _get()

    @property
    def sections(self) -> Any:
        """Awaitable: top-level sections of this page."""

        async def _get() -> list[WikipediaPageSection]:
            if not self._called["extracts"]:
                await self._fetch("extracts")
            return self._section

        return _get()

    def __getattr__(self, name: str) -> Any:
        """
        Return an awaitable that resolves an API response field.

        Overrides :meth:`BaseWikipediaPage.__getattr__` to preserve the
        async contract of this class: the returned value is a coroutine
        produced by :meth:`_info_attr`, so callers use it the same way as
        any explicit info property::

            value = await page.some_undocumented_field

        This makes undocumented fields returned by the MediaWiki API (i.e.
        keys not listed in :attr:`ATTRIBUTES_MAPPING` and without an
        explicit ``@property``) transparently accessible.

        :param name: attribute name to look up
        :return: coroutine that resolves to the cached value (or ``None``
            if the field was not returned by the API)
        :raises AttributeError: for private names (starting with ``_``)
            or when the page object is not yet fully initialised
        """
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        try:
            object.__getattribute__(self, "_attributes")
        except AttributeError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        return self._info_attr(name)

    async def _fetch(self, call: str) -> "AsyncWikipediaPage":
        """
        Await a named API method on ``self.wiki`` and mark it as called.

        Calls ``await getattr(self.wiki, call)(self)`` which populates
        the corresponding cache attributes in-place, then records the
        call so subsequent accesses skip the network round-trip.

        :param call: name of the API method to invoke (one of
            ``"extracts"``, ``"info"``, ``"langlinks"``, ``"links"``,
            ``"backlinks"``, ``"categories"``, ``"categorymembers"``)
        :return: ``self`` (for optional chaining)
        """
        await getattr(self.wiki, call)(self)
        self._called[call] = True
        return self

    async def exists(self) -> bool:
        """
        Return ``True`` if this page exists on Wikipedia.

        Lazily fetches ``pageid`` via the ``info`` API call on the first
        ``await`` (identical approach to ``await page.fullurl``).  No
        prior data-fetching call is required::

            exists = await page.exists()

        :return: ``True`` if the page has a positive ``pageid``;
            ``False`` otherwise
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        pageid = await self.pageid
        if pageid is None:
            return False
        return int(pageid) > 0

    def __repr__(self) -> str:
        """
        Return a compact human-readable representation of this page.

        Shows title, language, variant, namespace, and page ID (if the
        page has already been fetched; otherwise ``??``).

        :return: string of the form
            ``"<title> (lang: <lang>, variant: <variant>, id: <id>, ns: <ns>)"
        """
        r = f"{self.title} (lang: {self.language}, variant: {self.variant}, "
        if any(self._called.values()):
            r += f"id: {self._attributes.get('pageid')}, "
        else:
            r += "id: ??, "
        r += f"ns: {self.ns})"
        return r
