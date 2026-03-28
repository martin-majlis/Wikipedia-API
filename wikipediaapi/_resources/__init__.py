"""Resource classes for Wikipedia API operations.

This module contains the core resource classes that provide the Wikipedia API
functionality for both synchronous and asynchronous operations.
"""

from .async_wikipedia_resource import AsyncWikipediaResource
from .base_wikipedia_resource import BaseWikipediaResource
from .wikipedia_resource import WikipediaResource

__all__ = [
    "BaseWikipediaResource",
    "WikipediaResource",
    "AsyncWikipediaResource",
]
