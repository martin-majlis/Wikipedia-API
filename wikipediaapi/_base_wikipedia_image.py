"""Base class for Wikipedia image representations.

This module defines the BaseWikipediaImage class which provides common
functionality for both synchronous and asynchronous Wikipedia image
representations, including caching, attribute mapping, and state management.
"""

from abc import ABC
from abc import abstractmethod
from typing import Any, Generic, TypeVar

from ._enums import Namespace
from ._enums import namespace2int
from ._enums import WikiNamespace

ImageT = TypeVar("ImageT", bound="BaseWikipediaImage[Any]")


class BaseWikipediaImage(ABC, Generic[ImageT]):
    """
    Common base for WikipediaImage and AsyncWikipediaImage.

    Contains all state initialization and every method or property whose
    behavior is identical in both the synchronous and asynchronous
    subclasses.

    * :attr:`ATTRIBUTES_MAPPING` — declarative mapping of attribute names
      to the API calls that populate them.
    * :meth:`__init__` — sets up all cache dictionaries to empty values;
      no network call is made.
    * Named properties that return init-time values without any fetch:
      ``title``, ``language``, ``variant``, ``ns``.
    """

    #: Mapping from public attribute names to the API ``prop`` values that
    #: populate them.  Subclasses use this mapping to implement lazy
    #: properties and awaitable getters.
    ATTRIBUTES_MAPPING: dict[str, str] = {
        "timestamp": "imageinfo",
        "user": "imageinfo",
        "userid": "imageinfo",
        "comment": "imageinfo",
        "parsedcomment": "imageinfo",
        "canonicaltitle": "imageinfo",
        "url": "imageinfo",
        "size": "imageinfo",
        "width": "imageinfo",
        "height": "imageinfo",
        "pagecount": "imageinfo",
        "sha1": "imageinfo",
        "mime": "imageinfo",
        "thumbmime": "imageinfo",
        "mediatype": "imageinfo",
        "metadata": "imageinfo",
        "commonmetadata": "imageinfo",
        "extmetadata": "imageinfo",
    }

    def __init__(
        self,
        wiki: Any,
        title: str,
        ns: WikiNamespace = Namespace.FILE,
        language: str = "en",
        variant: str | None = None,
    ) -> None:
        """Initialize image stub without network call.

        Args:
            wiki: The Wikipedia client instance that created this image.
            title: Image title as it appears in Wikipedia URLs.
            ns: Namespace; defaults to :attr:`Namespace.FILE`.
            language: Two-letter language code.
            variant: Language variant for auto-conversion, or ``None``.
        """
        self._wiki: Any = wiki
        self._title: str = title
        self._ns: WikiNamespace = ns
        self._language: str = language
        self._variant: str | None = variant

        # Cache for API responses by property set
        self._cache: dict[str, Any] = {}

        # Cache for individual attributes populated from API responses
        self._attributes: dict[str, Any] = {}

    @property
    def title(self) -> str:
        """Image title as passed to constructor."""
        return self._title

    @property
    def language(self) -> str:
        """Two-letter language code this image belongs to."""
        return self._language

    @property
    def variant(self) -> str | None:
        """Language variant used for auto-conversion, or ``None``."""
        return self._variant

    @property
    def ns(self) -> int:
        """Integer namespace number (``6`` = file namespace)."""
        return namespace2int(self._ns)

    def _get_cached(self, prop: str, cache_key: str) -> Any:
        """Return cached API response for *prop* and *cache_key*.

        Returns a sentinel value if the property is not cached.
        """
        return self._cache.get(f"{prop}:{cache_key}")

    def _set_cached(self, prop: str, cache_key: str, value: Any) -> None:
        """Store API response for *prop* and *cache_key*."""
        self._cache[f"{prop}:{cache_key}"] = value

    def _get_attribute(self, attr: str) -> Any:
        """Return cached attribute value, or sentinel if not cached."""
        return self._attributes.get(attr)

    def _set_attribute(self, attr: str, value: Any) -> None:
        """Store attribute value."""
        self._attributes[attr] = value

    @abstractmethod
    def _fetch_imageinfo(self, props: tuple[str, ...]) -> Any:
        """Fetch imageinfo data from API.

        Args:
            props: Tuple of property names to fetch.

        Returns:
            Raw API response data for the imageinfo call.
        """
        pass

    def exists(self) -> bool:
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
            result = self._fetch_imageinfo(("timestamp",))
            return result is not None and len(result) > 0
        except Exception:
            return False

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"<{self.__class__.__name__} title={self._title!r} language={self._language!r}>"

    def __str__(self) -> str:
        """Return the image title."""
        return self._title
