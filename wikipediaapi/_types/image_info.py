"""A single revision's metadata for a file from prop=imageinfo.

Represents one entry from the ``prop=imageinfo`` API response.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImageInfo:
    """Metadata for one revision of a file from ``prop=imageinfo``.

    Represents one entry in the ``imageinfo`` list returned by the
    MediaWiki ``prop=imageinfo`` API.  All fields are optional because
    the API may omit them depending on the ``iiprop`` parameter and
    file availability.

    Args:
        timestamp: ISO 8601 timestamp of this file revision.
        user: Username of the uploader.
        url: Full URL of the file.
        descriptionurl: URL of the file description page.
        descriptionshorturl: Short URL of the file description page.
        width: Image width in pixels.
        height: Image height in pixels.
        size: File size in bytes.
        mime: MIME type of the file (e.g. ``"image/jpeg"``).
        mediatype: MediaWiki media type (e.g. ``"BITMAP"``).
        sha1: SHA-1 hash of the file content.
    """

    timestamp: str | None = None
    user: str | None = None
    url: str | None = None
    descriptionurl: str | None = None
    descriptionshorturl: str | None = None
    width: int | None = None
    height: int | None = None
    size: int | None = None
    mime: str | None = None
    mediatype: str | None = None
    sha1: str | None = None
