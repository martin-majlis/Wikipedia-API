"""Tests for async namespace property behavior."""

import pytest

from tests.mock_data import user_agent
import wikipediaapi


class TestAsyncNamespaceBehavior:
    """Test that async namespace property fetches from API like pageid."""

    @pytest.fixture
    async def wiki(self):
        """Create async Wikipedia client for testing."""
        return wikipediaapi.AsyncWikipedia(user_agent, "en")

    async def test_category_namespace_fetched_from_api(self, wiki):
        """Test that category pages have correct namespace fetched from API."""
        page = wiki.page("Category:foo")

        # The ns property should return construction-time value initially
        ns = page.ns
        assert ns == 0  # Initial value

        # Trigger extracts API which also populates namespace
        await page.summary
        ns = page.ns
        assert ns == 14

        # Test alias
        namespace = page.namespace
        assert namespace == 14

        # Verify API was called
        assert page._called["extracts"] is True

    async def test_main_namespace_fetched_from_api(self, wiki):
        """Test that main article pages have correct namespace fetched from API."""
        page = wiki.page("Python_(programming_language)")

        # The ns property should return construction-time value initially
        ns = page.ns
        assert ns == 0  # Initial value

        # Trigger extracts API which also populates namespace
        await page.summary
        ns = page.ns
        assert ns == 0

        # Test alias
        namespace = page.namespace
        assert namespace == 0

        # Verify API was called
        assert page._called["extracts"] is True

    async def test_namespace_consistency_after_api_calls(self, wiki):
        """Test that namespace remains consistent after various API calls."""
        page = wiki.page("Category:foo")

        # Get initial namespace
        initial_ns = page.ns
        assert initial_ns == 0

        # Make extracts API call to update namespace
        await page.summary

        # Make other API calls
        _ = await page.pageid

        # Namespace should remain consistent
        assert page.ns == 14
        assert page.namespace == 14

    async def test_namespace_triggers_api_only_once(self, wiki):
        """Test that accessing ns multiple times only triggers API once."""
        page = wiki.page("Category:foo")

        # First access should return initial value
        ns1 = page.ns
        assert ns1 == 0

        # Trigger extracts API
        await page.summary
        assert page._called["extracts"] is True

        # Second access should use updated value
        ns2 = page.ns
        assert ns2 == 14
        assert ns1 != ns2  # Value changed after API call

    async def test_namespace_vs_pageid_behavior(self, wiki):
        """Test that namespace and pageid have similar behavior."""
        # Fresh page for ns test
        page_ns = wiki.page("Category:foo")
        await page_ns.summary

        # Fresh page for pageid test
        page_pageid = wiki.page("Category:foo")
        _ = await page_pageid.pageid

        # Both should trigger API calls
        assert page_ns._called["extracts"] is True
        assert page_pageid._called["info"] is True

        # Both should have correct namespace
        assert page_ns.ns == 14
        assert page_pageid.ns == 14

    async def test_namespace_for_nonexistent_page(self, wiki):
        """Test namespace behavior for non-existent pages."""
        page = wiki.page("NonExistentPage12345")

        # Should return construction-time value initially
        ns = page.ns
        assert ns == 0

        # Trigger extracts API
        await page.summary
        ns = page.ns
        assert isinstance(ns, int)
        assert page._called["extracts"] is True

        # Page should not exist
        exists = await page.exists()
        assert exists is False
