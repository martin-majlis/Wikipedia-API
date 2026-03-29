"""Shared fixtures for VCR-based integration tests."""

import pytest

import wikipediaapi

VCR_USER_AGENT = (
    "Wikipedia-API-IntegrationTests/1.0"
    " (https://github.com/martin-majlis/Wikipedia-API; bot@example.com)"
)


@pytest.fixture(scope="module")
def vcr_config():
    """Configure VCR cassette recording/replay."""
    return {
        "cassette_library_dir": "tests/cassettes",
        "record_mode": "once",
        "match_on": ["method", "scheme", "host", "port", "path", "query"],
        "decode_compressed_response": True,
        "filter_headers": ["User-Agent", "Accept-Encoding"],
        "serializer": "json",
    }


@pytest.fixture()
def sync_wiki():
    """Create a synchronous Wikipedia client for integration tests."""
    return wikipediaapi.Wikipedia(user_agent=VCR_USER_AGENT, language="en")


@pytest.fixture()
def async_wiki():
    """Create an asynchronous Wikipedia client for integration tests."""
    return wikipediaapi.AsyncWikipedia(user_agent=VCR_USER_AGENT, language="en")
