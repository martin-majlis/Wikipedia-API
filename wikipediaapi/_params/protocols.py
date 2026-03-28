"""Protocol for objects with title attribute."""

from typing import Protocol


class _HasTitle(Protocol):
    @property
    def title(self) -> str: ...
