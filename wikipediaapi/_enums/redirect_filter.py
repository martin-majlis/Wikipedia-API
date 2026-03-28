"""Filter redirect values for methods like random.

This enum is used by ``random`` and ``batch_random`` methods
in both sync and async APIs.
"""

from enum import Enum
from typing import Union


class RedirectFilter(Enum):
    """Filter redirect values for methods like random.

    This enum is used by ``random`` and ``batch_random`` methods
    in both sync and async APIs.
    """

    ALL = "all"
    NONREDIRECTS = "nonredirects"
    REDIRECTS = "redirects"


#: Type alias for redirect filter arguments.
#: Accepts either a :class:`RedirectFilter` enum member or a raw ``str``.
#: e.g. ``RedirectFilter.NONREDIRECTS`` or simply ``"nonredirects"``.
WikiRedirectFilter = Union[RedirectFilter, str]


def redirect_filter2str(rfilter: WikiRedirectFilter) -> str:
    """
    Convert a :class:`WikiRedirectFilter` value to a plain ``str``.

    If *rfilter* is a :class:`RedirectFilter` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    :param rfilter: redirect filter to convert
    :return: string representation of the redirect filter

    **Examples:**

    .. code-block:: python

        from wikipediaapi import redirect_filter2str, RedirectFilter

        # Convert enum to string
        assert redirect_filter2str(RedirectFilter.ALL) == "all"
        assert redirect_filter2str(RedirectFilter.NONREDIRECTS) == "nonredirects"
        assert redirect_filter2str(RedirectFilter.REDIRECTS) == "redirects"

        # String pass-through (unchanged)
        assert redirect_filter2str("all") == "all"
        assert redirect_filter2str("nonredirects") == "nonredirects"
        assert redirect_filter2str("redirects") == "redirects"

        # Custom values pass through
        assert redirect_filter2str("custom") == "custom"
    """
    if isinstance(rfilter, RedirectFilter):
        return rfilter.value

    return rfilter
