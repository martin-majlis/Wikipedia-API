"""Parameters for list=random (prefix rn).

Args:
    namespace: Restrict to this namespace number.
    filter_redirect: Redirect filter: "all", "nonredirects", or "redirects".
    min_size: Minimum page size in bytes.
    max_size: Maximum page size in bytes.
    limit: Number of random pages to return (1–500).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .._enums import Namespace
from .._enums import RedirectFilter
from .._enums import WikiNamespace
from .._enums import WikiRedirectFilter
from .._enums import redirect_filter2str
from .base_params import _BaseParams


@dataclass(frozen=True)
class RandomParams(_BaseParams):
    """Parameters for ``list=random`` (prefix ``rn``).

    Args:
        namespace: Restrict to this namespace number.
        filter_redirect: Redirect filter: ``"all"``, ``"nonredirects"``,
            or ``"redirects"``.
        min_size: Minimum page size in bytes.
        max_size: Maximum page size in bytes.
        limit: Number of random pages to return (1–500).
    """

    namespace: WikiNamespace = Namespace.MAIN
    filter_redirect: WikiRedirectFilter = RedirectFilter.NONREDIRECTS
    min_size: int | None = None
    max_size: int | None = None
    limit: int = 1

    def __post_init__(self) -> None:
        """Normalize filter_redirect properly.

        Raises:
            TypeError: If ``filter_redirect`` is not a RedirectFilter or str.
        """
        if not isinstance(self.filter_redirect, (RedirectFilter, str)):
            raise TypeError("RandomParams.filter_redirect must be RedirectFilter or str")
        object.__setattr__(self, "filter_redirect", redirect_filter2str(self.filter_redirect))

    PREFIX: ClassVar[str] = "rn"
    FIELD_MAP: ClassVar[dict[str, str]] = {
        "namespace": "namespace",
        "filter_redirect": "filterredir",
        "min_size": "minsize",
        "max_size": "maxsize",
        "limit": "limit",
    }
