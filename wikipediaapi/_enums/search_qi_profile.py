"""Query-independent profile values for search query methods.

This enum is used by the ``search`` method in both sync and async
clients to specify the query-independent ranking profile to use.
"""

from enum import Enum
from typing import Union


class SearchQiProfile(Enum):
    """Query-independent profile values for search query methods.

    This enum is used by the ``search`` method in both sync and async
    clients to specify the query-independent ranking profile to use.
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
    """Weighted sum of links and pageviews for popular pages."""
    WSUM_INCLINKS = "wsum_inclinks"
    """Weighted sum of links and pageviews."""
    WSUM_INCLINKS_PV = "wsum_inclinks_pv"
    """Weighted sum of links and pageviews (alternative version)."""


#: Type alias for search qi profile arguments.
#: Accepts either a :class:`SearchQiProfile` enum member or a raw ``str``.
#: e.g. ``SearchQiProfile.ENGINE_AUTO_SELECT`` or simply ``"engine_autoselect"``.
WikiSearchQiProfile = Union[SearchQiProfile, str]


def search_qi_profile2str(qi_profile: WikiSearchQiProfile) -> str:
    """
    Convert a :class:`WikiSearchQiProfile` value to a plain ``str``.

    If *qi_profile* is a :class:`SearchQiProfile` enum member its string value
    is returned.  If it is already a ``str`` it is returned unchanged.

    :param qi_profile: search qi profile to convert
    :return: string representation of the search qi profile

    **Examples:**

    .. code-block:: python

        from wikipediaapi import search_qi_profile2str, SearchQiProfile

        # Convert enum to string
        assert search_qi_profile2str(SearchQiProfile.CLASSIC) == "classic"
        assert search_qi_profile2str(SearchQiProfile.ENGINE_AUTO_SELECT) == "engine_autoselect"

        # String pass-through (unchanged)
        assert search_qi_profile2str("classic") == "classic"
        assert search_qi_profile2str("engine_autoselect") == "engine_autoselect"

        # Custom values pass through
        assert search_qi_profile2str("custom") == "custom"
    """
    if isinstance(qi_profile, SearchQiProfile):
        return qi_profile.value

    return qi_profile
