"""
Wikipedia-API is easy to use wrapper for extracting information from Wikipedia.

It supports extracting texts, sections, links, categories, translations, etc.
from Wikipedia. Documentation provides code snippets for the most common use
cases.
"""

from ._enums import Direction
from ._pages_dict import AsyncPagesDict
from ._pages_dict import PagesDict
from ._types import Coordinate
from ._types import GeoBox
from ._types import GeoPoint
from ._types import GeoSearchMeta
from ._types import SearchMeta
from ._types import SearchResults
from ._version import __version__ as __version
from .async_wikipedia import AsyncWikipedia
from .async_wikipedia_page import AsyncWikipediaPage
from .exceptions import WikiConnectionError
from .exceptions import WikiHttpError
from .exceptions import WikiHttpTimeoutError
from .exceptions import WikiInvalidJsonError
from .exceptions import WikipediaException
from .exceptions import WikiRateLimitError
from .extract_format import ExtractFormat
from .namespace import Namespace
from .namespace import namespace2int
from .namespace import WikiNamespace
from .wikipedia import USER_AGENT
from .wikipedia import Wikipedia
from .wikipedia_page import WikipediaPage
from .wikipedia_page_section import WikipediaPageSection

__version__ = __version

__all__ = [
    "Wikipedia",
    "AsyncWikipedia",
    "WikipediaPage",
    "AsyncWikipediaPage",
    "WikipediaPageSection",
    "Coordinate",
    "GeoBox",
    "GeoPoint",
    "GeoSearchMeta",
    "SearchMeta",
    "SearchResults",
    "PagesDict",
    "AsyncPagesDict",
    "WikipediaException",
    "WikiHttpTimeoutError",
    "WikiHttpError",
    "WikiRateLimitError",
    "WikiInvalidJsonError",
    "WikiConnectionError",
    "ExtractFormat",
    "Direction",
    "Namespace",
    "WikiNamespace",
    "namespace2int",
    "USER_AGENT",
]
