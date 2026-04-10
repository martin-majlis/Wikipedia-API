"""Common base for WikipediaImage and AsyncWikipediaImage."""

import hashlib
from typing import Any

from .._page._base_wikipedia_page import BaseWikipediaPage


class BaseWikipediaImage(BaseWikipediaPage[Any]):
    """Shared logic for sync and async file-page representations.

    Holds image-specific helpers that are identical in both
    :class:`~wikipediaapi.WikipediaImage` and
    :class:`~wikipediaapi.AsyncWikipediaImage`.
    """

    def _compute_base_pageid(self) -> int:
        """Compute a deterministic page ID from the title using SHA-256.

        :return: a large positive integer derived from the title
        """
        return int(hashlib.sha256(self.title.encode("utf-8")).hexdigest(), 16) % (10**18)

    def _get_pageid(self) -> int:
        """Return a title-based page ID whose sign reflects existence.

        Reads ``pageid`` and ``known`` from the already-populated
        ``_attributes`` cache (no network call is made here).

        :return: positive integer if the file exists, negative otherwise
        """
        exists = int(self._attributes.get("pageid", -1)) > 0 or "known" in self._attributes
        base = self._compute_base_pageid()
        return base if exists else -base
