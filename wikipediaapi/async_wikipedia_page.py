from typing import Any

from ._base_wikipedia_page import BaseWikipediaPage
from .wikipedia_page import PagesDict
from .wikipedia_page_section import WikipediaPageSection


class AsyncWikipediaPage(BaseWikipediaPage):
    """
    Lazy representation of a Wikipedia page for use with
    :class:`~wikipediaapi.AsyncWikipedia`.

    Mirrors :class:`~wikipediaapi.WikipediaPage` but exposes data-fetching
    as coroutines instead of blocking properties.  A page stub is created
    by :meth:`~wikipediaapi.AsyncWikipedia.page` with no network call;
    each coroutine method fetches its data on the first ``await`` and
    caches the result for subsequent calls.

    **Named properties** (always available without a network call):

    :attr language: two-letter language code this page belongs to
    :attr variant: language variant used for auto-conversion, or ``None``
    :attr title: page title as passed to
        :meth:`~wikipediaapi.AsyncWikipedia.page`
    :attr ns: integer namespace number (``0`` = main article)

    **Dynamically resolved attributes** (populated after the first
    ``await`` of a data-fetching coroutine; see
    :attr:`ATTRIBUTES_MAPPING`):

    * ``pageid`` — MediaWiki page ID (positive int; ``-1`` = missing)
    * ``fullurl`` — canonical read URL of the page
    * ``canonicalurl`` — canonical URL
    * ``editurl`` — URL for editing the page
    * ``displaytitle`` — formatted display title
    * ``talkid`` — ID of the associated talk page
    * ``lastrevid``, ``length``, ``touched``, ``contentmodel``,
      ``pagelanguage``, ``pagelanguagehtmlcode``, ``pagelanguagedir``,
      ``protection``, ``restrictiontypes``, ``watchers``,
      ``visitingwatchers``, ``notificationtimestamp``, ``readable``,
      ``preload``, ``varianttitles``
    """

    def __getattr__(self, name: str) -> Any:
        """
        Resolve an attribute, returning an awaitable for info-only attributes.

        Attributes whose sole data source is the ``info`` API call (e.g.
        ``fullurl``, ``canonicalurl``, ``displaytitle``) return a
        coroutine that lazily fetches the data on the first ``await`` and
        caches the result for subsequent calls::

            url = await page.fullurl
            title = await page.displaytitle

        Attributes available from multiple sources (``pageid``) are
        returned directly from the cache after the relevant coroutine
        (e.g. :meth:`summary`) has been awaited — they do **not** return
        a coroutine.

        Attributes not present in :attr:`ATTRIBUTES_MAPPING` follow the
        normal ``__getattribute__`` path (raising ``AttributeError`` if
        truly absent).

        :param name: attribute name to look up
        :return: coroutine for info-only attributes; plain cached value
            (or ``None``) for multi-source attributes; result of
            ``__getattribute__`` for unknown names
        """
        if name not in self.ATTRIBUTES_MAPPING:
            return self.__getattribute__(name)

        calls = self.ATTRIBUTES_MAPPING[name]

        if not calls:
            # language, variant — set at init, no fetch needed
            return self._attributes.get(name)

        if calls == ["info"]:
            # Return a coroutine so callers can do: value = await page.fullurl
            async def _info_attr() -> Any:
                if name not in self._attributes and not self._called["info"]:
                    await self._fetch("info")
                return self._attributes.get(name)

            return _info_attr()

        # pageid and other multi-source attributes — return awaitable that
        # lazily fetches via the first listed source if not yet cached
        async def _multi_source_attr() -> Any:
            if name not in self._attributes:
                await self._fetch(calls[0])
            return self._attributes.get(name)

        return _multi_source_attr()

    @property
    def sections(self) -> list[WikipediaPageSection]:
        """
        Top-level sections of this page (populated after ``await page.summary()``).

        Unlike the sync counterpart, this property does **not** trigger a
        network call.  It returns whatever is cached; call and await
        :meth:`summary` first to ensure the sections are populated.

        :return: list of top-level :class:`WikipediaPageSection` objects
        """
        return self._section

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

    async def summary(self) -> str:
        """
        Return the introductory text of this page.

        Triggers an ``extracts`` API call on the first ``await``;
        subsequent calls return the cached value.  Returns an empty
        string for pages that do not exist.

        :return: plain-text or HTML summary string depending on
            ``wiki.extract_format``
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        if not self._called["extracts"]:
            await self._fetch("extracts")
        return self._summary

    async def langlinks(self) -> PagesDict:
        """
        Return a map of language codes to corresponding pages in other Wikipedias.

        Keys are two-letter language codes (e.g. ``"de"``, ``"fr"``),
        values are stub :class:`AsyncWikipediaPage` objects.  Triggers a
        ``langlinks`` API call on the first ``await``.

        :return: ``{language_code: AsyncWikipediaPage}`` dict
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        if not self._called["langlinks"]:
            await self._fetch("langlinks")
        return self._langlinks

    async def links(self) -> PagesDict:
        """
        Return a map of page titles to stub pages linked from this page.

        All outbound wiki links are fetched with automatic pagination.
        Triggers a ``links`` API call on the first ``await``.

        :return: ``{title: AsyncWikipediaPage}`` dict
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        if not self._called["links"]:
            await self._fetch("links")
        return self._links

    async def backlinks(self) -> PagesDict:
        """
        Return a map of page titles to stub pages that link *to* this page.

        Fetched with automatic pagination.  Triggers a ``backlinks`` API
        call on the first ``await``.

        :return: ``{title: AsyncWikipediaPage}`` dict
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        if not self._called["backlinks"]:
            await self._fetch("backlinks")
        return self._backlinks

    async def categories(self) -> PagesDict:
        """
        Return a map of category titles to stub category pages for this page.

        Keys include the ``Category:`` prefix.  Triggers a ``categories``
        API call on the first ``await``.

        :return: ``{title: AsyncWikipediaPage}`` dict
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        if not self._called["categories"]:
            await self._fetch("categories")
        return self._categories

    async def categorymembers(self) -> PagesDict:
        """
        Return a map of page titles to stub pages belonging to this category.

        Only meaningful when ``self.ns == Namespace.CATEGORY``.
        Fetched with automatic pagination.  Triggers a ``categorymembers``
        API call on the first ``await``.

        :return: ``{title: AsyncWikipediaPage}`` dict
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        if not self._called["categorymembers"]:
            await self._fetch("categorymembers")
        return self._categorymembers

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
        Return a human-readable representation of this async page.

        :return: multi-line string showing title, namespace, language,
            and variant
        """
        return "AsyncWikipediaPage: {}\nNS: {}\nLanguage: {}\nVariant: {}".format(
            self.title,
            self.ns,
            self.language,
            self.variant,
        )
