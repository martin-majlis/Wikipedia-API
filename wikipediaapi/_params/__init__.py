"""Internal parameter dataclasses for MediaWiki query submodules.

Each dataclass maps clean Python parameter names to their MediaWiki
API equivalents (which use module-specific prefixes like co, gs, im, rn, sr).
The to_api method produces a dict ready to merge into an API request.

These classes are **not** part of the public API; they are used internally
by _resources.py to convert explicit method signatures into API params.
"""

# Import classes for use by tests and resource modules
from .base_params import _BaseParams  # noqa: F401
from .coordinates_params import CoordinatesParams  # noqa: F401
from .geo_search_params import GeoSearchParams  # noqa: F401
from .imageinfo_params import ImageInfoParams  # noqa: F401
from .images_params import ImagesParams  # noqa: F401
from .protocols import _HasTitle  # noqa: F401
from .random_params import RandomParams  # noqa: F401
from .search_params import SearchParams  # noqa: F401

# No __all__ - these are internal classes not meant for export
