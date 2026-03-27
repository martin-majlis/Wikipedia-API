"""Asynchronous Wikipedia image representation.

This module defines the AsyncWikipediaImage class which represents a single
Wikipedia image file in an asynchronous context. It provides async methods and
awaitable properties for accessing image metadata and information.
"""

from typing import Any

from ._base_wikipedia_image import BaseWikipediaImage


class AsyncWikipediaImage(BaseWikipediaImage["AsyncWikipediaImage"]):
    """
    Lazy representation of a Wikipedia image file for use with AsyncWikipedia.

    Mirrors :class:`~wikipediaapi.WikipediaImage` but exposes all
    data-fetching as awaitables instead of blocking properties.  An image
    stub is created with no network call; each awaitable fetches its data
    on the first ``await`` and caches the result for subsequent accesses.

    **Named properties** (always available without a network call):

    :attr language: two-letter language code this image belongs to
    :attr variant: language variant used for auto-conversion, or ``None``
    :attr title: image title as passed to the constructor
    :attr ns: integer namespace number (``6`` = file namespace)

    **Awaitable data properties** (each triggers a network call on the
    first ``await`` and caches the result):

    * ``await image.timestamp`` — Upload timestamp of the file version
    * ``await image.user`` — Username of the uploader
    * ``await image.userid`` — User ID of the uploader
    * ``await image.comment`` — Upload comment
    * ``await image.parsedcomment`` — Parsed upload comment
    * ``await image.canonicaltitle`` — Canonical title of the file
    * ``await image.url`` — Direct URL to the file
    * ``await image.size`` — File size in bytes
    * ``await image.width`` — Image width in pixels
    * ``await image.height`` — Image height in pixels
    * ``await image.pagecount`` — Number of pages (for PDF/multi-page files)
    * ``await image.sha1`` — SHA-1 hash of the file
    * ``await image.mime`` — MIME type of the file
    * ``await image.thumbmime`` — MIME type of thumbnail (if requested)
    * ``await image.mediatype`` — Media type (BITMAP, DRAWING, AUDIO, VIDEO, etc.)
    * ``await image.metadata`` — Exif metadata dictionary
    * ``await image.commonmetadata`` — Common metadata dictionary
    * ``await image.extmetadata`` — Extended metadata dictionary

    All awaitable properties return coroutines that perform the actual
    API call when awaited.
    """

    def _fetch_imageinfo(self, props: tuple[str, ...]) -> Any:
        """Fetch imageinfo data from API asynchronously.

        This method returns a coroutine that must be awaited.

        Args:
            props: Tuple of property names to fetch.

        Returns:
            Coroutine that resolves to raw API response data for the imageinfo call.

        Raises:
            WikiHttpTimeoutError: If the request times out.
            WikiConnectionError: If a connection cannot be established.
            WikiRateLimitError: If the API returns HTTP 429.
            WikiHttpError: If the API returns a non-success HTTP status.
            WikiInvalidJsonError: If the response is not valid JSON.
        """
        return self._wiki.imageinfo(self, props=props)

    @property
    def timestamp(self) -> Any:
        """Awaitable: upload timestamp of the file version.

        Triggers an ``imageinfo`` API call on first access using default
        properties.  Subsequent accesses return the cached value.

        Returns:
            Coroutine that resolves to ISO 8601 timestamp string, or None if not available.
        """

        async def _get() -> str | None:
            cached = self._get_attribute("timestamp")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("timestamp",))
            if result and len(result) > 0:
                timestamp = result[0].get("timestamp")  # type: ignore[no-any-return]  # type: ignore[no-any-return]
                self._set_attribute("timestamp", timestamp)
                return timestamp  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def user(self) -> Any:
        """Awaitable: username of the uploader.

        Returns:
            Coroutine that resolves to username string, or None if not available.
        """

        async def _get() -> str | None:
            cached = self._get_attribute("user")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("user",))
            if result and len(result) > 0:
                user = result[0].get("user")  # type: ignore[no-any-return]
                self._set_attribute("user", user)
                return user  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def userid(self) -> Any:
        """Awaitable: user ID of the uploader.

        Returns:
            Coroutine that resolves to user ID as integer, or None if not available.
        """

        async def _get() -> int | None:
            cached = self._get_attribute("userid")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("userid",))
            if result and len(result) > 0:
                userid = result[0].get("userid")  # type: ignore[no-any-return]
                if userid is not None:
                    userid = int(userid)
                self._set_attribute("userid", userid)
                return userid  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def comment(self) -> Any:
        """Awaitable: upload comment.

        Returns:
            Coroutine that resolves to comment string, or None if not available.
        """

        async def _get() -> str | None:
            cached = self._get_attribute("comment")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("comment",))
            if result and len(result) > 0:
                comment = result[0].get("comment")  # type: ignore[no-any-return]
                self._set_attribute("comment", comment)
                return comment  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def parsedcomment(self) -> Any:
        """Awaitable: parsed upload comment.

        Returns:
            Coroutine that resolves to parsed comment string, or None if not available.
        """

        async def _get() -> str | None:
            cached = self._get_attribute("parsedcomment")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("parsedcomment",))
            if result and len(result) > 0:
                parsedcomment = result[0].get("parsedcomment")  # type: ignore[no-any-return]
                self._set_attribute("parsedcomment", parsedcomment)
                return parsedcomment  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def canonicaltitle(self) -> Any:
        """Awaitable: canonical title of the file.

        Returns:
            Coroutine that resolves to canonical title string, or None if not available.
        """

        async def _get() -> str | None:
            cached = self._get_attribute("canonicaltitle")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("canonicaltitle",))
            if result and len(result) > 0:
                canonicaltitle = result[0].get("canonicaltitle")  # type: ignore[no-any-return]
                self._set_attribute("canonicaltitle", canonicaltitle)
                return canonicaltitle  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def url(self) -> Any:
        """Awaitable: direct URL to the file.

        Returns:
            Coroutine that resolves to URL string, or None if not available.
        """

        async def _get() -> str | None:
            cached = self._get_attribute("url")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("url",))
            if result and len(result) > 0:
                url = result[0].get("url")  # type: ignore[no-any-return]
                self._set_attribute("url", url)
                return url  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def size(self) -> Any:
        """Awaitable: file size in bytes.

        Returns:
            Coroutine that resolves to file size as integer, or None if not available.
        """

        async def _get() -> int | None:
            cached = self._get_attribute("size")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("size",))
            if result and len(result) > 0:
                size = result[0].get("size")  # type: ignore[no-any-return]
                if size is not None:
                    size = int(size)
                self._set_attribute("size", size)
                return size  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def width(self) -> Any:
        """Awaitable: image width in pixels.

        Returns:
            Coroutine that resolves to width as integer, or None if not available.
        """

        async def _get() -> int | None:
            cached = self._get_attribute("width")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("size",))
            if result and len(result) > 0:
                width = result[0].get("width")  # type: ignore[no-any-return]
                if width is not None:
                    width = int(width)
                self._set_attribute("width", width)
                return width  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def height(self) -> Any:
        """Awaitable: image height in pixels.

        Returns:
            Coroutine that resolves to height as integer, or None if not available.
        """

        async def _get() -> int | None:
            cached = self._get_attribute("height")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("size",))
            if result and len(result) > 0:
                height = result[0].get("height")  # type: ignore[no-any-return]
                if height is not None:
                    height = int(height)
                self._set_attribute("height", height)
                return height  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def pagecount(self) -> Any:
        """Awaitable: number of pages (for PDF/multi-page files).

        Returns:
            Coroutine that resolves to page count as integer, or None if not available.
        """

        async def _get() -> int | None:
            cached = self._get_attribute("pagecount")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("size",))
            if result and len(result) > 0:
                pagecount = result[0].get("pagecount")  # type: ignore[no-any-return]
                if pagecount is not None:
                    pagecount = int(pagecount)
                self._set_attribute("pagecount", pagecount)
                return pagecount  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def sha1(self) -> Any:
        """Awaitable: SHA-1 hash of the file.

        Returns:
            Coroutine that resolves to SHA-1 hash string, or None if not available.
        """

        async def _get() -> str | None:
            cached = self._get_attribute("sha1")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("sha1",))
            if result and len(result) > 0:
                sha1 = result[0].get("sha1")  # type: ignore[no-any-return]
                self._set_attribute("sha1", sha1)
                return sha1  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def mime(self) -> Any:
        """Awaitable: MIME type of the file.

        Returns:
            Coroutine that resolves to MIME type string, or None if not available.
        """

        async def _get() -> str | None:
            cached = self._get_attribute("mime")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("mime",))
            if result and len(result) > 0:
                mime = result[0].get("mime")  # type: ignore[no-any-return]
                self._set_attribute("mime", mime)
                return mime  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def thumbmime(self) -> Any:
        """Awaitable: MIME type of thumbnail (if requested).

        Returns:
            Coroutine that resolves to thumbnail MIME type string, or None if not available.
        """

        async def _get() -> str | None:
            cached = self._get_attribute("thumbmime")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("thumbmime",))
            if result and len(result) > 0:
                thumbmime = result[0].get("thumbmime")  # type: ignore[no-any-return]
                self._set_attribute("thumbmime", thumbmime)
                return thumbmime  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def mediatype(self) -> Any:
        """Awaitable: media type of the file.

        Returns:
            Coroutine that resolves to media type string (BITMAP, DRAWING, AUDIO, VIDEO, etc.), or None if not available.
        """

        async def _get() -> str | None:
            cached = self._get_attribute("mediatype")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("mediatype",))
            if result and len(result) > 0:
                mediatype = result[0].get("mediatype")  # type: ignore[no-any-return]
                self._set_attribute("mediatype", mediatype)
                return mediatype  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def metadata(self) -> Any:
        """Awaitable: Exif metadata dictionary.

        Returns:
            Coroutine that resolves to Exif metadata dictionary, or None if not available.
        """

        async def _get() -> dict[str, Any] | None:
            cached = self._get_attribute("metadata")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("metadata",))
            if result and len(result) > 0:
                metadata = result[0].get("metadata")  # type: ignore[no-any-return]
                self._set_attribute("metadata", metadata)
                return metadata  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def commonmetadata(self) -> Any:
        """Awaitable: common metadata dictionary.

        Returns:
            Coroutine that resolves to common metadata dictionary, or None if not available.
        """

        async def _get() -> dict[str, Any] | None:
            cached = self._get_attribute("commonmetadata")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("commonmetadata",))
            if result and len(result) > 0:
                commonmetadata = result[0].get("commonmetadata")  # type: ignore[no-any-return]
                self._set_attribute("commonmetadata", commonmetadata)
                return commonmetadata  # type: ignore[no-any-return]
            return None

        return _get()

    @property
    def extmetadata(self) -> Any:
        """Awaitable: extended metadata dictionary.

        Returns:
            Coroutine that resolves to extended metadata dictionary, or None if not available.
        """

        async def _get() -> dict[str, Any] | None:
            cached = self._get_attribute("extmetadata")
            if cached is not None:
                return cached  # type: ignore[no-any-return]

            result = await self._fetch_imageinfo(("extmetadata",))
            if result and len(result) > 0:
                extmetadata = result[0].get("extmetadata")  # type: ignore[no-any-return]
                self._set_attribute("extmetadata", extmetadata)
                return extmetadata  # type: ignore[no-any-return]
            return None

        return _get()

    async def exists(self) -> bool:  # type: ignore[override]
        """Check if the image file exists on the server.

        Returns:
            True if the image exists and is accessible, False if the image
            does not exist or cannot be accessed.

        Raises:
            WikiHttpTimeoutError: If the request times out.
            WikiConnectionError: If a connection cannot be established.
            WikiRateLimitError: If the API returns HTTP 429.
            WikiHttpError: If the API returns a non-success HTTP status.
            WikiInvalidJsonError: If the response is not valid JSON.
        """
        # Try to fetch basic imageinfo to check existence
        try:
            result = await self._fetch_imageinfo(("timestamp",))
            return result is not None and len(result) > 0
        except Exception:
            return False
