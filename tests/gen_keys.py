#!/usr/bin/env python3
"""Helper script to generate mock data keys for new API endpoints."""

import sys

sys.path.insert(0, "/Users/martin.majlis/development/Wikipedia-API")

from wikipediaapi._params import (
    CoordinatesParams,  # noqa: E402
    GeoSearchParams,  # noqa: E402
    ImagesParams,  # noqa: E402
    RandomParams,  # noqa: E402
    SearchParams,  # noqa: E402
)
from wikipediaapi._types import GeoPoint  # noqa: E402


def gen_key(language, base_params, param_obj):
    """Generate a mock data key from language, base params, and a param object."""
    params = dict(base_params)
    params.update(param_obj.to_api())
    params["format"] = "json"
    params["redirects"] = 1
    query = ""
    for k in sorted(params.keys()):
        query += k + "=" + str(params[k]) + "&"
    return language + ":" + query


# Coordinates (default)
print("COORDS DEFAULT:")
print(
    gen_key(
        "en", {"action": "query", "prop": "coordinates", "titles": "Test_1"}, CoordinatesParams()
    )
)

# Coordinates (primary=all)
print("\nCOORDS ALL:")
print(
    gen_key(
        "en",
        {"action": "query", "prop": "coordinates", "titles": "Test_1"},
        CoordinatesParams(primary="all"),
    )
)

# Coordinates (NonExistent)
print("\nCOORDS NONEXISTENT:")
print(
    gen_key(
        "en",
        {"action": "query", "prop": "coordinates", "titles": "NonExistent"},
        CoordinatesParams(),
    )
)

# Images
print("\nIMAGES:")
print(gen_key("en", {"action": "query", "prop": "images", "titles": "Test_1"}, ImagesParams()))

# Images (NonExistent)
print("\nIMAGES NONEXISTENT:")
print(gen_key("en", {"action": "query", "prop": "images", "titles": "NonExistent"}, ImagesParams()))

# Geosearch
print("\nGEOSEARCH:")
print(
    gen_key(
        "en",
        {"action": "query", "list": "geosearch"},
        GeoSearchParams(coord=GeoPoint(51.5074, -0.1278)),
    )
)

# Random
print("\nRANDOM:")
print(gen_key("en", {"action": "query", "list": "random"}, RandomParams(limit=2)))

# Search
print("\nSEARCH:")
print(
    gen_key(
        "en",
        {"action": "query", "list": "search"},
        SearchParams(query="Python", namespace=0, limit=10, sort="relevance"),
    )
)
