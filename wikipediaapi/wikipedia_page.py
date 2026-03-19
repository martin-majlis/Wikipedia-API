"""Synchronous Wikipedia page representation.

This module defines the WikipediaPage class which represents a single
Wikipedia page in a synchronous context. It provides methods and properties
for accessing page content, metadata, and related information.
"""

from typing import Any

from ._base_wikipedia_page import BaseWikipediaPage
from .wikipedia_page_section import WikipediaPageSection

PagesDict = dict[str, "WikipediaPage"]


class WikipediaPage(BaseWikipediaPage["WikipediaPage"]):
    """
    Lazy representation of a Wikipedia page.

    A ``WikipediaPage`` is created by :meth:`~wikipediaapi.Wikipedia.page`
    and requires no network call at construction time.  Data is fetched
    from the MediaWiki API on demand: accessing a property triggers the
    minimum API call needed to populate it, and the result is cached so
    subsequent accesses are free.

    **Named properties** (always available without a network call):

    :attr language: two-letter language code this page belongs to
    :attr variant: language variant used for auto-conversion, or ``None``
    :attr title: page title as passed to :meth:`~wikipediaapi.Wikipedia.page`
    :attr namespace: integer namespace number (``0`` = main article)

    **Dynamically resolved attributes** (fetched lazily via
    :attr:`ATTRIBUTES_MAPPING`; trigger an ``info`` or ``extracts`` call
    on first access):

    * ``pageid`` — MediaWiki page ID (``-1`` for missing pages)
    * ``fullurl`` — canonical read URL of the page
    * ``canonicalurl`` — canonical URL
    * ``editurl`` — URL for editing the page
    * ``displaytitle`` — formatted display title
    * ``talkid`` — ID of the associated talk page
    * ``lastrevid`` — ID of the most recent revision
    * ``length`` — page size in bytes
    * ``touched`` — timestamp of the last cache invalidation
    * ``contentmodel``, ``pagelanguage``, ``pagelanguagehtmlcode``,
      ``pagelanguagedir``, ``protection``, ``restrictiontypes``,
      ``watchers``, ``visitingwatchers``, ``notificationtimestamp``,
      ``readable``, ``preload``, ``varianttitles``
    """

    def _info_attr(self, name: str) -> Any:
        """Return a cached ``info``-sourced attribute, fetching if not yet loaded."""
        if name in self._attributes:
            return self._attributes[name]
        if not self._called["info"]:
            self._fetch("info")
        return self._attributes.get(name)

    @property
    def pageid(self) -> Any:
        """MediaWiki numeric page ID (``-1`` for missing pages)."""
        return self._info_attr("pageid")

    @property
    def contentmodel(self) -> Any:
        """Content model of the page (e.g. ``"wikitext"``)."""
        return self._info_attr("contentmodel")

    @property
    def pagelanguage(self) -> Any:
        """BCP-47 language code of the page content."""
        return self._info_attr("pagelanguage")

    @property
    def pagelanguagehtmlcode(self) -> Any:
        """HTML ``lang`` attribute value for the page language."""
        return self._info_attr("pagelanguagehtmlcode")

    @property
    def pagelanguagedir(self) -> Any:
        """Text directionality of the page language (``"ltr"`` or ``"rtl"``)."""
        return self._info_attr("pagelanguagedir")

    @property
    def touched(self) -> Any:
        """ISO 8601 timestamp of the last cache invalidation."""
        return self._info_attr("touched")

    @property
    def lastrevid(self) -> Any:
        """Revision ID of the most recent edit."""
        return self._info_attr("lastrevid")

    @property
    def length(self) -> Any:
        """Page size in bytes."""
        return self._info_attr("length")

    @property
    def protection(self) -> Any:
        """List of active protection descriptors (type, level, expiry)."""
        return self._info_attr("protection")

    @property
    def restrictiontypes(self) -> Any:
        """List of protection types applicable to this page."""
        return self._info_attr("restrictiontypes")

    @property
    def watchers(self) -> Any:
        """Number of users watching this page (may be ``None``)."""
        return self._info_attr("watchers")

    @property
    def visitingwatchers(self) -> Any:
        """Watchers who recently visited the page (may be ``None``)."""
        return self._info_attr("visitingwatchers")

    @property
    def notificationtimestamp(self) -> Any:
        """Timestamp of the last change that triggered a notification."""
        return self._info_attr("notificationtimestamp")

    @property
    def talkid(self) -> Any:
        """Page ID of the associated talk page."""
        return self._info_attr("talkid")

    @property
    def fullurl(self) -> Any:
        """Canonical read URL of the page."""
        return self._info_attr("fullurl")

    @property
    def editurl(self) -> Any:
        """URL for editing the page in the browser."""
        return self._info_attr("editurl")

    @property
    def canonicalurl(self) -> Any:
        """Canonical URL of the page."""
        return self._info_attr("canonicalurl")

    @property
    def readable(self) -> Any:
        """Non-empty string if the page is readable by the current user."""
        return self._info_attr("readable")

    @property
    def preload(self) -> Any:
        """Preload template name if set, otherwise ``None``."""
        return self._info_attr("preload")

    @property
    def displaytitle(self) -> Any:
        """Return the formatted display title (may differ from :attr:`title` in casing)."""
        return self._info_attr("displaytitle")

    @property
    def varianttitles(self) -> Any:
        """Dict mapping variant codes to variant-specific titles."""
        return self._info_attr("varianttitles")

    def exists(self) -> bool:
        """
        Return ``True`` if this page exists on Wikipedia.

        Triggers an ``info`` API call on first invocation (via
        ``pageid`` attribute resolution) and caches the result.
        A ``pageid`` of ``-1`` indicates a missing page.

        :return: ``True`` if the page exists, ``False`` otherwise
        """
        return bool(self.pageid != -1)

    @property
    def summary(self) -> str:
        """
        Introductory text of this page (the content before the first section).

        Triggers an ``extracts`` API call on first access; subsequent
        accesses return the cached value.  Returns an empty string for
        pages that do not exist.

        :return: plain-text or HTML summary string depending on
            ``wiki.extract_format``
        """
        if not self._called["extracts"]:
            self._fetch("extracts")
        return self._summary

    @property
    def sections(self) -> list[WikipediaPageSection]:
        """
        Top-level sections of this page.

        Each element is a :class:`WikipediaPageSection` that may contain
        its own child sections.  Triggers an ``extracts`` call on first
        access.

        :return: list of top-level :class:`WikipediaPageSection` objects
            (may be empty for pages with no sections)
        """
        if not self._called["extracts"]:
            self._fetch("extracts")
        return self._section

    def sections_by_title(
        self,
        title: str,
    ) -> list[WikipediaPageSection]:
        """
        Return all sections on this page whose heading matches *title*.

        Overrides the base implementation to trigger an ``extracts``
        fetch automatically on first call, so callers need not fetch
        sections explicitly.

        :param title: exact heading text to look up
        :return: list of matching :class:`WikipediaPageSection` objects;
            empty list if no section with that title exists
        """
        if not self._called["extracts"]:
            self._fetch("extracts")
        sections = self._section_mapping.get(title)
        if sections is None:
            return []
        return sections

    @property
    def text(self) -> str:
        """
        Full text of this page: summary followed by all sections.

        Assembles the text by concatenating :attr:`summary` with the
        :meth:`~WikipediaPageSection.full_text` of every top-level
        section.  The result is stripped of leading/trailing whitespace.

        Triggers an ``extracts`` call on first access.

        :return: complete page text as a single string
        """
        txt = self.summary
        if len(txt) > 0:
            txt += "\n\n"
        for sec in self.sections:
            txt += sec.full_text(level=2)
        return txt.strip()

    @property
    def langlinks(self) -> PagesDict:
        """
        Map of language codes to corresponding pages in other Wikipedias.

        Keys are two-letter language codes (e.g. ``"de"``, ``"fr"``),
        values are stub :class:`WikipediaPage` objects with their
        ``language`` and ``fullurl`` pre-set.  Triggers a ``langlinks``
        API call on first access.

        API reference:

        * https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blanglinks
        * https://www.mediawiki.org/wiki/API:Langlinks

        :return: ``{language_code: WikipediaPage}`` dict
        """
        if not self._called["langlinks"]:
            self._fetch("langlinks")
        return self._langlinks

    @property
    def links(self) -> PagesDict:
        """
        Map of page titles to stub pages linked from this page.

        All inter-wiki links are included, with automatic pagination so
        the complete set is always returned.  Triggers a ``links`` API
        call on first access.

        API reference:

        * https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blinks
        * https://www.mediawiki.org/wiki/API:Links

        :return: ``{title: WikipediaPage}`` dict
        """
        if not self._called["links"]:
            self._fetch("links")
        return self._links

    @property
    def backlinks(self) -> PagesDict:
        """
        Map of page titles to stub pages that link *to* this page.

        All backlinks are fetched with automatic pagination.  Triggers a
        ``backlinks`` API call on first access.

        API reference:

        * https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bbacklinks
        * https://www.mediawiki.org/wiki/API:Backlinks

        :return: ``{title: WikipediaPage}`` dict
        """
        if not self._called["backlinks"]:
            self._fetch("backlinks")
        return self._backlinks

    @property
    def categories(self) -> PagesDict:
        """
        Map of category titles to stub category pages for this page.

        Keys include the ``Category:`` prefix.  Triggers a ``categories``
        API call on first access.

        API reference:

        * https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategories
        * https://www.mediawiki.org/wiki/API:Categories

        :return: ``{title: WikipediaPage}`` dict
        """
        if not self._called["categories"]:
            self._fetch("categories")
        return self._categories

    @property
    def categorymembers(self) -> PagesDict:
        """
        Map of page titles to stub pages belonging to this category.

        Only meaningful when ``self.namespace == Namespace.CATEGORY``.
        Fetched with automatic pagination.  Triggers a ``categorymembers``
        API call on first access.

        API reference:

        * https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategorymembers
        * https://www.mediawiki.org/wiki/API:Categorymembers

        :return: ``{title: WikipediaPage}`` dict
        """
        if not self._called["categorymembers"]:
            self._fetch("categorymembers")
        return self._categorymembers

    def __getattr__(self, name: str) -> Any:
        """
        Return a cached API attribute, triggering an ``info`` fetch if needed.

        Overrides :meth:`BaseWikipediaPage.__getattr__` to add lazy fetching:
        if *name* is not yet in ``_attributes`` and the ``info`` call has not
        been made, it is dispatched automatically before re-checking the
        cache.  This means undocumented fields returned by the MediaWiki API
        (i.e. keys not listed in :attr:`ATTRIBUTES_MAPPING`) are accessible
        transparently without any extra call from the caller.

        :param name: attribute name to look up
        :return: the cached value
        :raises AttributeError: if *name* is absent even after fetching info
        """
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        try:
            attrs = object.__getattribute__(self, "_attributes")
        except AttributeError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        if name in attrs:
            return attrs[name]
        try:
            called = object.__getattribute__(self, "_called")
        except AttributeError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        if not called.get("info", False):
            object.__getattribute__(self, "_fetch")("info")
            if name in attrs:
                return attrs[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def _fetch(self, call: str) -> "WikipediaPage":
        """
        Invoke a named API method on ``self.wiki`` and mark it as called.

        Calls ``getattr(self.wiki, call)(self)`` which populates the
        corresponding cache attributes in-place, then records the call so
        subsequent accesses skip the network round-trip.

        :param call: name of the API method to invoke (one of
            ``"extracts"``, ``"info"``, ``"langlinks"``, ``"links"``,
            ``"backlinks"``, ``"categories"``, ``"categorymembers"``)
        :return: ``self`` (for optional chaining)
        """
        getattr(self.wiki, call)(self)
        self._called[call] = True
        return self

    def __repr__(self) -> str:
        """
        Return a compact human-readable representation of this page.

        Shows title, language, variant, namespace, and page ID (if the
        page has already been fetched; otherwise ``??``).

        :return: string of the form
            ``"<title> (lang: <lang>, variant: <variant>, id: <id>, ns: <ns>)"``
        """
        r = f"{self.title} (lang: {self.language}, variant: {self.variant}, "
        if any(self._called.values()):
            r += f"id: {self.pageid}, "
        else:
            r += "id: ??, "

        r += f"ns: {self.ns})"
        return r
