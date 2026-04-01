"""Parameters for prop=imageinfo (prefix ii).

Args:
    prop: Properties to retrieve (iterable of strings, e.g. ``("url", "size")``).
    limit: Maximum number of revisions to return (1–500).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .base_params import _BaseParams

_DEFAULT_PROP: tuple[str, ...] = ("url", "size", "mime", "mediatype", "sha1", "timestamp", "user")


@dataclass(frozen=True)
class ImageInfoParams(_BaseParams):
    """Parameters for ``prop=imageinfo`` (prefix ``ii``).

    Args:
        prop: Tuple of ``iiprop`` field names controlling which metadata
            fields are returned.  Defaults to the standard set of fields.
            Strings are rejected at construction time (raises ``TypeError``).
        limit: Maximum number of file revisions to return (1–500).
    """

    prop: tuple[str, ...] = _DEFAULT_PROP
    limit: int = 1

    PREFIX: ClassVar[str] = "ii"
    FIELD_MAP: ClassVar[dict[str, str]] = {
        "limit": "limit",
    }

    def __post_init__(self) -> None:
        """Validate that prop is not a bare string."""
        if isinstance(self.prop, str):
            raise TypeError(
                "ImageInfoParams.prop must be an iterable of strings, not a str. "
                "Use a tuple or list, e.g. ('url', 'size')."
            )

    def to_api(self) -> dict[str, str]:
        """Convert params to prefixed MediaWiki API params.

        Overrides the base implementation to handle the ``prop`` tuple
        (joined with ``|``) in addition to the standard scalar fields.

        Returns:
            Dictionary of ``{api_param_name: string_value}`` pairs ready
            to merge into an API request.
        """
        result = super().to_api()
        if self.prop:
            result["iiprop"] = "|".join(self.prop)
        return result
