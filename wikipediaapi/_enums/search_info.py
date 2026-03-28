"""Metadata values for search query methods.

This enum is used by the ``search`` method in both sync and async
clients to specify which metadata to include in search results.
"""

from enum import Enum
from typing import Union


class SearchInfo(Enum):
    """Metadata values for search query methods.

    This enum is used by the ``search`` method in both sync and async
    clients to specify which metadata to include in search results.
    """

    REWRITTEN_QUERY = "rewrittenquery"
    """The rewritten/normalized search query used by the engine."""
    SUGGESTION = "suggestion"
    """Spelling suggestion for alternative search terms."""
    TOTAL_HITS = "totalhits"
    """Total number of matches found for the search query."""


#: Type alias for search info arguments.
#: Accepts either a :class:`SearchInfo` enum member or a raw ``str``.
#: e.g. ``SearchInfo.TOTAL_HITS`` or simply ``"totalhits"``.
WikiSearchInfo = Union[SearchInfo, str]


def search_info2str(info: WikiSearchInfo) -> str:
    """
    Convert a :class:`WikiSearchInfo` value to a plain ``str``.

    If *info* is a :class:`SearchInfo` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    :param info: search info to convert
    :return: string representation of the search info

    **Examples:**

    .. code-block:: python

        from wikipediaapi import search_info2str, SearchInfo

        # Convert enum to string
        assert search_info2str(SearchInfo.REWRITTEN_QUERY) == "rewrittenquery"
        assert search_info2str(SearchInfo.SUGGESTION) == "suggestion"
        assert search_info2str(SearchInfo.TOTAL_HITS) == "totalhits"

        # String pass-through (unchanged)
        assert search_info2str("rewrittenquery") == "rewrittenquery"
        assert search_info2str("suggestion") == "suggestion"
        assert search_info2str("totalhits") == "totalhits"

        # Custom values pass through
        assert search_info2str("custom") == "custom"
    """
    if isinstance(info, SearchInfo):
        return info.value

    return info
