"""Asynchronous Wikipedia image (file) representation.

This module defines the AsyncWikipediaImage class which represents a single
file page in an asynchronous context.  It mirrors WikipediaImage but
exposes all data-fetching as awaitables.
"""

from collections.abc import Coroutine
from typing import Any

from .._enums import WikiNamespace
from .._page._base_wikipedia_page import NOT_CACHED
from .._page.wikipedia_page_section import WikipediaPageSection
from .._params.imageinfo_params import ImageInfoParams
from .._types import ImageInfo
from ._base_wikipedia_image import BaseWikipediaImage


class AsyncWikipediaImage(BaseWikipediaImage):
    """Lazy async representation of a Wikipedia/Commons file page.

    Mirrors :class:`~wikipediaapi.WikipediaImage` but exposes all
    data-fetching as awaitables instead of blocking properties.  A file
    stub is created by internal resource methods with no network call;
    each awaitable property fetches its data on the first ``await``.

    **Named properties** (always available without a network call):

    :attr language: two-letter language code this image belongs to
    :attr variant: language variant used for auto-conversion, or ``None``
    :attr title: file title including the ``File:`` prefix
    :attr ns: integer namespace number (6 for files)

    **Awaitable data properties** (trigger an ``imageinfo`` call on first
    ``await``):

    * ``await image.imageinfo`` — list of :class:`~wikipediaapi.ImageInfo`
    * ``await image.url``, ``await image.descriptionurl``, etc.
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
        """Initialise a lazy async file-page stub.

        No network call is made here.  All cache attributes are
        initialised to empty values.

        :param wiki: the client (``AsyncWikipedia``)
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

    async def exists(self) -> bool:
        """Return ``True`` if this file exists (local or on Commons).

        Triggers an ``imageinfo`` fetch on first call if the cache has
        not yet been populated.

        :return: ``True`` if the file is available, ``False`` otherwise
        """
        if not self._called["imageinfo"]:
            await self._fetch("imageinfo")
        return int(self._attributes.get("pageid", -1)) > 0 or "known" in self._attributes

    @property
    def pageid(self) -> Coroutine[Any, Any, int]:
        """Awaitable: MediaWiki numeric page ID (positive for existing, negative for missing).

        Returns a deterministic page ID based on image title hash
        when image exists either locally (pageid > 0) or on Wikimedia
        Commons (known attribute present). Returns a negative value when
        image does not exist.
        Triggers an ``imageinfo`` fetch on first access if the cache has not yet been populated.

        :return: coroutine resolving to positive integer if image exists, negative integer otherwise
        """

        async def _get() -> int:
            if not self._called["imageinfo"]:
                await self._fetch("imageinfo")
            return self._get_pageid()

        return _get()

    @property
    def imageinfo(self) -> Coroutine[Any, Any, list[ImageInfo]]:
        """Awaitable: list of :class:`~wikipediaapi.ImageInfo` objects.

        Triggers an ``imageinfo`` API call on first access using default
        parameters.  Subsequent accesses return the cached value.

        Returns:
            Coroutine resolving to a list of :class:`ImageInfo` objects.
        """

        async def _get() -> list[ImageInfo]:
            default_params = ImageInfoParams()
            cached = self._get_cached("imageinfo", default_params.cache_key())
            if isinstance(cached, type(NOT_CACHED)):
                await self.wiki.imageinfo(self)  # type: ignore[union-attr]
                cached = self._get_cached("imageinfo", default_params.cache_key())
                if isinstance(cached, type(NOT_CACHED)):
                    return []
            return cached  # type: ignore[no-any-return]

        return _get()

    @property
    def url(self) -> Coroutine[Any, Any, str | None]:
        """Awaitable: full URL of the file, or ``None`` if unavailable."""

        async def _get() -> str | None:
            infos: list[ImageInfo] = await self.imageinfo
            return infos[0].url if infos else None

        return _get()

    @property
    def descriptionurl(self) -> Coroutine[Any, Any, str | None]:
        """Awaitable: URL of the file description page, or ``None``."""

        async def _get() -> str | None:
            infos: list[ImageInfo] = await self.imageinfo
            return infos[0].descriptionurl if infos else None

        return _get()

    @property
    def descriptionshorturl(self) -> Coroutine[Any, Any, str | None]:
        """Awaitable: short URL of the file description page, or ``None``."""

        async def _get() -> str | None:
            infos: list[ImageInfo] = await self.imageinfo
            return infos[0].descriptionshorturl if infos else None

        return _get()

    @property
    def width(self) -> Coroutine[Any, Any, int | None]:
        """Awaitable: image width in pixels, or ``None``."""

        async def _get() -> int | None:
            infos: list[ImageInfo] = await self.imageinfo
            return infos[0].width if infos else None

        return _get()

    @property
    def height(self) -> Coroutine[Any, Any, int | None]:
        """Awaitable: image height in pixels, or ``None``."""

        async def _get() -> int | None:
            infos: list[ImageInfo] = await self.imageinfo
            return infos[0].height if infos else None

        return _get()

    @property
    def size(self) -> Coroutine[Any, Any, int | None]:
        """Awaitable: file size in bytes, or ``None``."""

        async def _get() -> int | None:
            infos: list[ImageInfo] = await self.imageinfo
            return infos[0].size if infos else None

        return _get()

    @property
    def mime(self) -> Coroutine[Any, Any, str | None]:
        """Awaitable: MIME type of the file, or ``None``."""

        async def _get() -> str | None:
            infos: list[ImageInfo] = await self.imageinfo
            return infos[0].mime if infos else None

        return _get()

    @property
    def mediatype(self) -> Coroutine[Any, Any, str | None]:
        """Awaitable: MediaWiki media type, or ``None``."""

        async def _get() -> str | None:
            infos: list[ImageInfo] = await self.imageinfo
            return infos[0].mediatype if infos else None

        return _get()

    @property
    def sha1(self) -> Coroutine[Any, Any, str | None]:
        """Awaitable: SHA-1 hash of the file content, or ``None``."""

        async def _get() -> str | None:
            infos: list[ImageInfo] = await self.imageinfo
            return infos[0].sha1 if infos else None

        return _get()

    @property
    def timestamp(self) -> Coroutine[Any, Any, str | None]:
        """Awaitable: ISO 8601 timestamp of this file revision, or ``None``."""

        async def _get() -> str | None:
            infos: list[ImageInfo] = await self.imageinfo
            return infos[0].timestamp if infos else None

        return _get()

    @property
    def user(self) -> Coroutine[Any, Any, str | None]:
        """Awaitable: username of the uploader, or ``None``."""

        async def _get() -> str | None:
            infos: list[ImageInfo] = await self.imageinfo
            return infos[0].user if infos else None

        return _get()

    def __getattr__(self, name: str) -> Any:
        """Return an awaitable that resolves to a cached ``info`` attribute.

        Overrides :meth:`BaseWikipediaPage.__getattr__` so that accessing an
        undocumented API field (e.g. ``fullurl``) on an async image returns an
        awaitable coroutine that fetches ``info`` on demand and then returns
        the value from the cache.

        :param name: attribute name to look up
        :return: coroutine resolving to the cached value
        :raises AttributeError: immediately for private names (``_``-prefixed)
        """
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        async def _get_attr() -> Any:
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
                await object.__getattribute__(self, "_fetch")("info")
                if name in attrs:
                    return attrs[name]
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        return _get_attr()

    async def _fetch(self, call: str) -> "AsyncWikipediaImage":
        """Await a named API method on ``self.wiki`` and mark it as called.

        :param call: name of the API method to invoke (e.g. ``"imageinfo"``)
        :return: ``self`` (for optional chaining)
        """
        await getattr(self.wiki, call)(self)
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
