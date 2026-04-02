"""Parameters for list=search (prefix sr).

Args:
    query: Search string (required).
    namespace: Namespace to search in.
    limit: Maximum results to return (1–500).
    prop: Properties as an iterable (deprecated upstream).
    info: Metadata as an iterable
        (e.g. [SearchInfo.TOTAL_HITS, SearchInfo.SUGGESTION, SearchInfo.REWRITTEN_QUERY]).
    sort: Sort order (e.g. "relevance", "last_edit_desc").
    what: Search type: "title", "text", or "nearmatch".
    interwiki: Include interwiki results.
    enable_rewrites: Allow backend to rewrite query.
    qi_profile: Query-independent ranking profile.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import ClassVar

from .._enums import Namespace
from .._enums import SearchQiProfile
from .._enums import SearchSort
from .._enums import SearchWhat
from .._enums import WikiNamespace
from .._enums import WikiSearchInfo
from .._enums import WikiSearchProp
from .._enums import WikiSearchQiProfile
from .._enums import WikiSearchSort
from .._enums import WikiSearchWhat
from .._enums import search_info2str
from .._enums import search_prop2str
from .._enums import search_qi_profile2str
from .._enums import search_sort2str
from .._enums import search_what2str
from .base_params import _BaseParams


@dataclass(frozen=True)
class SearchParams(_BaseParams):
    """Parameters for ``list=search`` (prefix ``sr``).

    Args:
        query: Search string (required).
        namespace: Namespace to search in.
        limit: Maximum results to return (1–500).
        prop: Properties as an iterable (deprecated upstream).
        info: Metadata as an iterable
            (e.g. ``[SearchInfo.TOTAL_HITS, SearchInfo.SUGGESTION, SearchInfo.REWRITTEN_QUERY]``).
        sort: Sort order (e.g. ``"relevance"``, ``"last_edit_desc"``).
        what: Search type: ``"title"``, ``"text"``, or ``"nearmatch"``.
        interwiki: Include interwiki results.
        enable_rewrites: Allow backend to rewrite query.
        qi_profile: Query-independent ranking profile.
    """

    query: str = ""
    namespace: WikiNamespace = Namespace.MAIN
    limit: int = 10
    prop: Iterable[WikiSearchProp] | None = None
    info: Iterable[WikiSearchInfo] | None = None
    sort: WikiSearchSort = SearchSort.RELEVANCE
    what: WikiSearchWhat | None = None
    interwiki: bool = False
    enable_rewrites: bool = False
    qi_profile: WikiSearchQiProfile | None = None

    def __post_init__(self) -> None:
        """Normalize iterable search properties and reject string input.

        Converts iterable ``prop`` and ``info`` values into MediaWiki-required
        pipe-separated string representations when provided. Also converts
        enum values for sort, what, and qi_profile parameters.

        Raises:
            TypeError: If ``prop`` or ``info`` is passed as a string instead
                of an iterable.
        """
        if not isinstance(self.sort, (SearchSort, str)):
            raise TypeError("SearchParams.sort must be SearchSort or str")
        object.__setattr__(self, "sort", search_sort2str(self.sort))

        if self.what is not None:
            if not isinstance(self.what, (SearchWhat, str)):
                raise TypeError("SearchParams.what must be SearchWhat or str")
            object.__setattr__(self, "what", search_what2str(self.what))

        if self.qi_profile is not None:
            if not isinstance(self.qi_profile, (SearchQiProfile, str)):
                raise TypeError("SearchParams.qi_profile must be SearchQiProfile or str")
            object.__setattr__(self, "qi_profile", search_qi_profile2str(self.qi_profile))

        if self.prop is not None:
            if isinstance(self.prop, str):
                raise TypeError("SearchParams.prop must be an iterable of WikiSearchProp, not str")
            converted_props = [search_prop2str(p) for p in self.prop]
            object.__setattr__(self, "prop", "|".join(converted_props))
        if self.info is not None:
            if isinstance(self.info, str):
                raise TypeError("SearchParams.info must be an iterable of WikiSearchInfo, not str")
            converted_info = [search_info2str(i) for i in self.info]
            object.__setattr__(self, "info", "|".join(converted_info))

    PREFIX: ClassVar[str] = "sr"
    FIELD_MAP: ClassVar[dict[str, str]] = {
        "query": "search",
        "namespace": "namespace",
        "limit": "limit",
        "prop": "prop",
        "info": "info",
        "sort": "sort",
        "what": "what",
        "interwiki": "interwiki",
        "enable_rewrites": "enablerewrites",
        "qi_profile": "qiprofile",
    }
