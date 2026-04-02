"""
Wikipedia-API is easy to use wrapper for extracting information from Wikipedia.

It supports extracting texts, sections, links, categories, translations, etc.
from Wikipedia. Documentation provides code snippets for the most common use
cases.
"""

from ._enums.coordinate_type import CoordinateType, WikiCoordinateType, coordinate_type2str
from ._enums.coordinates_prop import CoordinatesProp, WikiCoordinatesProp, coordinates_prop2str
from ._enums.direction import Direction, WikiDirection, direction2str
from ._enums.geosearch_sort import GeoSearchSort, WikiGeoSearchSort, geosearch_sort2str
from ._enums.globe import Globe, WikiGlobe, globe2str
from ._enums.namespace import Namespace, WikiNamespace, namespace2int
from ._enums.redirect_filter import RedirectFilter, WikiRedirectFilter, redirect_filter2str
from ._enums.search_info import SearchInfo, WikiSearchInfo, search_info2str
from ._enums.search_prop import SearchProp, WikiSearchProp, search_prop2str
from ._enums.search_qi_profile import SearchQiProfile, WikiSearchQiProfile, search_qi_profile2str
from ._enums.search_sort import SearchSort, WikiSearchSort, search_sort2str
from ._enums.search_what import SearchWhat, WikiSearchWhat, search_what2str
from ._http_client import USER_AGENT, AsyncHTTPClient, BaseHTTPClient, SyncHTTPClient
from ._pages_dict import AsyncImagesDict, AsyncPagesDict, ImagesDict, PagesDict
from ._resources import AsyncWikipediaResource, BaseWikipediaResource, WikipediaResource
from ._types import (
    Coordinate,
    GeoBox,
    GeoPoint,
    GeoSearchMeta,
    ImageInfo,
    SearchMeta,
    SearchResults,
)
from ._version import __version__ as __version
from .async_wikipedia import AsyncWikipedia
from .async_wikipedia_image import AsyncWikipediaImage
from .async_wikipedia_page import AsyncWikipediaPage
from .exceptions import (
    WikiConnectionError,
    WikiHttpError,
    WikiHttpTimeoutError,
    WikiInvalidJsonError,
    WikipediaException,
    WikiRateLimitError,
)
from .extract_format import ExtractFormat
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
