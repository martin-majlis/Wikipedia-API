"""Sort values for search method.

This enum is used by the ``search`` method in both sync and async APIs.
"""

from enum import Enum
from typing import Union


class SearchSort(Enum):
    """Sort values for ``search`` method."""

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
#: e.g. ``SearchSort.RELEVANCE`` or simply ``"relevance"``.
WikiSearchSort = Union[SearchSort, str]


def search_sort2str(sort: WikiSearchSort) -> str:
    """
    Convert a :class:`WikiSearchSort` value to a plain ``str``.

    If *sort* is a :class:`SearchSort` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    :param sort: sort direction to convert
    :return: string representation of the sort direction

    **Examples:**

    .. code-block:: python

        from wikipediaapi import search_sort2str, SearchSort

        # Convert enum to string
        assert search_sort2str(SearchSort.RELEVANCE) == "relevance"

        # String pass-through (unchanged)
        assert search_sort2str("relevance") == "relevance"

        # Custom values pass through
        assert search_sort2str("custom") == "custom"
    """
    if isinstance(sort, SearchSort):
        return sort.value

    return sort
