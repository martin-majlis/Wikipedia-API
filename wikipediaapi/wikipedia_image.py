"""Synchronous Wikipedia image representation.

This module defines the WikipediaImage class which represents a single
Wikipedia image file in a synchronous context. It provides methods and
properties for accessing image metadata and information.
"""

from typing import Any

from ._base_wikipedia_image import BaseWikipediaImage


class WikipediaImage(BaseWikipediaImage["WikipediaImage"]):
    """
    Lazy representation of a Wikipedia image file.

    A ``WikipediaImage`` is created by image listing methods with no
    network call at construction time.  Data is fetched from the MediaWiki
    API on demand: accessing a property triggers the minimum API call
    needed to populate it, and the result is cached so subsequent accesses
    are free.

    **Named properties** (always available without a network call):

    :attr language: two-letter language code this image belongs to
    :attr variant: language variant used for auto-conversion, or ``None``
    :attr title: image title as passed to the constructor
    :attr ns: integer namespace number (``6`` = file namespace)

    **Dynamically resolved attributes** (fetched lazily via
    :attr:`ATTRIBUTES_MAPPING`; trigger an ``imageinfo`` call
    on first access):

    * ``timestamp`` — Upload timestamp of the file version
    * ``user`` — Username of the uploader
    * ``userid`` — User ID of the uploader
    * ``comment`` — Upload comment
    * ``parsedcomment`` — Parsed upload comment
    * ``canonicaltitle`` — Canonical title of the file
    * ``url`` — Direct URL to the file
    * ``size`` — File size in bytes
    * ``width`` — Image width in pixels
    * ``height`` — Image height in pixels
    * ``pagecount`` — Number of pages (for PDF/multi-page files)
    * ``sha1`` — SHA-1 hash of the file
    * ``mime`` — MIME type of the file
    * ``thumbmime`` — MIME type of thumbnail (if requested)
    * ``mediatype`` — Media type (BITMAP, DRAWING, AUDIO, VIDEO, etc.)
    * ``metadata`` — Exif metadata dictionary
    * ``commonmetadata`` — Common metadata dictionary
    * ``extmetadata`` — Extended metadata dictionary

    All API methods block until the HTTP response is received and parsed.
    """

    def _fetch_imageinfo(self, props: tuple[str, ...]) -> Any:
        """Fetch imageinfo data from API synchronously.

        Args:
            props: Tuple of property names to fetch.

        Returns:
            Raw API response data for the imageinfo call.

        Raises:
            WikiHttpTimeoutError: If the request times out.
            WikiConnectionError: If a connection cannot be established.
            WikiRateLimitError: If the API returns HTTP 429.
            WikiHttpError: If the API returns a non-success HTTP status.
            WikiInvalidJsonError: If the response is not valid JSON.
        """
        return self._wiki.imageinfo(self, props=props)

    @property
    def timestamp(self) -> str | None:
        """Upload timestamp of the file version.

        Triggers an ``imageinfo`` API call on first access using default
        properties.  Subsequent accesses return the cached value.

        Returns:
            ISO 8601 timestamp string, or None if not available.
        """
        cached = self._get_attribute("timestamp")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("timestamp",))
        if result and len(result) > 0:
            timestamp = result[0].get("timestamp")  # type: ignore[no-any-return]
            self._set_attribute("timestamp", timestamp)
            return timestamp  # type: ignore[no-any-return]
        return None

    @property
    def user(self) -> str | None:
        """Username of the uploader.

        Returns:
            Username string, or None if not available.
        """
        cached = self._get_attribute("user")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("user",))
        if result and len(result) > 0:
            user = result[0].get("user")  # type: ignore[no-any-return]
            self._set_attribute("user", user)
            return user  # type: ignore[no-any-return]
        return None

    @property
    def userid(self) -> int | None:
        """User ID of the uploader.

        Returns:
            User ID as integer, or None if not available.
        """
        cached = self._get_attribute("userid")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("userid",))
        if result and len(result) > 0:
            userid = result[0].get("userid")  # type: ignore[no-any-return]
            if userid is not None:
                userid = int(userid)
            self._set_attribute("userid", userid)
            return userid  # type: ignore[no-any-return]
        return None

    @property
    def comment(self) -> str | None:
        """Upload comment.

        Returns:
            Comment string, or None if not available.
        """
        cached = self._get_attribute("comment")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("comment",))
        if result and len(result) > 0:
            comment = result[0].get("comment")  # type: ignore[no-any-return]
            self._set_attribute("comment", comment)
            return comment  # type: ignore[no-any-return]
        return None

    @property
    def parsedcomment(self) -> str | None:
        """Parsed upload comment.

        Returns:
            Parsed comment string, or None if not available.
        """
        cached = self._get_attribute("parsedcomment")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("parsedcomment",))
        if result and len(result) > 0:
            parsedcomment = result[0].get("parsedcomment")  # type: ignore[no-any-return]
            self._set_attribute("parsedcomment", parsedcomment)
            return parsedcomment  # type: ignore[no-any-return]
        return None

    @property
    def canonicaltitle(self) -> str | None:
        """Canonical title of the file.

        Returns:
            Canonical title string, or None if not available.
        """
        cached = self._get_attribute("canonicaltitle")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("canonicaltitle",))
        if result and len(result) > 0:
            canonicaltitle = result[0].get("canonicaltitle")  # type: ignore[no-any-return]
            self._set_attribute("canonicaltitle", canonicaltitle)
            return canonicaltitle  # type: ignore[no-any-return]
        return None

    @property
    def url(self) -> str | None:
        """Direct URL to the file.

        Returns:
            URL string, or None if not available.
        """
        cached = self._get_attribute("url")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("url",))
        if result and len(result) > 0:
            url = result[0].get("url")  # type: ignore[no-any-return]
            self._set_attribute("url", url)
            return url  # type: ignore[no-any-return]
        return None

    @property
    def size(self) -> int | None:
        """File size in bytes.

        Returns:
            File size as integer, or None if not available.
        """
        cached = self._get_attribute("size")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("size",))
        if result and len(result) > 0:
            size = result[0].get("size")  # type: ignore[no-any-return]
            if size is not None:
                size = int(size)
            self._set_attribute("size", size)
            return size  # type: ignore[no-any-return]
        return None

    @property
    def width(self) -> int | None:
        """Image width in pixels.

        Returns:
            Width as integer, or None if not available.
        """
        cached = self._get_attribute("width")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("size",))
        if result and len(result) > 0:
            width = result[0].get("width")  # type: ignore[no-any-return]
            if width is not None:
                width = int(width)
            self._set_attribute("width", width)
            return width  # type: ignore[no-any-return]
        return None

    @property
    def height(self) -> int | None:
        """Image height in pixels.

        Returns:
            Height as integer, or None if not available.
        """
        cached = self._get_attribute("height")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("size",))
        if result and len(result) > 0:
            height = result[0].get("height")  # type: ignore[no-any-return]
            if height is not None:
                height = int(height)
            self._set_attribute("height", height)
            return height  # type: ignore[no-any-return]
        return None

    @property
    def pagecount(self) -> int | None:
        """Number of pages (for PDF/multi-page files).

        Returns:
            Page count as integer, or None if not available.
        """
        cached = self._get_attribute("pagecount")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("size",))
        if result and len(result) > 0:
            pagecount = result[0].get("pagecount")  # type: ignore[no-any-return]
            if pagecount is not None:
                pagecount = int(pagecount)
            self._set_attribute("pagecount", pagecount)
            return pagecount  # type: ignore[no-any-return]
        return None

    @property
    def sha1(self) -> str | None:
        """SHA-1 hash of the file.

        Returns:
            SHA-1 hash string, or None if not available.
        """
        cached = self._get_attribute("sha1")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("sha1",))
        if result and len(result) > 0:
            sha1 = result[0].get("sha1")  # type: ignore[no-any-return]
            self._set_attribute("sha1", sha1)
            return sha1  # type: ignore[no-any-return]
        return None

    @property
    def mime(self) -> str | None:
        """MIME type of the file.

        Returns:
            MIME type string, or None if not available.
        """
        cached = self._get_attribute("mime")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("mime",))
        if result and len(result) > 0:
            mime = result[0].get("mime")  # type: ignore[no-any-return]
            self._set_attribute("mime", mime)
            return mime  # type: ignore[no-any-return]
        return None

    @property
    def thumbmime(self) -> str | None:
        """MIME type of thumbnail (if requested).

        Returns:
            Thumbnail MIME type string, or None if not available.
        """
        cached = self._get_attribute("thumbmime")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("thumbmime",))
        if result and len(result) > 0:
            thumbmime = result[0].get("thumbmime")  # type: ignore[no-any-return]
            self._set_attribute("thumbmime", thumbmime)
            return thumbmime  # type: ignore[no-any-return]
        return None

    @property
    def mediatype(self) -> str | None:
        """Media type of the file.

        Returns:
            Media type string (BITMAP, DRAWING, AUDIO, VIDEO, etc.), or None if not available.
        """
        cached = self._get_attribute("mediatype")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("mediatype",))
        if result and len(result) > 0:
            mediatype = result[0].get("mediatype")  # type: ignore[no-any-return]
            self._set_attribute("mediatype", mediatype)
            return mediatype  # type: ignore[no-any-return]
        return None

    @property
    def metadata(self) -> dict[str, Any] | None:
        """Exif metadata dictionary.

        Returns:
            Exif metadata dictionary, or None if not available.
        """
        cached = self._get_attribute("metadata")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("metadata",))
        if result and len(result) > 0:
            metadata = result[0].get("metadata")  # type: ignore[no-any-return]
            self._set_attribute("metadata", metadata)
            return metadata  # type: ignore[no-any-return]
        return None

    @property
    def commonmetadata(self) -> dict[str, Any] | None:
        """Common metadata dictionary.

        Returns:
            Common metadata dictionary, or None if not available.
        """
        cached = self._get_attribute("commonmetadata")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("commonmetadata",))
        if result and len(result) > 0:
            commonmetadata = result[0].get("commonmetadata")  # type: ignore[no-any-return]
            self._set_attribute("commonmetadata", commonmetadata)
            return commonmetadata  # type: ignore[no-any-return]
        return None

    @property
    def extmetadata(self) -> dict[str, Any] | None:
        """Extended metadata dictionary.

        Returns:
            Extended metadata dictionary, or None if not available.
        """
        cached = self._get_attribute("extmetadata")
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        result = self._fetch_imageinfo(("extmetadata",))
        if result and len(result) > 0:
            extmetadata = result[0].get("extmetadata")  # type: ignore[no-any-return]
            self._set_attribute("extmetadata", extmetadata)
            return extmetadata  # type: ignore[no-any-return]
        return None
