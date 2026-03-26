"""Shared enum definitions for Wikipedia API options."""

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
    """Coordinate types for coordinates and geosearch methods."""

    ALL = "all"
    PRIMARY = "primary"
    SECONDARY = "secondary"


#: Type alias for primary coordinate arguments.
#: Accepts either a :class:`CoordinateType` enum member or a raw ``str``.
WikiCoordinateType = Union[CoordinateType, str]


def coordinate_type2str(ctype: WikiCoordinateType) -> str:
    """
    Convert a :class:`WikiCoordinateType` value to a plain ``str``.

    :param ctype: coordinate type to convert
    :return: string representation of the coordinate type
    """
    if isinstance(ctype, CoordinateType):
        return ctype.value

    return ctype


class CoordinatesProp(Enum):
    """Property values for coordinates query methods.

    This enum is used by ``coordinates`` and ``batch_coordinates`` methods in both
    sync and async APIs to specify which additional coordinate properties
    to return from the MediaWiki API.
    """

    COUNTRY = "country"
    DIM = "dim"
    GLOBE = "globe"
    NAME = "name"
    REGION = "region"
    TYPE = "type"


#: Type alias for coordinates property arguments accepted throughout the library.
#: Accepts either a :class:`CoordinatesProp` enum member or a raw ``str``,
#: e.g. ``CoordinatesProp.GLOBE`` or simply ``"globe"``.
WikiCoordinatesProp = Union[CoordinatesProp, str]


def coordinates_prop2str(prop: WikiCoordinatesProp) -> str:
    """
    Convert a :class:`WikiCoordinatesProp` value to a plain ``str``.

    If *prop* is a :class:`CoordinatesProp` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    :param prop: coordinates property to convert
    :return: string representation of the coordinates property
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
