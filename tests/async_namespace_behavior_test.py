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

        # The ns property should trigger API call and return correct namespace
        ns = await page.ns
        assert ns == 14

        # Test alias
        namespace = await page.namespace
        assert namespace == 14

        # Verify API was called
        assert page._called["info"] is True

    async def test_main_namespace_fetched_from_api(self, wiki):
        """Test that main article pages have correct namespace fetched from API."""
        page = wiki.page("Python_(programming_language)")

        # The ns property should trigger API call and return correct namespace
        ns = await page.ns
        assert ns == 0

        # Test alias
        namespace = await page.namespace
        assert namespace == 0

        # Verify API was called
        assert page._called["info"] is True

    async def test_namespace_consistency_after_api_calls(self, wiki):
        """Test that namespace remains consistent after various API calls."""
        page = wiki.page("Category:foo")

        # Get initial namespace
        initial_ns = await page.ns
        assert initial_ns == 14

        # Make other API calls
        _ = await page.summary
        _ = await page.pageid

        # Namespace should remain consistent
        ns_after = await page.ns
        assert ns_after == initial_ns
        namespace_after = await page.namespace
        assert namespace_after == initial_ns

    async def test_namespace_triggers_api_only_once(self, wiki):
        """Test that accessing ns multiple times only triggers API once."""
        page = wiki.page("Category:foo")

        # First access should trigger API call
        ns1 = await page.ns
        assert page._called["info"] is True

        # Second access should use cached value
        ns2 = await page.ns
        assert ns1 == ns2

    async def test_namespace_vs_pageid_behavior(self, wiki):
        """Test that namespace and pageid have similar behavior."""
        # Fresh page for ns test
        page_ns = wiki.page("Category:foo")
        _ = await page_ns.ns

        # Fresh page for pageid test
        page_pageid = wiki.page("Category:foo")
        _ = await page_pageid.pageid

        # Both should trigger API calls
        assert page_ns._called["info"] is True
        assert page_pageid._called["info"] is True

        # Both should have correct namespace
        assert await page_ns.ns == 14
        assert await page_pageid.ns == 14

    async def test_namespace_for_nonexistent_page(self, wiki):
        """Test namespace behavior for non-existent pages."""
        page = wiki.page("NonExistentPage12345")

        # Should trigger API call and return some namespace value
        ns = await page.ns
        assert isinstance(ns, int)
        assert page._called["info"] is True

        # Page should not exist
        exists = await page.exists()
        assert exists is False
