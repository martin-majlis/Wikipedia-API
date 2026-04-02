r"""Shared enum definitions for Wikipedia API options.

This module provides type-safe enum classes for Wikipedia API parameters,
along with type aliases and converter functions that enable both enum
and string usage while maintaining backward compatibility.

**Key Features:**

- **Type Safety**: Strong typing for API parameters with enum members
- **Backward Compatibility**: All existing string-based code continues to work
- **Flexible Type Aliases**: ``Wiki*`` aliases accept both enums and strings
- **Converter Functions**: Handle enum-to-string conversion gracefully

**Available Enums:**

- **Search Enums**:
  - :class:`SearchProp` - Search result properties (``SIZE``, ``WORDCOUNT``, ``TIMESTAMP``, etc.)
  - :class:`SearchInfo` - Search metadata (``TOTAL_HITS``, ``SUGGESTION``, ``REWRITTEN_QUERY``)
  - :class:`SearchWhat` - Search types (``TEXT``, ``TITLE``, ``NEAR_MATCH``)
  - :class:`SearchQiProfile` - Ranking profiles (``ENGINE_AUTO_SELECT``, ``CLASSIC``, etc.)
  - :class:`SearchSort` - Sort options (``RELEVANCE``, ``LAST_EDIT_DESC``, etc.)

- **Geographic Enums**:
  - :class:`Globe` - Celestial bodies (``EARTH``, ``MARS``, ``MOON``, ``VENUS``)
  - :class:`CoordinateType` - Coordinate filtering (``ALL``, ``PRIMARY``, ``SECONDARY``)
  - :class:`CoordinatesProp` - Coordinate properties
    (``COUNTRY``, ``DIM``, ``GLOBE``, ``NAME``, ``REGION``, ``TYPE``)
  - :class:`GeoSearchSort` - Geographic sort options (``DISTANCE``, ``RELEVANCE``)

- **Utility Enums**:
  - :class:`RedirectFilter` - Redirect filtering (``ALL``, ``REDIRECTS``, ``NONREDIRECTS``)
  - :class:`Direction` - Sort direction (``ASCENDING``, ``DESCENDING``)
  - :class:`Namespace` - MediaWiki namespaces (integer values 0-105+)

**Usage Examples:**

.. code-block:: python

    from wikipediaapi import (
        SearchProp, SearchInfo, SearchWhat, SearchQiProfile, SearchSort,
        WikiSearchProp, WikiSearchInfo, WikiSearchWhat, WikiSearchQiProfile
    )

    # Type-safe enum usage (recommended)
    results = wiki.search(
        "python",
        prop=[SearchProp.SIZE, SearchProp.WORDCOUNT],
        info=[SearchInfo.TOTAL_HITS, SearchInfo.SUGGESTION],
        what=SearchWhat.TEXT,
        qi_profile=SearchQiProfile.ENGINE_AUTO_SELECT,
        sort=SearchSort.RELEVANCE
    )

    # Backward-compatible string usage (still works)
    results = wiki.search(
        "python",
        prop=["size", "wordcount"],
        info=["totalhits", "suggestion"],
        what="text",
        qi_profile="engine_autoselect",
        sort="relevance"
    )

    # Type-safe function signatures
    def search_function(
        query: str,
        prop: list[WikiSearchProp] | None = None,
        info: list[WikiSearchInfo] | None = None,
        what: WikiSearchWhat | None = None,
        qi_profile: WikiSearchQiProfile | None = None
    ) -> SearchResults:
        \"\"\"Accepts both enums and strings for maximum flexibility.\"\"\"
        return wiki.search(query, prop=prop, info=info, what=what, qi_profile=qi_profile)

    # Coordinate enum usage
    from wikipediaapi import (
        CoordinatesProp,
        CoordinateType,
        WikiCoordinatesProp,
        WikiCoordinateType,
    )

    # Type-safe coordinate usage
    coords = wiki.coordinates(
        page,
        prop=[CoordinatesProp.GLOBE, CoordinatesProp.TYPE, CoordinatesProp.COUNTRY],
        primary=CoordinateType.ALL
    )

    # Backward-compatible coordinate usage
    coords = wiki.coordinates(
        page,
        prop=["globe", "type", "country"],
        primary="all"
    )

**Converter Functions:**

The module provides converter functions that handle both enum and string inputs:
- :func:`search_prop2str` - Convert :class:`WikiSearchProp` to string
- :func:`search_info2str` - Convert :class:`WikiSearchInfo` to string
- :func:`search_what2str` - Convert :class:`WikiSearchWhat` to string
- :func:`search_qi_profile2str` - Convert :class:`WikiSearchQiProfile` to string
- :func:`search_sort2str` - Convert :class:`WikiSearchSort` to string
- :func:`geosearch_sort2str` - Convert :class:`WikiGeoSearchSort` to string
- :func:`globe2str` - Convert :class:`Globe` to string
- :func:`coordinate_type2str` - Convert :class:`CoordinateType` to string
- :func:`coordinates_prop2str` - Convert :class:`WikiCoordinatesProp` to string
- :func:`redirect_filter2str` - Convert :class:`WikiRedirectFilter` to string
- :func:`direction2str` - Convert :class:`Direction` to string
- :func:`namespace2int` - Convert :class:`Namespace` to string

All converters follow the same pattern: enum members are converted to their
string values, while strings are passed through unchanged. This enables
seamless backward compatibility while providing type safety for new code.
"""

