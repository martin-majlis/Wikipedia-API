from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .wikipedia import Wikipedia

from .namespace import Namespace
from .namespace import namespace2int
from .namespace import WikiNamespace
from .wikipedia_page_section import WikipediaPageSection

PagesDict = dict[str, "WikipediaPage"]


class WikipediaPage:
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

    ATTRIBUTES_MAPPING = {
        "language": [],
        "variant": [],
        "pageid": ["info", "extracts", "langlinks"],
        "ns": ["info", "extracts", "langlinks"],
        "title": ["info", "extracts", "langlinks"],
        "contentmodel": ["info"],
        "pagelanguage": ["info"],
        "pagelanguagehtmlcode": ["info"],
        "pagelanguagedir": ["info"],
        "touched": ["info"],
        "lastrevid": ["info"],
        "length": ["info"],
        "protection": ["info"],
        "restrictiontypes": ["info"],
        "watchers": ["info"],
        "visitingwatchers": ["info"],
        "notificationtimestamp": ["info"],
        "talkid": ["info"],
        "fullurl": ["info"],
        "editurl": ["info"],
        "canonicalurl": ["info"],
        "readable": ["info"],
        "preload": ["info"],
        "displaytitle": ["info"],
        "varianttitles": ["info"],
    }

    def __init__(
        self,
        wiki: "Wikipedia",
        title: str,
        ns: WikiNamespace = Namespace.MAIN,
        language: str = "en",
        variant: str | None = None,
        url: str | None = None,
    ) -> None:
        """
        Initialise a lazy Wikipedia page stub.

        No network call is made here.  All cache attributes are
        initialised to empty values; they are populated by the first
        access to the corresponding property.

        :param wiki: the :class:`~wikipediaapi.Wikipedia` client used to
            fetch data when properties are accessed
        :param title: page title exactly as passed by the caller
        :param ns: namespace; stored as an integer via
            :func:`~wikipediaapi.namespace2int`
        :param language: two-letter Wikipedia language code
        :param variant: language variant for automatic conversion, or
            ``None`` to disable
        :param url: pre-set ``fullurl`` attribute; used when the page
            stub is created from a lang-link response
        """
        self.wiki = wiki
        self._summary = ""  # type: str
        self._section = []  # type: list[WikipediaPageSection]
        self._section_mapping = {}  # type: dict[str, list[WikipediaPageSection]]
        self._langlinks = {}  # type: PagesDict
        self._links = {}  # type: PagesDict
        self._backlinks = {}  # type: PagesDict
        self._categories = {}  # type: PagesDict
        self._categorymembers = {}  # type: PagesDict

        self._called = {
            "extracts": False,
            "info": False,
            "langlinks": False,
            "links": False,
            "backlinks": False,
            "categories": False,
            "categorymembers": False,
        }

        self._attributes: dict[str, Any] = {
            "title": title,
            "ns": namespace2int(ns),
            "language": language,
            "variant": variant,
        }

        if url is not None:
            self._attributes["fullurl"] = url

    def __getattr__(self, name: str) -> Any:
        """
        Resolve a lazily-fetched attribute by name.

        Three distinct cases mirror the async counterpart:

        * **No-fetch attributes** (``language``, ``variant``) — returned
          directly from the init-time cache; no network call is ever made.
        * **Info-only attributes** (e.g. ``fullurl``, ``displaytitle``) —
          the ``info`` API call is issued on the first access and the result
          is cached for all subsequent reads.
        * **Multi-source attributes** (e.g. ``pageid``) — fetched via the
          first listed source in :attr:`ATTRIBUTES_MAPPING` if not already
          cached.

        For attributes not present in :attr:`ATTRIBUTES_MAPPING` the normal
        ``__getattribute__`` path is used (raising ``AttributeError`` for
        truly absent names).

        :param name: attribute name to resolve
        :return: the attribute value, fetching if necessary
        """
        if name not in self.ATTRIBUTES_MAPPING:
            return self.__getattribute__(name)

        calls = self.ATTRIBUTES_MAPPING[name]

        if not calls:
            # language, variant — set at init, no fetch needed
            return self._attributes.get(name)

        if name in self._attributes:
            return self._attributes[name]

        if calls == ["info"]:
            if not self._called["info"]:
                self._fetch("info")
            return self._attributes.get(name)

        # multi-source attributes: fetch via first listed source if not yet cached
        if not self._called[calls[0]]:
            self._fetch(calls[0])
        return self._attributes.get(name)

    @property
    def language(self) -> str:
        """
        Two-letter Wikipedia language code for this page.

        Set at construction time and never changed.

        :return: language code string (e.g. ``"en"``, ``"de"``)
        """
        return str(self._attributes["language"])

    @property
    def variant(self) -> str | None:
        """
        Language variant used for automatic text conversion, or ``None``.

        When set, the MediaWiki API converts the page content to the
        specified variant (e.g. ``"zh-tw"`` for Traditional Chinese).

        :return: variant string, or ``None`` if no conversion is applied
        """
        v = self._attributes["variant"]
        return str(v) if v else None

    @property
    def title(self) -> str:
        """
        Title of this page as supplied to :meth:`~wikipediaapi.Wikipedia.page`.

        :return: page title string
        """
        return str(self._attributes["title"])

    @property
    def namespace(self) -> int:
        """
        Integer namespace number of this page.

        ``0`` for main-namespace articles; see :class:`~wikipediaapi.Namespace`
        for the full list of namespace values.

        :return: namespace as an integer
        """
        return int(self._attributes["ns"])

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

    def section_by_title(
        self,
        title: str,
    ) -> WikipediaPageSection | None:
        """
        Return the last section on this page whose heading matches *title*.

        Triggers an ``extracts`` call on first access if needed.
        When several sections share the same heading (e.g. multiple
        "January" sections in a year page) the last one is returned.

        :param title: exact heading text to look up
        :return: the matching :class:`WikipediaPageSection`, or ``None``
            if no section with that title exists
        """
        if not self._called["extracts"]:
            self._fetch("extracts")
        sections = self._section_mapping.get(title)
        if sections:
            return sections[-1]
        return None

    def sections_by_title(
        self,
        title: str,
    ) -> list[WikipediaPageSection]:
        """
        Return all sections on this page whose heading matches *title*.

        Useful for year-type pages where multiple sections share the
        same heading (e.g. ``"January"``).
        Triggers an ``extracts`` call on first access if needed.

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
