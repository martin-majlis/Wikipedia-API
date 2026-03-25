"""Shared enum definitions for Wikipedia API options."""

from enum import Enum


class Direction(Enum):
    """Sort direction values for image query methods.

    This enum is used by ``images`` and ``batch_images`` methods in both
    sync and async APIs.
    """

    ASCENDING = "ascending"
    DESCENDING = "descending"
