"""Wrapper for search results combining pages with aggregate metadata.

Returned by ``wiki.search()``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._pages_dict import PagesDict


@dataclass
class SearchResults:
    """Wrapper for search results combining pages with aggregate metadata.

    Returned by ``wiki.search()``.  The ``pages`` attribute is a
    :class:`~wikipediaapi.PagesDict` keyed by title; each
    page carries a :class:`SearchMeta` sub-object accessible via
    ``page.search_meta``.

    Args:
        pages: Dictionary of matching pages keyed by title.
        totalhits: Total number of matches reported by the API.
        suggestion: Spelling suggestion from search backend, or None.
    """

    pages: PagesDict
    totalhits: int = 0
    suggestion: str | None = None
