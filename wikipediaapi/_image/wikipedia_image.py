"""Synchronous Wikipedia image (file) representation.
This module defines the WikipediaImage class which represents a single
file page in a synchronous context.  It is a lighter variant of
WikipediaPage focused on file metadata rather than article text.
"""

from typing import TYPE_CHECKING
from typing import Any

from .._enums import WikiNamespace
from .._page._base_wikipedia_page import NOT_CACHED
from .._page.wikipedia_page_section import WikipediaPageSection
from .._params.imageinfo_params import ImageInfoParams
from .._types import ImageInfo
from ._base_wikipedia_image import BaseWikipediaImage

if TYPE_CHECKING:
    pass


class WikipediaImage(BaseWikipediaImage):
    """Lazy representation of a Wikipedia/Commons file page.
    A ``WikipediaImage`` is created by internal resource methods when
    building image lists.  It requires no network call at construction
    time; accessing ``imageinfo`` (or any convenience property derived
    from it) triggers the minimum API call needed to populate the cache.
    **Named properties** (always available without a network call):
    :attr language: two-letter language code this image belongs to
    :attr variant: language variant used for auto-conversion, or ``None``
    :attr title: file title including the ``File:`` prefix
    :attr ns: integer namespace number (6 for files)
    **Dynamically fetched** (trigger an ``imageinfo`` call on first access):
    * ``imageinfo`` — list of :class:`~wikipediaapi.ImageInfo` objects
    * ``url``, ``descriptionurl``, ``descriptionshorturl`` — URLs
    * ``width``, ``height``, ``size`` — dimensions and file size
    * ``mime``, ``mediatype``, ``sha1``, ``timestamp``, ``user``
    """

    def __init__(
        self,
        wiki: object,
        title: str,
        ns: WikiNamespace = 6,
        language: str = "en",
        variant: str | None = None,
        url: str | None = None,
    ) -> None:
        """Initialise a lazy file-page stub.
        No network call is made here.  All cache attributes are
        initialised to empty values.
        :param wiki: the client (``Wikipedia`` or ``AsyncWikipedia``)
        :param title: file title (e.g. ``"File:Albert Einstein Head.jpg"``)
        :param ns: namespace (defaults to 6 = File)
        :param language: two-letter Wikipedia language code
        :param variant: language variant, or ``None``
        :param url: pre-set ``fullurl``, or ``None``
        """
        super().__init__(wiki=wiki, title=title, ns=ns, language=language, variant=variant, url=url)
        self._called["imageinfo"] = False

    @property
    def sections(self) -> list[WikipediaPageSection]:
        """File pages have no sections; always returns an empty list."""
        return []

    def sections_by_title(self, title: str) -> list[WikipediaPageSection]:
        """File pages have no sections; always returns an empty list."""
        return []

    def exists(self) -> bool:
        """Return ``True`` if this file exists (local or on Commons).
        A file is considered to exist when it has a positive pageid
        *or* when the API returned a ``known=""`` key (indicating the file
        is hosted on Wikimedia Commons).  Triggers an ``imageinfo`` fetch
        on first call if the cache has not yet been populated.
        :return: ``True`` if the file is available, ``False`` otherwise
        """
        if self._called["imageinfo"]:
            return int(self._attributes.get("pageid", -1)) > 0 or "known" in self._attributes
        self._fetch("imageinfo")
        return int(self._attributes.get("pageid", -1)) > 0 or "known" in self._attributes

    @property
    def pageid(self) -> int:
        """MediaWiki numeric page ID (positive for existing images, negative for missing).

        Returns a deterministic page ID based on image title hash
        when image exists either locally (pageid > 0) or on Wikimedia
        Commons (known attribute present). Returns a negative value when
        image does not exist.
        Triggers an ``imageinfo`` fetch on first access if the cache has not yet been populated.

        :return: positive integer if image exists, negative integer otherwise
        """
        if self._called["imageinfo"]:
            return self._get_pageid()
        else:
            self._fetch("imageinfo")
            return self._get_pageid()

    @property
    def imageinfo(self) -> list[ImageInfo]:
        """List of :class:`~wikipediaapi.ImageInfo` objects for this file.
        Triggers an ``imageinfo`` API call on first access using default
        parameters.  Subsequent accesses return the cached value.
        Returns:
            List of :class:`ImageInfo` objects; empty list if the file
            does not exist or has no metadata.
        """
        default_params = ImageInfoParams()
        cached = self._get_cached("imageinfo", default_params.cache_key())
        if isinstance(cached, type(NOT_CACHED)):
            self.wiki.imageinfo(self)  # type: ignore[union-attr]
            cached = self._get_cached("imageinfo", default_params.cache_key())
            if isinstance(cached, type(NOT_CACHED)):
                return []
        return cached  # type: ignore[no-any-return]

    def _first_info(self) -> ImageInfo | None:
        """Return the first ImageInfo entry, or None if list is empty."""
        infos = self.imageinfo
        return infos[0] if infos else None

    @property
    def url(self) -> str | None:
        """Full URL of the file, or ``None`` if unavailable."""
        info = self._first_info()
        return info.url if info else None

    @property
    def descriptionurl(self) -> str | None:
        """URL of the file description page, or ``None`` if unavailable."""
        info = self._first_info()
        return info.descriptionurl if info else None

    @property
    def descriptionshorturl(self) -> str | None:
        """Short URL of the file description page, or ``None`` if unavailable."""
        info = self._first_info()
        return info.descriptionshorturl if info else None

    @property
    def width(self) -> int | None:
        """Image width in pixels, or ``None`` if unavailable."""
        info = self._first_info()
        return info.width if info else None

    @property
    def height(self) -> int | None:
        """Image height in pixels, or ``None`` if unavailable."""
        info = self._first_info()
        return info.height if info else None

    @property
    def size(self) -> int | None:
        """File size in bytes, or ``None`` if unavailable."""
        info = self._first_info()
        return info.size if info else None

    @property
    def mime(self) -> str | None:
        """MIME type of the file (e.g. ``"image/jpeg"``), or ``None``."""
        info = self._first_info()
        return info.mime if info else None

    @property
    def mediatype(self) -> str | None:
        """MediaWiki media type (e.g. ``"BITMAP"``), or ``None``."""
        info = self._first_info()
        return info.mediatype if info else None

    @property
    def sha1(self) -> str | None:
        """SHA-1 hash of the file content, or ``None`` if unavailable."""
        info = self._first_info()
        return info.sha1 if info else None

    @property
    def timestamp(self) -> str | None:
        """ISO 8601 timestamp of this file revision, or ``None``."""
        info = self._first_info()
        return info.timestamp if info else None

    @property
    def user(self) -> str | None:
        """Username of the uploader, or ``None`` if unavailable."""
        info = self._first_info()
        return info.user if info else None

    def __getattr__(self, name: str) -> Any:
        """Return a cached attribute, triggering an ``info`` fetch if needed.
        Overrides :meth:`BaseWikipediaPage.__getattr__` to add lazy fetching:
        if *name* is not yet in ``_attributes`` and the ``info`` call has not
        been made, it is dispatched automatically before re-checking the cache.
        :param name: attribute name to look up
        :return: the cached value
        :raises AttributeError: if *name* is absent even after fetching info
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
        try:
            called = object.__getattribute__(self, "_called")
        except AttributeError as err:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            ) from err
        if not called.get("info", False):
            object.__getattribute__(self, "_fetch")("info")
            if name in attrs:
                return attrs[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def _fetch(self, call: str) -> "WikipediaImage":
        """Invoke a named API method on ``self.wiki`` and mark it as called.
        :param call: name of the API method to invoke (e.g. ``"imageinfo"``)
        :return: ``self`` (for optional chaining)
        """
        getattr(self.wiki, call)(self)
        self._called[call] = True
        return self

    def __repr__(self) -> str:
        """Return a compact human-readable representation of this image.
        Shows title, language, namespace, and page ID (if the image has
        already been fetched; otherwise ``??``).
        :return: string of the form
            ``"<title> (lang: <lang>, id: <id>, ns: <ns>)"``
        """
        r = f"{self.title} (lang: {self.language}, "
        if any(self._called.values()):
            r += f"id: {self._attributes.get('pageid', '??')}, "
        else:
            r += "id: ??, "
        r += f"ns: {self.ns})"
        return r
