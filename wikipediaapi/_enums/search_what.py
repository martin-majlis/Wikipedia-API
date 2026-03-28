"""Search type values for search query methods.

This enum is used by the ``search`` method in both sync and async
clients to specify which type of search to perform.
"""

from enum import Enum
from typing import Union


class SearchWhat(Enum):
    """Search type values for search query methods.

    This enum is used by the ``search`` method in both sync and async
    clients to specify which type of search to perform.
    """

    NEAR_MATCH = "nearmatch"
    """Near match for typos (finds pages with similar titles)."""
    TEXT = "text"
    """Search page text content (default, full-text search)."""
    TITLE = "title"
    """Search page titles only (asterisk, title-only matching)."""


#: Type alias for search what arguments.
#: Accepts either a :class:`SearchWhat` enum member or a raw ``str``.
#: e.g. ``SearchWhat.TEXT`` or simply ``"text"``.
WikiSearchWhat = Union[SearchWhat, str]


def search_what2str(what: WikiSearchWhat) -> str:
    """
    Convert a :class:`WikiSearchWhat` value to a plain ``str``.

    If *what* is a :class:`SearchWhat` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    :param what: search what to convert
    :return: string representation of the search what

    **Examples:**

    .. code-block:: python

        from wikipediaapi import search_what2str, SearchWhat

        # Convert enum to string
        assert search_what2str(SearchWhat.NEAR_MATCH) == "nearmatch"
        assert search_what2str(SearchWhat.TEXT) == "text"
        assert search_what2str(SearchWhat.TITLE) == "title"

        # String pass-through (unchanged)
        assert search_what2str("nearmatch") == "nearmatch"
        assert search_what2str("text") == "text"
        assert search_what2str("title") == "title"

        # Custom values pass through
        assert search_what2str("custom") == "custom"
    """
    if isinstance(what, SearchWhat):
        return what.value

    return what