# Import all enum classes and converters
from .coordinate_type import CoordinateType
from .coordinate_type import WikiCoordinateType
from .coordinate_type import coordinate_type2str
from .coordinates_prop import CoordinatesProp
from .coordinates_prop import WikiCoordinatesProp
from .coordinates_prop import coordinates_prop2str
from .direction import Direction
from .direction import WikiDirection
from .direction import direction2str
from .geosearch_sort import GeoSearchSort
from .geosearch_sort import WikiGeoSearchSort
from .geosearch_sort import geosearch_sort2str
from .globe import Globe
from .globe import WikiGlobe
from .globe import globe2str
from .namespace import Namespace
from .namespace import WikiNamespace
from .namespace import namespace2int
from .redirect_filter import RedirectFilter
from .redirect_filter import WikiRedirectFilter
from .redirect_filter import redirect_filter2str
from .search_info import SearchInfo
from .search_info import WikiSearchInfo
from .search_info import search_info2str
from .search_prop import SearchProp
from .search_prop import WikiSearchProp
from .search_prop import search_prop2str
from .search_qi_profile import SearchQiProfile
from .search_qi_profile import WikiSearchQiProfile
from .search_qi_profile import search_qi_profile2str
from .search_sort import SearchSort
from .search_sort import WikiSearchSort
from .search_sort import search_sort2str
from .search_what import SearchWhat
from .search_what import WikiSearchWhat
from .search_what import search_what2str

# Export all public symbols
__all__ = [
    # Enum classes
    "CoordinateType",
    "WikiCoordinateType",
    "CoordinatesProp",
    "WikiCoordinatesProp",
    "Direction",
    "WikiDirection",
    "GeoSearchSort",
    "WikiGeoSearchSort",
    "Globe",
    "WikiGlobe",
    "RedirectFilter",
    "WikiRedirectFilter",
    "SearchProp",
    "WikiSearchProp",
    "SearchInfo",
    "WikiSearchInfo",
    "SearchWhat",
    "WikiSearchWhat",
    "SearchQiProfile",
    "WikiSearchQiProfile",
    "SearchSort",
    "WikiSearchSort",
    "Namespace",
    "WikiNamespace",
    # Converter functions
    "coordinate_type2str",
    "coordinates_prop2str",
    "direction2str",
    "geosearch_sort2str",
    "globe2str",
    "redirect_filter2str",
    "search_prop2str",
    "search_info2str",
    "search_what2str",
    "search_qi_profile2str",
    "search_sort2str",
    "namespace2int",
]
