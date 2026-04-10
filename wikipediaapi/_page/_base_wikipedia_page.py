from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from .._enums import Namespace
from .._enums import WikiNamespace
from .._enums import namespace2int
from .wikipedia_page_section import WikipediaPageSection

PageT = TypeVar("PageT", bound="BaseWikipediaPage[Any]")


class _Sentinel:
    """Singleton sentinel indicating a cache miss (distinct from None)."""

    _instance: "_Sentinel | None" = None

    def __new__(cls) -> "_Sentinel":
        """Return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        """Return a readable representation."""
        return "<NOT_CACHED>"

    def __bool__(self) -> bool:
        """Return False so ``if cached:`` skips sentinels."""
        return False


NOT_CACHED = _Sentinel()


class BaseWikipediaPage(ABC, Generic[PageT]):
    """
    Common base for WikipediaPage and AsyncWikipediaPage.

    Contains all state initialisation and every method or property whose

        Contains all state initialisation and every method or property whose
        behaviour is identical in both the synchronous and asynchronous
        subclasses.

        * :attr:`ATTRIBUTES_MAPPING` — declarative mapping of attribute names
          to the API calls that populate them.
        * :meth:`__init__` — sets up all cache dictionaries to empty values;
          no network call is made.
        * Named properties that return init-time values without any fetch:
          :attr:`language`, :attr:`variant`, :attr:`title`, :attr:`ns`,
          :attr:`namespace`.
        * :meth:`sections_by_title` — reads from the cached section mapping.
          The synchronous subclass overrides this to trigger a fetch when the
          cache is empty; the asynchronous subclass inherits this version and
          requires an explicit ``await page.summary`` before calling it.
        * :meth:`section_by_title` — delegates to :meth:`sections_by_title`
          so both subclasses automatically use the correct (overridden or
          inherited) version.

        Subclass responsibilities:

        * :meth:`_fetch` — ``def`` in sync, ``async def`` in async.
        * ``sections`` — both sync and async auto-fetch via ``extracts`` on first access.
        * ``exists()`` — sync auto-fetches via ``self.pageid``; async is a
          coroutine that lazily fetches ``pageid`` via ``info``.
        * All data-fetching surface (``summary``, ``text``, ``langlinks``, …) —
          explicit ``@property`` in both; async properties return coroutines.
    """

    ATTRIBUTES_MAPPING: dict[str, list[str]] = {
        "language": [],
        "variant": [],
        "ns": [],
        "namespace": [],
        "title": [],
        "pageid": ["info", "extracts", "langlinks"],
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
        "summary": ["extracts"],
        "text": ["extracts"],
        "sections": ["extracts"],
        "coordinates": [],
        "images": [],
        "geosearch_meta": [],
        "search_meta": [],
    }

    def __init__(
        self,
        wiki: Any,
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
        access to the corresponding property or coroutine.

        :param wiki: the client (``Wikipedia`` or ``AsyncWikipedia``)
            used to fetch data on demand
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
        self._summary: str = ""
        self._section: list[WikipediaPageSection] = []
        self._section_mapping: dict[str, list[WikipediaPageSection]] = {}
        self._langlinks: dict[str, PageT] = {}
        self._links: dict[str, PageT] = {}
        self._backlinks: dict[str, PageT] = {}
        self._categories: dict[str, PageT] = {}
        self._categorymembers: dict[str, PageT] = {}

        self._called = {
            "extracts": False,
            "info": False,
            "langlinks": False,
            "links": False,
            "backlinks": False,
            "categories": False,
            "categorymembers": False,
        }

        self._param_cache: dict[str, dict[tuple[tuple[str, Any], ...], Any]] = {}

        self._geosearch_meta: Any = None
        self._search_meta: Any = None

        self._attributes: dict[str, Any] = {
            "title": title,
            "ns": namespace2int(ns),
            "language": language,
            "variant": variant,
        }

        if url is not None:
            self._attributes["fullurl"] = url

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

        Set at construction time.  Non-``None`` only when the client was
        created with a ``variant`` argument (e.g. ``"zh-cn"``).

        :return: variant string or ``None``
        """
        v = self._attributes.get("variant")
        return str(v) if v is not None else None

    @property
    def title(self) -> str:
        """
        Title of this page as supplied to the client ``page()`` call.

        May be updated to the API-normalised form after the first fetch.

        :return: page title string
        """
        return str(self._attributes["title"])

    @property
    def ns(self) -> int:
        """
        Integer namespace number of this page.

        Set at construction time from the ``ns`` argument.

        :return: namespace integer (e.g. ``0`` for main articles,
            ``14`` for categories)
        """
        return int(self._attributes["ns"])

    @property
    def namespace(self) -> int:
        """
        Integer namespace number of this page (alias for :attr:`ns`).

        :return: namespace integer (e.g. ``0`` for main articles,
            ``14`` for categories)
        """
        return int(self._attributes["ns"])

    def __eq__(self, other: object) -> bool:
        """Compare pages by logical identity tuple.

        Two page objects are considered equal when they refer to the same
        language, title, and namespace.

        Args:
            other: Object to compare against.

        Returns:
            ``True`` when ``other`` is a ``BaseWikipediaPage`` with the same
            language, title, and namespace; otherwise ``False``.
        """
        if not isinstance(other, BaseWikipediaPage):
            return False
        return (
            self.language,
            self.title,
            self.ns,
        ) == (
            other.language,
            other.title,
            other.ns,
        )

    def __hash__(self) -> int:
        """Return the hash of the page identity tuple.

        Returns:
            Hash computed from ``(language, title, namespace)``.
        """
        return hash((self.language, self.title, self.ns))

    @property
    @abstractmethod
    def sections(self) -> list[WikipediaPageSection]:
        """
        Top-level sections of this page.

        Must be implemented by each subclass:

        * :class:`~wikipediaapi.WikipediaPage` — auto-fetches via
          ``extracts`` on first access.
        * :class:`~wikipediaapi.AsyncWikipediaPage` — awaitable that
          auto-fetches via ``extracts`` on first access.

        :return: list of top-level :class:`WikipediaPageSection` objects
        """

    @abstractmethod
    def exists(self) -> Any:
        """
        Return whether this page exists on Wikipedia.

        Must be implemented by each subclass:

        * :class:`~wikipediaapi.WikipediaPage` — returns ``bool``
          directly, auto-fetching ``pageid`` if not yet cached.
        * :class:`~wikipediaapi.AsyncWikipediaPage` — returns a
          coroutine (``async def``); awaiting it lazily fetches
          ``pageid`` via the ``info`` API call if not yet cached.

        :return: ``bool`` (sync) or an awaitable ``bool`` (async)
        """

    def __getattribute__(self, name: str) -> Any:
        """
        Intercept attribute access to block __dict__ and other special attributes.

        This method is called for every attribute access, allowing us to
        block access to __dict__ and other special attributes while preserving
        normal attribute lookup behavior.

        :param name: attribute name to look up
        :return: the attribute value
        :raises AttributeError: if accessing blocked special attributes
        """
        if name == "__dict__":
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        return super().__getattribute__(name)

    def __getattr__(self, name: str) -> Any:
        """
        Return a value stored in the API response cache.

        Called only when normal attribute lookup fails (i.e. the name is not
        a regular instance attribute or class-level descriptor).  Reads from
        ``_attributes``, which is populated by API calls such as ``info`` and
        ``extracts``.  This lets callers access documented attributes like
        ``pageid`` and ``fullurl`` as well as any additional fields the
        MediaWiki API may return that are not explicitly listed in
        :attr:`ATTRIBUTES_MAPPING`.

        Raises :exc:`AttributeError` when the name is not present in the
        cache, preserving the standard Python contract.

        :param name: attribute name to look up
        :return: the cached value
        :raises AttributeError: if *name* is not in the API response cache
        """
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        try:
            attrs = object.__getattribute__(self, "_attributes")
        except AttributeError as err:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            ) from err
        if name in attrs:
            return attrs[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def sections_by_title(
        self,
        title: str,
    ) -> list[WikipediaPageSection]:
        """
        Return all sections whose heading matches *title*.

        Reads directly from the cached section mapping without triggering
        any network call.  Ensure sections are populated before calling
        this method:

        * **Sync** — the overriding implementation in
          :class:`~wikipediaapi.WikipediaPage` triggers a fetch
          automatically.
        * **Async** — call ``await page.sections`` first.

        :param title: exact heading text to search for
        :return: list of matching :class:`WikipediaPageSection` objects;
            empty list if no section with that heading exists
        """
        sections = self._section_mapping.get(title)
        if sections is None:
            return []
        return sections

    def section_by_title(
        self,
        title: str,
    ) -> WikipediaPageSection | None:
        """
        Return the last section whose heading matches *title*, or ``None``.

        Delegates to :meth:`sections_by_title` so both subclasses
        automatically benefit from any override (e.g. the auto-fetch
        behaviour in :class:`~wikipediaapi.WikipediaPage`).

        When multiple sections share the same heading the last one is
        returned.

        :param title: exact heading text to search for
        :return: the matching :class:`WikipediaPageSection`, or ``None``
        """
        sections = self.sections_by_title(title)
        if sections:
            return sections[-1]
        return None

    def _get_cached(self, key: str, cache_key: tuple[tuple[str, Any], ...]) -> Any:
        """Return a cached value for *key* and *cache_key*, or :data:`NOT_CACHED`.

        Args:
            key: Top-level cache namespace (e.g. ``"coordinates"``).
            cache_key: Hashable tuple produced by ``params.cache_key()``.

        Returns:
            The cached value, or :data:`NOT_CACHED` if no entry exists.
        """
        bucket = self._param_cache.get(key)
        if bucket is None:
            return NOT_CACHED
        return bucket.get(cache_key, NOT_CACHED)

    def _set_cached(self, key: str, cache_key: tuple[tuple[str, Any], ...], value: Any) -> None:
        """Store *value* in the per-param cache under *key* / *cache_key*.

        Args:
            key: Top-level cache namespace (e.g. ``"coordinates"``).
            cache_key: Hashable tuple produced by ``params.cache_key()``.
            value: The value to cache (may be ``None``).
        """
        if key not in self._param_cache:
            self._param_cache[key] = {}
        self._param_cache[key][cache_key] = value
