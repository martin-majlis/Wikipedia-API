"""
Wikipedia-API is easy to use wrapper for extracting information from Wikipedia.

It supports extracting texts, sections, links, categories, translations, etc.
from Wikipedia. Documentation provides code snippets for the most common use
cases.
"""

from ._enums import coordinate_type2str
from ._enums import coordinates_prop2str
from ._enums import CoordinatesProp
from ._enums import CoordinateType
from ._enums import Direction
from ._enums import direction2str
from ._enums import geosearch_sort2str
from ._enums import GeoSearchSort
from ._enums import Globe
from ._enums import globe2str
from ._enums import image_info_prop2str
from ._enums import ImageInfoProp
from ._enums import Namespace
from ._enums import namespace2int
from ._enums import redirect_filter2str
from ._enums import RedirectFilter
from ._enums import search_info2str
from ._enums import search_prop2str
from ._enums import search_qi_profile2str
from ._enums import search_sort2str
from ._enums import search_what2str
from ._enums import SearchInfo
from ._enums import SearchProp
from ._enums import SearchQiProfile
from ._enums import SearchSort
from ._enums import SearchWhat
from ._enums import WikiCoordinatesProp
from ._enums import WikiCoordinateType
from ._enums import WikiDirection
from ._enums import WikiGeoSearchSort
from ._enums import WikiGlobe
from ._enums import WikiImageInfoProp
from ._enums import WikiNamespace
from ._enums import WikiSearchInfo
from ._enums import WikiSearchProp
from ._enums import WikiSearchQiProfile
from ._enums import WikiSearchSort
from ._enums import WikiSearchWhat
from ._pages_dict import AsyncImagesDict
from ._pages_dict import AsyncPagesDict
from ._pages_dict import ImagesDict
from ._pages_dict import PagesDict
from ._types import Coordinate
from ._types import GeoBox
from ._types import GeoPoint
from ._types import GeoSearchMeta
from ._types import SearchMeta
from ._types import SearchResults
from ._version import __version__ as __version
from .async_wikipedia import AsyncWikipedia
from .async_wikipedia_image import AsyncWikipediaImage
from .async_wikipedia_page import AsyncWikipediaPage
from .exceptions import WikiConnectionError
from .exceptions import WikiHttpError
from .exceptions import WikiHttpTimeoutError
from .exceptions import WikiInvalidJsonError
from .exceptions import WikipediaException
from .exceptions import WikiRateLimitError
from .extract_format import ExtractFormat
from .wikipedia import USER_AGENT
from .wikipedia import Wikipedia
from .wikipedia_image import WikipediaImage
from .wikipedia_page import WikipediaPage
from .wikipedia_page_section import WikipediaPageSection

__version__ = __version

__all__ = [
    "Wikipedia",
    "AsyncWikipedia",
    "WikipediaPage",
    "AsyncWikipediaPage",
    "WikipediaPageSection",
    "WikipediaImage",
    "AsyncWikipediaImage",
    "Coordinate",
    "GeoBox",
    "GeoPoint",
    "GeoSearchMeta",
    "SearchMeta",
    "SearchResults",
    "PagesDict",
    "AsyncPagesDict",
    "ImagesDict",
    "AsyncImagesDict",
    "WikipediaException",
    "WikiHttpTimeoutError",
    "WikiHttpError",
    "WikiRateLimitError",
    "WikiInvalidJsonError",
    "WikiConnectionError",
    "ExtractFormat",
    "Direction",
    "WikiDirection",
    "direction2str",
    "CoordinateType",
    "WikiCoordinateType",
    "coordinate_type2str",
    "CoordinatesProp",
    "WikiCoordinatesProp",
    "coordinates_prop2str",
    "GeoSearchSort",
    "WikiGeoSearchSort",
    "geosearch_sort2str",
    "Globe",
    "WikiGlobe",
    "globe2str",
    "ImageInfoProp",
    "WikiImageInfoProp",
    "image_info_prop2str",
    "RedirectFilter",
    "WikiRedirectFilter",
    "redirect_filter2str",
    "SearchInfo",
    "WikiSearchInfo",
    "search_info2str",
    "SearchProp",
    "WikiSearchProp",
    "search_prop2str",
    "SearchQiProfile",
    "WikiSearchQiProfile",
    "search_qi_profile2str",
    "SearchWhat",
    "WikiSearchWhat",
    "search_what2str",
    "SearchSort",
    "WikiSearchSort",
    "search_sort2str",
    "Namespace",
    "WikiNamespace",
    "namespace2int",
    "USER_AGENT",
]
