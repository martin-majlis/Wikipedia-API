from typing import Any

from ._base_wikipedia_page import BaseWikipediaPage
from .wikipedia_page_section import WikipediaPageSection


class AsyncWikipediaPage(BaseWikipediaPage):
    """
    Lazy representation of a Wikipedia page for use with
    :class:`~wikipediaapi.AsyncWikipedia`.

    Mirrors :class:`~wikipediaapi.WikipediaPage` but exposes all
    data-fetching as awaitables instead of blocking properties.  A page
    stub is created by :meth:`~wikipediaapi.AsyncWikipedia.page` with no
    network call; each awaitable fetches its data on the first ``await``
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

    COROUTINE_PROPERTIES: dict[str, tuple[str, str]] = {
        "summary": ("extracts", "_summary"),
        "langlinks": ("langlinks", "_langlinks"),
        "links": ("links", "_links"),
        "backlinks": ("backlinks", "_backlinks"),
        "categories": ("categories", "_categories"),
        "categorymembers": ("categorymembers", "_categorymembers"),
    }

    def __getattr__(self, name: str) -> Any:
        """
        Resolve an attribute, returning an awaitable.

        Three dispatch paths:

        1. **Coroutine properties** (``summary``, ``langlinks``, ``links``,
           ``backlinks``, ``categories``, ``categorymembers``) — return a
           coroutine that fetches via the corresponding API call on the
           first ``await`` and caches the result::

               text = await page.summary
               ll   = await page.langlinks

        2. **Info-only attributes** (e.g. ``fullurl``, ``displaytitle``) —
           return a coroutine that lazily fetches via the ``info`` API call::

               url   = await page.fullurl
               title = await page.displaytitle

        3. **Multi-source attributes** (e.g. ``pageid``) — return a coroutine
           that fetches via the first listed source in
           :attr:`ATTRIBUTES_MAPPING` if not yet cached.

        Attributes not in :attr:`COROUTINE_PROPERTIES` or
        :attr:`ATTRIBUTES_MAPPING` follow the normal ``__getattribute__``
        path (raising ``AttributeError`` if truly absent).

        :param name: attribute name to look up
        :return: coroutine for all data-fetching attributes; result of
            ``__getattribute__`` for unknown names
        """
        if name in self.COROUTINE_PROPERTIES:
            call, cache_attr = self.COROUTINE_PROPERTIES[name]

            async def _coroutine_property() -> Any:
                if not self._called[call]:
                    await self._fetch(call)
                return object.__getattribute__(self, cache_attr)

            return _coroutine_property()

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
