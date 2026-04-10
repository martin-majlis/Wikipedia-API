"""
Wikipedia-API is easy to use wrapper for extracting information from Wikipedia.

It supports extracting texts, sections, links, categories, translations, etc.
from Wikipedia. Documentation provides code snippets for the most common use
cases.
"""

from ._enums.coordinate_type import CoordinateType
from ._enums.coordinate_type import WikiCoordinateType
from ._enums.coordinate_type import coordinate_type2str
from ._enums.coordinates_prop import CoordinatesProp
from ._enums.coordinates_prop import WikiCoordinatesProp
from ._enums.coordinates_prop import coordinates_prop2str
from ._enums.direction import Direction
from ._enums.direction import WikiDirection
from ._enums.direction import direction2str
from ._enums.geosearch_sort import GeoSearchSort
from ._enums.geosearch_sort import WikiGeoSearchSort
from ._enums.geosearch_sort import geosearch_sort2str
from ._enums.globe import Globe
from ._enums.globe import WikiGlobe
from ._enums.globe import globe2str
from ._enums.namespace import Namespace
from ._enums.namespace import WikiNamespace
from ._enums.namespace import namespace2int
from ._enums.redirect_filter import RedirectFilter
from ._enums.redirect_filter import WikiRedirectFilter
from ._enums.redirect_filter import redirect_filter2str
from ._enums.search_info import SearchInfo
from ._enums.search_info import WikiSearchInfo
from ._enums.search_info import search_info2str
from ._enums.search_prop import SearchProp
from ._enums.search_prop import WikiSearchProp
from ._enums.search_prop import search_prop2str
from ._enums.search_qi_profile import SearchQiProfile
from ._enums.search_qi_profile import WikiSearchQiProfile
from ._enums.search_qi_profile import search_qi_profile2str
from ._enums.search_sort import SearchSort
from ._enums.search_sort import WikiSearchSort
from ._enums.search_sort import search_sort2str
from ._enums.search_what import SearchWhat
from ._enums.search_what import WikiSearchWhat
from ._enums.search_what import search_what2str
from ._http_client import USER_AGENT
from ._http_client import AsyncHTTPClient
from ._http_client import BaseHTTPClient
from ._http_client import SyncHTTPClient
from ._image.async_wikipedia_image import AsyncWikipediaImage
from ._image.wikipedia_image import WikipediaImage
from ._page.async_wikipedia_page import AsyncWikipediaPage
from ._page.wikipedia_page import WikipediaPage
from ._page.wikipedia_page_section import WikipediaPageSection
from ._pages_dict import AsyncImagesDict
from ._pages_dict import AsyncPagesDict
from ._pages_dict import ImagesDict
from ._pages_dict import PagesDict
from ._resources import AsyncWikipediaResource
from ._resources import BaseWikipediaResource
from ._resources import WikipediaResource
from ._types import Coordinate
from ._types import GeoBox
from ._types import GeoPoint
from ._types import GeoSearchMeta
from ._types import ImageInfo
from ._types import SearchMeta
from ._types import SearchResults
from ._version import __version__ as __version
from ._wikipedia.async_wikipedia import AsyncWikipedia
from ._wikipedia.wikipedia import Wikipedia
from .exceptions import WikiConnectionError
from .exceptions import WikiHttpError
from .exceptions import WikiHttpTimeoutError
from .exceptions import WikiInvalidJsonError
from .exceptions import WikipediaException
from .exceptions import WikiRateLimitError
from .extract_format import ExtractFormat

__version__ = __version

__all__ = [
    "Wikipedia",
    "AsyncWikipedia",
    "WikipediaPage",
    "AsyncWikipediaPage",
    "WikipediaImage",
    "AsyncWikipediaImage",
    "WikipediaPageSection",
    "Coordinate",
    "GeoBox",
    "GeoPoint",
    "GeoSearchMeta",
    "ImageInfo",
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
    "BaseHTTPClient",
    "SyncHTTPClient",
    "AsyncHTTPClient",
    "BaseWikipediaResource",
    "WikipediaResource",
    "AsyncWikipediaResource",
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
    "Namespace",
    "WikiNamespace",
    "namespace2int",
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
    "SearchSort",
    "WikiSearchSort",
    "search_sort2str",
    "SearchWhat",
    "WikiSearchWhat",
    "search_what2str",
    "USER_AGENT",
]
