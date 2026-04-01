"""Batch-capable page dictionaries for sync and async contexts.

Replaces former ``PagesDict = dict[str, WikipediaPage]`` type alias
with a proper ``dict`` subclass that carries a back-reference to wiki
client and exposes batch-fetching methods for new query submodules.

Backward compatible: ``PagesDict`` subclasses ``dict``, so all existing
code that treats it as a plain dict continues to work.
"""

# Import classes for export and internal use
from .async_images_dict import AsyncImagesDict  # noqa: F401
from .async_pages_dict import AsyncPagesDict  # noqa: F401
from .base_pages_dict import _AsyncBatchWiki  # noqa: F401 - Internal protocol
from .base_pages_dict import _AsyncImageWiki  # noqa: F401 - Internal protocol
from .base_pages_dict import _SyncBatchWiki  # noqa: F401 - Internal protocol
from .base_pages_dict import _SyncImageWiki  # noqa: F401 - Internal protocol
from .images_dict import ImagesDict  # noqa: F401
from .pages_dict import PagesDict  # noqa: F401

__all__ = [
    "PagesDict",
    "AsyncPagesDict",
    "ImagesDict",
    "AsyncImagesDict",
]
