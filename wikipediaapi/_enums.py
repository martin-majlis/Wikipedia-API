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
  - :class:`CoordinatesProp` - Coordinate properties (``COUNTRY``, ``DIM``, ``GLOBE``, ``NAME``, ``REGION``, ``TYPE``)
  - :class:`GeoSearchSort` - Geographic sort options (``DISTANCE``, ``RELEVANCE``)

- **Utility Enums**:
  - :class:`RedirectFilter` - Redirect filtering (``ALL``, ``REDIRECTS``, ``NONREDIRECTS``)
  - :class:`Direction` - Sort direction (``ASCENDING``, ``DESCENDING``)

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
        info=[SearchInfo.TOTAL_HITS],
        what=SearchWhat.TEXT,
        qi_profile=SearchQiProfile.ENGINE_AUTO_SELECT,
        sort=SearchSort.RELEVANCE
    )

    # Backward-compatible string usage (still works)
    results = wiki.search(
        "python",
        prop=["size", "wordcount"],
        info=["totalhits"],
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
    from wikipediaapi import CoordinatesProp, CoordinateType, WikiCoordinatesProp, WikiCoordinateType

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
- :func:`globe2str` - Convert :class:`WikiGlobe` to string
- :func:`coordinate_type2str` - Convert :class:`WikiCoordinateType` to string
- :func:`coordinates_prop2str` - Convert :class:`WikiCoordinatesProp` to string
- :func:`redirect_filter2str` - Convert :class:`WikiRedirectFilter` to string
- :func:`direction2str` - Convert :class:`WikiDirection` to string

All converters follow the same pattern: enum members are converted to their
string values, while strings are passed through unchanged. This enables
seamless backward compatibility while providing type safety for new code.
"""

from enum import Enum
from enum import IntEnum
from typing import Union


class Direction(Enum):
    """Sort direction values for image query methods.

    This enum is used by ``images`` and ``batch_images`` methods in both
    sync and async APIs.
    """

    ASCENDING = "ascending"
    DESCENDING = "descending"


#: Type alias for direction arguments accepted throughout the library.
#: Accepts either a :class:`Direction` enum member or a raw ``str``,
#: e.g. ``Direction.ASCENDING`` or simply ``"ascending"``.
WikiDirection = Union[Direction, str]


def direction2str(direction: WikiDirection) -> str:
    """
    Convert a :class:`WikiDirection` value to a plain ``str``.

    If *direction* is a :class:`Direction` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    :param direction: direction to convert
    :return: string representation of the direction
    """
    if isinstance(direction, Direction):
        return direction.value

    return direction


class SearchSort(Enum):
    """Sort values for the ``search`` method."""

    CREATE_TIMESTAMP_ASC = "create_timestamp_asc"
    CREATE_TIMESTAMP_DESC = "create_timestamp_desc"
    INCOMING_LINKS_ASC = "incoming_links_asc"
    INCOMING_LINKS_DESC = "incoming_links_desc"
    JUST_MATCH = "just_match"
    LAST_EDIT_ASC = "last_edit_asc"
    LAST_EDIT_DESC = "last_edit_desc"
    NONE = "none"
    RANDOM = "random"
    RELEVANCE = "relevance"
    TITLE_NATURAL_ASC = "title_natural_asc"
    TITLE_NATURAL_DESC = "title_natural_desc"
    USER_RANDOM = "user_random"


#: Type alias for search sort arguments accepted by ``search``.
#: Accepts either a :class:`SearchSort` enum member or a raw ``str``.
WikiSearchSort = Union[SearchSort, str]


def search_sort2str(sort: WikiSearchSort) -> str:
    """
    Convert a :class:`WikiSearchSort` value to a plain ``str``.

    :param sort: sort direction to convert
    :return: string representation of the sort direction
    """
    if isinstance(sort, SearchSort):
        return sort.value

    return sort


class GeoSearchSort(Enum):
    """Sort values for the ``geosearch`` method."""

    DISTANCE = "distance"
    RELEVANCE = "relevance"


#: Type alias for geosearch sort arguments accepted by ``geosearch``.
#: Accepts either a :class:`GeoSearchSort` enum member or a raw ``str``.
WikiGeoSearchSort = Union[GeoSearchSort, str]


def geosearch_sort2str(sort: WikiGeoSearchSort) -> str:
    """
    Convert a :class:`WikiGeoSearchSort` value to a plain ``str``.

    :param sort: geosearch sort direction to convert
    :return: string representation of the sort direction
    """
    if isinstance(sort, GeoSearchSort):
        return sort.value

    return sort


class Globe(Enum):
    """Globe values for geosearch and coordinates methods."""

    EARTH = "earth"
    MARS = "mars"
    MOON = "moon"
    VENUS = "venus"


#: Type alias for globe arguments accepted by geosearch methods.
#: Accepts either a :class:`Globe` enum member or a raw ``str``.
WikiGlobe = Union[Globe, str]


def globe2str(globe: WikiGlobe) -> str:
    """
    Convert a :class:`WikiGlobe` value to a plain ``str``.

    :param globe: globe to convert
    :return: string representation of the globe
    """
    if isinstance(globe, Globe):
        return globe.value

    return globe


class CoordinateType(Enum):
    """Coordinate types for coordinates and geosearch methods.

    This enum is used by ``coordinates``, ``batch_coordinates``, and ``geosearch``
    methods in both sync and async APIs to specify which type of coordinates to return.

    **Enum Values:**

    - ``ALL`` - Return both primary and secondary coordinates
    - ``PRIMARY`` - Return only primary coordinates (location of the article subject)
    - ``SECONDARY`` - Return only secondary coordinates (locations of objects mentioned in article)

    **Usage Example:**

    .. code-block:: python

        from wikipediaapi import CoordinateType, WikiCoordinateType

        # Using enum members (type-safe)
        coords = wiki.coordinates(page, primary=CoordinateType.ALL)

        # Using strings (backward compatible)
        coords = wiki.coordinates(page, primary="all")

        # In function signatures
        def coords_function(primary: WikiCoordinateType) -> list[Coordinate]:
            return wiki.coordinates(page, primary=primary)
    """

    ALL = "all"
    """Return both primary and secondary coordinates."""

    PRIMARY = "primary"
    """Return only primary coordinates (location of the article subject)."""

    SECONDARY = "secondary"
    """Return only secondary coordinates (locations of objects mentioned in article)."""


#: Type alias for primary coordinate arguments.
#: Accepts either a :class:`CoordinateType` enum member or a raw ``str``.
WikiCoordinateType = Union[CoordinateType, str]


def coordinate_type2str(ctype: WikiCoordinateType) -> str:
    """
    Convert a :class:`WikiCoordinateType` value to a plain ``str``.

    If *ctype* is a :class:`CoordinateType` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    This converter is used internally by the library to handle both enum
    and string inputs gracefully, providing backward compatibility while
    enabling type-safe usage.

    :param ctype: coordinate type to convert
    :return: string representation of the coordinate type

    **Examples:**

    .. code-block:: python

        from wikipediaapi import coordinate_type2str, CoordinateType

        # Convert enum to string
        assert coordinate_type2str(CoordinateType.ALL) == "all"
        assert coordinate_type2str(CoordinateType.PRIMARY) == "primary"

        # String pass-through (unchanged)
        assert coordinate_type2str("all") == "all"
        assert coordinate_type2str("primary") == "primary"

        # Custom values pass through
        assert coordinate_type2str("custom_type") == "custom_type"
    """
    if isinstance(ctype, CoordinateType):
        return ctype.value

    return ctype


class CoordinatesProp(Enum):
    """Property values for coordinates query methods.

    This enum is used by ``coordinates`` and ``batch_coordinates`` methods in both
    sync and async APIs to specify which additional coordinate properties
    to return from the MediaWiki API.

    **Enum Values:**

    - ``COUNTRY`` - ISO 3166-1 alpha-2 country code (e.g. US or RU)
    - ``DIM`` - Approximate size of the object in meters
    - ``GLOBE`` - Which terrestrial body the coordinates are relative to (e.g. moon or pluto)
    - ``NAME`` - Name of the object the coordinates point to
    - ``REGION`` - ISO 3166-2 region code (the part after the dash; e.g. FL or MOS)
    - ``TYPE`` - Type of the object the coordinates point to

    **Usage Example:**

    .. code-block:: python

        from wikipediaapi import CoordinatesProp, WikiCoordinatesProp

        # Using enum members (type-safe)
        coords = wiki.coordinates(page, prop=[CoordinatesProp.GLOBE, CoordinatesProp.TYPE])

        # Using strings (backward compatible)
        coords = wiki.coordinates(page, prop=["globe", "type"])

        # In function signatures
        def coords_function(prop: list[WikiCoordinatesProp]) -> list[Coordinate]:
            return wiki.coordinates(page, prop=prop)

        # Mixed usage (enum and string)
        coords = wiki.coordinates(page, prop=[CoordinatesProp.GLOBE, "type"])
    """

    COUNTRY = "country"
    """ISO 3166-1 alpha-2 country code (e.g. US or RU)."""

    DIM = "dim"
    """Approximate size of the object in meters."""

    GLOBE = "globe"
    """Which terrestrial body the coordinates are relative to (e.g. moon or pluto)."""

    NAME = "name"
    """Name of the object the coordinates point to."""

    REGION = "region"
    """ISO 3166-2 region code (the part after the dash; e.g. FL or MOS)."""

    TYPE = "type"
    """Type of the object the coordinates point to."""


#: Type alias for coordinates property arguments accepted throughout the library.
#: Accepts either a :class:`CoordinatesProp` enum member or a raw ``str``,
#: e.g. ``CoordinatesProp.GLOBE`` or simply ``"globe"``.
WikiCoordinatesProp = Union[CoordinatesProp, str]


def coordinates_prop2str(prop: WikiCoordinatesProp) -> str:
    """
    Convert a :class:`WikiCoordinatesProp` value to a plain ``str``.

    If *prop* is a :class:`CoordinatesProp` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    This converter is used internally by the library to handle both enum
    and string inputs gracefully, providing backward compatibility while
    enabling type-safe usage.

    :param prop: coordinates property to convert
    :return: string representation of the coordinates property

    **Examples:**

    .. code-block:: python

        from wikipediaapi import coordinates_prop2str, CoordinatesProp

        # Convert enum to string
        assert coordinates_prop2str(CoordinatesProp.GLOBE) == "globe"
        assert coordinates_prop2str(CoordinatesProp.COUNTRY) == "country"

        # String pass-through (unchanged)
        assert coordinates_prop2str("globe") == "globe"
        assert coordinates_prop2str("country") == "country"

        # Custom values pass through
        assert coordinates_prop2str("custom_prop") == "custom_prop"
    """
    if isinstance(prop, CoordinatesProp):
        return prop.value

    return prop


class RedirectFilter(Enum):
    """Filter redirect values for methods like random."""

    ALL = "all"
    NONREDIRECTS = "nonredirects"
    REDIRECTS = "redirects"


#: Type alias for redirect filter arguments.
#: Accepts either a :class:`RedirectFilter` enum member or a raw ``str``.
WikiRedirectFilter = Union[RedirectFilter, str]


def redirect_filter2str(rfilter: WikiRedirectFilter) -> str:
    """
    Convert a :class:`WikiRedirectFilter` value to a plain ``str``.

    :param rfilter: redirect filter to convert
    :return: string representation of the redirect filter
    """
    if isinstance(rfilter, RedirectFilter):
        return rfilter.value

    return rfilter


class Namespace(IntEnum):
    """
    Integer enumeration of MediaWiki namespaces.

    Each Wikipedia page belongs to a namespace identified by an integer.
    Namespace 0 (``MAIN``) contains ordinary articles; other values
    represent talk pages, user pages, category pages, etc.

    Pass a member of this enum wherever a ``WikiNamespace`` is accepted
    (e.g. ``wiki.page("Python", ns=Namespace.MAIN)``).

    Full namespace reference:

    * https://en.wikipedia.org/wiki/Wikipedia:Namespace
    * https://en.wikipedia.org/wiki/Wikipedia:Namespace#Programming
    """

    MAIN = 0
    """Main article namespace (ns=0). Ordinary Wikipedia articles live here."""

    TALK = 1
    """Talk namespace (ns=1). Discussion pages for main-namespace articles."""

    USER = 2
    """User namespace (ns=2). Pages belonging to registered users."""

    USER_TALK = 3
    """User talk namespace (ns=3). Discussion pages for user pages."""

    WIKIPEDIA = 4
    """Wikipedia project namespace (ns=4). Policy and project pages."""

    WIKIPEDIA_TALK = 5
    """Wikipedia talk namespace (ns=5). Discussion of project pages."""

    FILE = 6
    """File namespace (ns=6). Images, audio files, and other media."""

    FILE_TALK = 7
    """File talk namespace (ns=7). Discussion of file pages."""

    MEDIAWIKI = 8
    """MediaWiki namespace (ns=8). Interface messages and system texts."""

    MEDIAWIKI_TALK = 9
    """MediaWiki talk namespace (ns=9). Discussion of interface messages."""

    TEMPLATE = 10
    """Template namespace (ns=10). Reusable wiki templates."""

    TEMPLATE_TALK = 11
    """Template talk namespace (ns=11). Discussion of templates."""

    HELP = 12
    """Help namespace (ns=12). Help and how-to pages."""

    HELP_TALK = 13
    """Help talk namespace (ns=13). Discussion of help pages."""

    CATEGORY = 14
    """Category namespace (ns=14). Category pages that group articles."""

    CATEGORY_TALK = 15
    """Category talk namespace (ns=15). Discussion of category pages."""

    PORTAL = 100
    """Portal namespace (ns=100). Topic-focused entry-point portals."""

    PORTAL_TALK = 101
    """Portal talk namespace (ns=101). Discussion of portals."""

    PROJECT = 102
    """Project namespace (ns=102). WikiProject coordination pages."""

    PROJECT_TALK = 103
    """Project talk namespace (ns=103). Discussion of WikiProject pages."""

    REFERENCE = 104
    """Reference namespace (ns=104). Reference desk pages."""

    REFERENCE_TALK = 105
    """Reference talk namespace (ns=105). Discussion of reference pages."""

    BOOK = 108
    """Book namespace (ns=108). Wikipedia book pages."""

    BOOK_TALK = 109
    """Book talk namespace (ns=109). Discussion of book pages."""

    DRAFT = 118
    """Draft namespace (ns=118). Unreviewed draft articles."""

    DRAFT_TALK = 119
    """Draft talk namespace (ns=119). Discussion of draft pages."""

    EDUCATION_PROGRAM = 446
    """Education Program namespace (ns=446). Educational course pages."""

    EDUCATION_PROGRAM_TALK = 447
    """Education Program talk namespace (ns=447)."""

    TIMED_TEXT = 710
    """TimedText namespace (ns=710). Subtitle/caption files for media."""

    TIMED_TEXT_TALK = 711
    """TimedText talk namespace (ns=711). Discussion of timed-text pages."""

    MODULE = 828
    """Module namespace (ns=828). Lua scripting modules."""

    MODULE_TALK = 829
    """Module talk namespace (ns=829). Discussion of Lua modules."""

    GADGET = 2300
    """Gadget namespace (ns=2300). JavaScript gadget pages."""

    GADGET_TALK = 2301
    """Gadget talk namespace (ns=2301). Discussion of gadget pages."""

    GADGET_DEFINITION = 2302
    """Gadget definition namespace (ns=2302). Gadget definition pages."""

    GADGET_DEFINITION_TALK = 2303
    """Gadget definition talk namespace (ns=2303)."""


#: Type alias for namespace arguments accepted throughout the library.
#: Accepts either a :class:`Namespace` enum member or a raw ``int``,
#: e.g. ``Namespace.CATEGORY`` or simply ``14``.
WikiNamespace = Union[Namespace, int]


def namespace2int(namespace: WikiNamespace) -> int:
    """
    Convert a :class:`WikiNamespace` value to a plain ``int``.

    If *namespace* is a :class:`Namespace` enum member its integer value
    is returned.  If it is already an ``int`` it is returned unchanged.

    :param namespace: namespace to convert
    :return: integer representation of the namespace
    """
    if isinstance(namespace, Namespace):
        return namespace.value

    return namespace


class SearchProp(Enum):
    """Property values for search query methods.

    This enum is used by the ``search`` method in both sync and async
    clients to specify which properties to include in search results.

    The ``srprop`` parameter is deprecated upstream but still supported.

    **Usage Example:**

    .. code-block:: python

        from wikipediaapi import SearchProp, WikiSearchProp

        # Using enum members (type-safe)
        results = wiki.search("python", prop=[SearchProp.SIZE, SearchProp.WORDCOUNT])

        # Using strings (backward compatible)
        results = wiki.search("python", prop=["size", "wordcount"])

        # In function signatures
        def search_function(prop: list[WikiSearchProp]) -> SearchResults:
            return wiki.search("query", prop=prop)
    """

    SIZE = "size"
    """Adds the size of the page in bytes."""

    WORDCOUNT = "wordcount"
    """Adds the word count of the page."""

    TIMESTAMP = "timestamp"
    """Adds the timestamp of when the page was last edited."""

    SNIPPET = "snippet"
    """Adds a snippet of the page with query term highlighting markup."""

    TITLE_SNIPPET = "titlesnippet"
    """Adds the page title with query term highlighting markup."""

    REDIRECT_TITLE = "redirecttitle"
    """Adds the title of the matching redirect."""

    REDIRECT_SNIPPET = "redirectsnippet"
    """Adds the title of the matching redirect with highlighting."""

    SECTION_TITLE = "sectiontitle"
    """Adds the title of the matching section."""

    SECTION_SNIPPET = "sectionsnippet"
    """Adds the title of the matching section with highlighting."""

    IS_FILE_MATCH = "isfilematch"
    """Adds a boolean indicating if the search matched file content."""

    CATEGORY_SNIPPET = "categorysnippet"
    """Adds the matching category name with highlighting."""

    SCORE = "score"
    """Relevance score (deprecated upstream, ignored)."""

    HAS_RELATED = "hasrelated"
    """Has related suggestions (deprecated upstream, ignored)."""

    EXTENSION_DATA = "extensiondata"
    """Adds extra data generated by extensions."""


class SearchInfo(Enum):
    """Metadata values for search query methods.

    This enum is used by the ``search`` method in both sync and async
    clients to specify which metadata to include in search results.

    **Usage Example:**

    .. code-block:: python

        from wikipediaapi import SearchInfo, WikiSearchInfo

        # Using enum members (type-safe)
        results = wiki.search("python", info=[SearchInfo.TOTAL_HITS, SearchInfo.SUGGESTION])

        # Using strings (backward compatible)
        results = wiki.search("python", info=["totalhits", "suggestion"])

        # Accessing metadata from results
        print(f"Total hits: {results.totalhits}")
        print(f"Suggestion: {results.suggestion}")
    """

    REWRITTEN_QUERY = "rewrittenquery"
    """The rewritten/normalized search query used by the engine."""

    SUGGESTION = "suggestion"
    """Spelling suggestion for alternative search terms."""

    TOTAL_HITS = "totalhits"
    """Total number of matches found for the search query."""


#: Type alias for search property arguments accepted throughout the library.
#: Accepts either a :class:`SearchProp` enum member or a raw ``str``,
#: e.g. ``SearchProp.SIZE`` or simply ``"size"``.
WikiSearchProp = Union[SearchProp, str]


#: Type alias for search info arguments accepted throughout the library.
#: Accepts either a :class:`SearchInfo` enum member or a raw ``str``,
#: e.g. ``SearchInfo.TOTAL_HITS`` or simply ``"totalhits"``.
WikiSearchInfo = Union[SearchInfo, str]


def search_prop2str(prop: WikiSearchProp) -> str:
    """
    Convert a :class:`WikiSearchProp` value to a plain ``str``.

    If *prop* is a :class:`SearchProp` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    This converter is used internally by the library to handle both enum
    and string inputs gracefully, providing backward compatibility while
    enabling type-safe usage.

    :param prop: search property to convert
    :return: string representation of the search property

    **Examples:**

    .. code-block:: python

        from wikipediaapi import search_prop2str, SearchProp

        # Convert enum to string
        assert search_prop2str(SearchProp.SIZE) == "size"
        assert search_prop2str(SearchProp.WORDCOUNT) == "wordcount"

        # String pass-through (unchanged)
        assert search_prop2str("size") == "size"
        assert search_prop2str("wordcount") == "wordcount"

        # Custom values pass through
        assert search_prop2str("custom_prop") == "custom_prop"
    """
    if isinstance(prop, SearchProp):
        return prop.value

    return prop


def search_info2str(info: WikiSearchInfo) -> str:
    """
    Convert a :class:`WikiSearchInfo` value to a plain ``str``.

    If *info* is a :class:`SearchInfo` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    This converter is used internally by the library to handle both enum
    and string inputs gracefully, providing backward compatibility while
    enabling type-safe usage.

    :param info: search info to convert
    :return: string representation of the search info

    **Examples:**

    .. code-block:: python

        from wikipediaapi import search_info2str, SearchInfo

        # Convert enum to string
        assert search_info2str(SearchInfo.TOTAL_HITS) == "totalhits"
        assert search_info2str(SearchInfo.SUGGESTION) == "suggestion"

        # String pass-through (unchanged)
        assert search_info2str("totalhits") == "totalhits"
        assert search_info2str("suggestion") == "suggestion"

        # Custom values pass through
        assert search_info2str("custom_info") == "custom_info"
    """
    if isinstance(info, SearchInfo):
        return info.value

    return info


class SearchWhat(Enum):
    """Search type values for search query methods.

    This enum is used by the ``search`` method in both sync and async
    clients to specify which type of search to perform.

    **Usage Example:**

    .. code-block:: python

        from wikipediaapi import SearchWhat, WikiSearchWhat

        # Full-text search (default)
        results = wiki.search("python", what=SearchWhat.TEXT)

        # Title-only search (faster)
        results = wiki.search("python", what=SearchWhat.TITLE)

        # Near match for typos
        results = wiki.search("pythn", what=SearchWhat.NEAR_MATCH)

        # In function signatures
        def search_function(query: str, what: WikiSearchWhat) -> SearchResults:
            return wiki.search(query, what=what)
    """

    NEAR_MATCH = "nearmatch"
    """Near match search (finds pages with similar titles)."""

    TEXT = "text"
    """Search page text content (default, full-text search)."""

    TITLE = "title"
    """Search page titles only (faster, title-only matching)."""


class SearchQiProfile(Enum):
    """Query-independent profile values for search query methods.

    This enum is used by the ``search`` method in both sync and async
    clients to specify the query-independent ranking profile to use.

    **Usage Example:**

    .. code-block:: python

        from wikipediaapi import SearchQiProfile, WikiSearchQiProfile

        # Let engine choose best profile (default)
        results = wiki.search("python", qi_profile=SearchQiProfile.ENGINE_AUTO_SELECT)

        # Classic ranking
        results = wiki.search("python", qi_profile=SearchQiProfile.CLASSIC)

        # Machine learning ranking
        results = wiki.search("python", qi_profile=SearchQiProfile.MLR_1024RS)

        # Prioritize popular pages
        results = wiki.search("python", qi_profile=SearchQiProfile.POPULAR_INCLINKS)

        # In function signatures
        def search_function(query: str, qi_profile: WikiSearchQiProfile) -> SearchResults:
            return wiki.search(query, qi_profile=qi_profile)
    """

    CLASSIC = "classic"
    """Classic ranking profile based on traditional factors."""

    CLASSIC_NO_BOOST_LINKS = "classic_noboostlinks"
    """Classic ranking without link boost factors."""

    EMPTY = "empty"
    """Empty profile (debug only, no ranking applied)."""

    ENGINE_AUTO_SELECT = "engine_autoselect"
    """Let the search engine automatically select the best profile (default)."""

    GROWTH_UNDERLINKED = "growth_underlinked"
    """Prioritize underlinked articles for growth."""

    MLR_1024RS = "mlr-1024rs"
    """Machine learning ranking model (1024 features)."""

    MLR_1024RS_NEXT = "mlr-1024rs-next"
    """Next generation machine learning ranking model."""

    POPULAR_INCLINKS = "popular_inclinks"
    """Prioritize popular pages with many incoming links."""

    POPULAR_INCLINKS_PV = "popular_inclinks_pv"
    """Prioritize popular pages with pageviews and links."""

    WSUM_INCLINKS = "wsum_inclinks"
    """Weighted sum of incoming links."""

    WSUM_INCLINKS_PV = "wsum_inclinks_pv"
    """Weighted sum of links and pageviews."""


#: Type alias for search what arguments accepted throughout the library.
#: Accepts either a :class:`SearchWhat` enum member or a raw ``str``,
#: e.g. ``SearchWhat.TEXT`` or simply ``"text"``.
WikiSearchWhat = Union[SearchWhat, str]


#: Type alias for search qi profile arguments accepted throughout the library.
#: Accepts either a :class:`SearchQiProfile` enum member or a raw ``str``,
#: e.g. ``SearchQiProfile.ENGINE_AUTO_SELECT`` or simply ``"engine_autoselect"``.
WikiSearchQiProfile = Union[SearchQiProfile, str]


def search_what2str(what: WikiSearchWhat) -> str:
    """
    Convert a :class:`WikiSearchWhat` value to a plain ``str``.

    If *what* is a :class:`SearchWhat` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    This converter is used internally by the library to handle both enum
    and string inputs gracefully, providing backward compatibility while
    enabling type-safe usage.

    :param what: search what to convert
    :return: string representation of the search what

    **Examples:**

    .. code-block:: python

        from wikipediaapi import search_what2str, SearchWhat

        # Convert enum to string
        assert search_what2str(SearchWhat.TEXT) == "text"
        assert search_what2str(SearchWhat.TITLE) == "title"

        # String pass-through (unchanged)
        assert search_what2str("text") == "text"
        assert search_what2str("title") == "title"

        # Custom values pass through
        assert search_what2str("custom_what") == "custom_what"
    """
    if isinstance(what, SearchWhat):
        return what.value

    return what


def search_qi_profile2str(qi_profile: WikiSearchQiProfile) -> str:
    """
    Convert a :class:`WikiSearchQiProfile` value to a plain ``str``.

    If *qi_profile* is a :class:`SearchQiProfile` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    This converter is used internally by the library to handle both enum
    and string inputs gracefully, providing backward compatibility while
    enabling type-safe usage.

    :param qi_profile: search qi profile to convert
    :return: string representation of the search qi profile

    **Examples:**

    .. code-block:: python

        from wikipediaapi import search_qi_profile2str, SearchQiProfile

        # Convert enum to string
        assert search_qi_profile2str(SearchQiProfile.ENGINE_AUTO_SELECT) == "engine_autoselect"
        assert search_qi_profile2str(SearchQiProfile.CLASSIC) == "classic"

        # String pass-through (unchanged)
        assert search_qi_profile2str("engine_autoselect") == "engine_autoselect"
        assert search_qi_profile2str("classic") == "classic"

        # Custom values pass through
        assert search_qi_profile2str("custom_profile") == "custom_profile"
    """
    if isinstance(qi_profile, SearchQiProfile):
        return qi_profile.value

    return qi_profile
