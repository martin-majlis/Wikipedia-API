"""Base exception for Wikipedia-API errors.

This module contains the base exception class that all other Wikipedia-API
exceptions inherit from, providing a common ancestor for error handling.
"""


class WikipediaException(Exception):
    """
    Base exception for all Wikipedia-API errors.

    All library-specific exceptions inherit from this class, so callers
    can catch every possible error with a single ``except`` clause::

        try:
            page = wiki.page("Python")
            print(page.summary)
        except wikipediaapi.WikipediaException as e:
            print(f"Wikipedia error: {e}")
    """
