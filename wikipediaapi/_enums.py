"""Shared enum definitions for Wikipedia API options."""

from enum import Enum
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
