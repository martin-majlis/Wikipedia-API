"""Contextual metadata attached to pages returned by a search query.

Accessible via ``page.search_meta`` on pages produced by
``wiki.search()``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchMeta:
    """Contextual metadata attached to pages returned by a search query.

    Accessible via ``page.search_meta`` on pages produced by
    ``wiki.search()``.  Contains search-specific fields like
    highlighted snippet.

    Args:
        snippet: HTML snippet with query-term highlighting.
        size: Page size in bytes.
        wordcount: Word count of page.
        timestamp: ISO 8601 timestamp of last edit.
    """

    snippet: str = ""
    size: int = 0
    wordcount: int = 0
    timestamp: str = ""
