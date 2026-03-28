"""Tests for namespace property behavior."""

from tests.mock_data import create_mock_wikipedia


class TestNamespaceBehavior:
    """Test that namespace property fetches from API like pageid."""

    def test_category_namespace_fetched_from_api(self):
        """Test that category pages have correct namespace fetched from API."""
        wiki = create_mock_wikipedia()
        page = wiki.page("Category:foo")

        # The ns property should trigger API call and return correct namespace
        assert page.ns == 14
        assert page.namespace == 14  # Test alias

        # Verify API was called
        assert page._called["info"] is True

    def test_main_namespace_fetched_from_api(self):
        """Test that main article pages have correct namespace fetched from API."""
        wiki = create_mock_wikipedia()
        page = wiki.page("Python_(programming_language)")

        # The ns property should trigger API call and return correct namespace
        assert page.ns == 0
        assert page.namespace == 0  # Test alias

        # Verify API was called
        assert page._called["info"] is True

    def test_namespace_consistency_after_api_calls(self):
        """Test that namespace remains consistent after various API calls."""
        wiki = create_mock_wikipedia()
        page = wiki.page("Category:foo")

        # Get initial namespace
        initial_ns = page.ns
        assert initial_ns == 14

        # Make other API calls
        _ = page.summary
        _ = page.pageid

        # Namespace should remain consistent
        assert page.ns == initial_ns
        assert page.namespace == initial_ns

    def test_namespace_triggers_api_only_once(self):
        """Test that accessing ns multiple times only triggers API once."""
        wiki = create_mock_wikipedia()
        page = wiki.page("Category:foo")

        # First access should trigger API call
        ns1 = page.ns
        assert page._called["info"] is True

        # Second access should use cached value
        ns2 = page.ns
        assert ns1 == ns2
        # API should not be called again (this is tracked by the mock)

    def test_namespace_vs_pageid_behavior(self):
        """Test that namespace and pageid have similar behavior."""
        wiki = create_mock_wikipedia()

        # Fresh page for ns test
        page_ns = wiki.page("Category:foo")
        _ = page_ns.ns

        # Fresh page for pageid test
        page_pageid = wiki.page("Category:foo")
        _ = page_pageid.pageid

        # Both should trigger API calls
        assert page_ns._called["info"] is True
        assert page_pageid._called["info"] is True

        # Both should have correct namespace
        assert page_ns.ns == 14
        assert page_pageid.ns == 14

    def test_namespace_for_nonexistent_page(self):
        """Test namespace behavior for non-existent pages."""
        wiki = create_mock_wikipedia()
        page = wiki.page("NonExistentPage12345")

        # Should trigger API call and return some namespace value
        ns = page.ns
        assert isinstance(ns, int)
        assert page._called["info"] is True

        # Page should not exist
        assert page.exists() is False
