"""Mixin providing the to_api() and cache_key() methods.

Subclasses must define PREFIX and FIELD_MAP class attributes.
"""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any
from typing import ClassVar
from typing import cast


class _BaseParams:
    """Mixin providing the ``to_api()`` and ``cache_key()`` methods.

    Subclasses must define ``PREFIX`` and ``FIELD_MAP`` class attributes.

    Invariants:
        - ``PREFIX`` is MediaWiki module prefix (e.g. ``"co"``).
        - ``FIELD_MAP`` maps Python field names to MW suffixes
          (e.g. ``{"limit": "limit", "distance_from_point": "distancefrompoint"}``).
    """

    PREFIX: ClassVar[str] = ""
    FIELD_MAP: ClassVar[dict[str, str]] = {}  # Class variable, not instance variable

    def to_api(self) -> dict[str, str]:
        """Convert clean Python params to prefixed MediaWiki API params.

        Iterates over ``FIELD_MAP``, reads the corresponding attribute
        value, and emits ``{PREFIX}{suffix}: str(value)`` for every
        non-None field.  Boolean ``False`` values are skipped.

        Returns:
            Dictionary of ``{api_param_name: string_value}`` pairs ready
            to merge into an API request.
        """
        result: dict[str, str] = {}
        for field_name, api_suffix in self.FIELD_MAP.items():
            val = getattr(self, field_name)
            if val is None:
                continue
            if isinstance(val, bool):
                if val:
                    result[f"{self.PREFIX}{api_suffix}"] = "1"
                continue
            if isinstance(val, Enum):
                result[f"{self.PREFIX}{api_suffix}"] = str(val.value)
                continue
            result[f"{self.PREFIX}{api_suffix}"] = str(val)
        return result

    def cache_key(self) -> tuple[tuple[str, Any], ...]:
        """Return a hashable key representing this parameter set.

        Used by per-param cache on page objects to distinguish
        results fetched with different parameters.

        Returns:
            Tuple of ``(field_name, value)`` pairs, sorted by field name.
        """
        return tuple(sorted((f.name, getattr(self, f.name)) for f in fields(cast(Any, self))))
