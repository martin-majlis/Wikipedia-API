"""Tests for the package-level logger ``wikipediaapi.log``.

The README section "How To See Underlying API Call" tells users to configure
``wikipediaapi.log`` (and uses ``wikipediaapi.logging``). These tests make sure
both attributes exist and that messages from the HTTP client modules reach
handlers attached to ``wikipediaapi.log``.
"""

import logging
from collections.abc import Iterator

import pytest

import wikipediaapi
from tests.mock_data import create_mock_async_wikipedia
from tests.mock_data import create_mock_wikipedia


class _ListHandler(logging.Handler):
    """Logging handler that keeps every record in a list for assertions."""

    def __init__(self) -> None:
        """Create the handler with level DEBUG and an empty record list."""
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Store the record.

        Args:
            record: The log record emitted by a logger.
        """
        self.records.append(record)


@pytest.fixture
def package_log_records() -> Iterator[list[logging.LogRecord]]:
    """Attach a handler to ``wikipediaapi.log`` the way the README does.

    Yields:
        The list that collects records reaching the package logger.
    """
    handler = _ListHandler()
    previous_level = wikipediaapi.log.level
    wikipediaapi.log.setLevel(level=wikipediaapi.logging.DEBUG)
    wikipediaapi.log.addHandler(handler)
    try:
        yield handler.records
    finally:
        wikipediaapi.log.removeHandler(handler)
        wikipediaapi.log.setLevel(previous_level)


def test_package_logger_is_exported() -> None:
    """``wikipediaapi.log`` is the logger named after the package."""
    assert wikipediaapi.log is logging.getLogger("wikipediaapi")
    assert wikipediaapi.logging is logging


def test_sync_client_messages_reach_package_logger(
    package_log_records: list[logging.LogRecord],
) -> None:
    """Messages from the sync HTTP client propagate to ``wikipediaapi.log``."""
    create_mock_wikipedia(language="cs")
    messages = [r.getMessage() for r in package_log_records]
    assert any("language=cs" in m for m in messages)
    assert all(r.name.startswith("wikipediaapi.") for r in package_log_records)


def test_async_client_messages_reach_package_logger(
    package_log_records: list[logging.LogRecord],
) -> None:
    """Messages from the async HTTP client propagate to ``wikipediaapi.log``."""
    create_mock_async_wikipedia(language="de")
    messages = [r.getMessage() for r in package_log_records]
    assert any("language=de" in m for m in messages)
