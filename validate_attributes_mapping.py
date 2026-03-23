#!/usr/bin/env python3
"""
Validate that all properties in WikipediaPage and AsyncWikipediaPage are properly defined and tracked.

This script systematically tests property access patterns to ensure internal tracking

This script systematically tests property access patterns to ensure internal tracking
(_called flags and _attributes population) matches documented ATTRIBUTES_MAPPING.

This script systematically tests property access patterns to ensure internal tracking
(_called flags and _attributes population) matches documented ATTRIBUTES_MAPPING.

## Usage Examples

# Basic validation (clean output, default test pages):
uv run python validate_attributes_mapping.py

# Test specific pages:
uv run python validate_attributes_mapping.py --pages en:Python de:Berlin

# Enable HTTP cache debugging:
uv run python validate_attributes_mapping.py --cache-debug

# Test specific pages with cache debugging:
uv run python validate_attributes_mapping.py --cache-debug --pages en:Python

# Store output to timestamped log file:
# uv run python validate_attributes_mapping.py 2>&1 | \
#   tee validate_attributes_mapping_$(date +%Y%m%d_%H%M%S).out

## What the Script Tests

1. **Property Discovery**: Uses dir() to find all accessible properties on
   WikipediaPage and AsyncWikipediaPage
2. **API Call Tracking**: Monitors which internal API calls (info, extracts,
   langlinks, etc.) are triggered by each property access
3. **Attribute Population**: Tracks which keys are added to the internal
   _attributes dictionary
4. **Mapping Validation**: Compares observed behavior against the documented
   ATTRIBUTES_MAPPING
5. **HTTP Caching**: Implements caching at the HTTP level to prevent duplicate
   network requests

## Exit Codes

- **0**: All validations passed
- **1**: Validation failures detected (missing properties, attribute mismatches, or mapping issues)

## Output

The script provides:
- Console summary of validation results
- Detailed JSON report with complete test results
- Cache statistics showing HTTP request efficiency
- Specific error reporting for any mismatches found
"""

import argparse
import asyncio
from collections.abc import Callable
import json
import sys
from typing import Any

import wikipediaapi
from wikipediaapi._http_client import AsyncHTTPClient
from wikipediaapi._http_client import SyncHTTPClient

# Global cache to prevent duplicate HTTP requests
_http_cache: dict[str, Any] = {}

# Global flag for cache debugging
_cache_debug = False

# Attributes that should not be accessed during testing
IGNORED_ATTRIBUTES = {
    "ATTRIBUTES_MAPPING",  # Class-level constant
    "wiki",  # Parent client instance
    "sections_by_title",  # Method requiring parameters
    "section_by_title",  # Method requiring parameters
    "exists",  # Method requiring no parameters but complex logic
    "langlinks",  # Property that returns a dict, not page details
    "links",  # Property that returns a dict, not page details
    "backlinks",  # Property that returns a dict, not page details
    "categories",  # Property that returns a dict, not page details
    "categorymembers",  # Property that returns a dict, not page details
}


def create_cache_key(url: str, params: dict[str, Any]) -> str:
    """Create a consistent cache key from URL and parameters.



    Generates a SHA256 hash based on the URL and sorted parameters to ensure
    consistent cache key generation regardless of parameter order.

    Args:
        url: The base URL for the request.
        params: Dictionary of query parameters to include in the cache key.

    Returns:

        A SHA256 hash string that uniquely represents the URL and
        parameters.

    Invariants:
        - Same URL and parameters will always generate the same cache key
        - Parameter order does not affect the generated key
        - Generated keys are safe for use as dictionary keys
    """
    import hashlib
    import json

    # Sort params to ensure consistent key generation
    sorted_params = json.dumps(dict(sorted(params.items())), sort_keys=True)
    key_content = f"{url}?{sorted_params}"
    return hashlib.sha256(key_content.encode()).hexdigest()


def cached_sync_do_get(original_do_get: Callable):  # type: ignore[no-any-return]
    """Create a cached wrapper for synchronous HTTP client requests.

    Wraps the original SyncHTTPClient._do_get method to add caching at the HTTP
    level, preventing duplicate network requests for the same URL and parameters.

    Args:
        original_do_get: The original _do_get method to wrap.

    Returns:
        A wrapper function that provides caching functionality.

    Invariants:
        - Cache is thread-safe for read operations
        - Cache keys are consistent regardless of parameter order
        - Original method behavior is preserved for cache misses
        - Debug output is controlled by global _cache_debug flag
    """

    def wrapper(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        cache_key = create_cache_key(url, params)

        if cache_key not in _http_cache:
            result: dict[str, Any] = original_do_get(self, url, params)
            _http_cache[cache_key] = result
            if _cache_debug:
                print(f"SYNC HTTP CACHE MISS: {url}")
                print(f"  Params: {params}")
                print(f"  Cache key: {cache_key}")
        else:
            if _cache_debug:
                print(f"SYNC HTTP CACHE HIT: {url}")
                print(f"  Params: {params}")
                print(f"  Cache key: {cache_key}")

        return _http_cache[cache_key]  # type: ignore[no-any-return]

    return wrapper


def cached_async_do_get(original_do_get: Callable):  # type: ignore[no-any-return]
    """Create a cached wrapper for asynchronous HTTP client requests.

    Wraps the original AsyncHTTPClient._do_get method to add caching at the HTTP
    level, preventing duplicate network requests for the same URL and parameters.

    Args:
        original_do_get: The original async _do_get method to wrap.

    Returns:
        An async wrapper function that provides caching functionality.

    Invariants:
        - Cache is thread-safe for read operations
        - Cache keys are consistent regardless of parameter order
        - Original method behavior is preserved for cache misses
        - Debug output is controlled by global _cache_debug flag
        - Wrapper maintains async/await compatibility
    """

    async def wrapper(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        cache_key = create_cache_key(url, params)

        if cache_key not in _http_cache:
            result: dict[str, Any] = await original_do_get(self, url, params)
            _http_cache[cache_key] = result
            if _cache_debug:
                print(f"ASYNC HTTP CACHE MISS: {url}")
                print(f"  Params: {params}")
                print(f"  Cache key: {cache_key}")
        else:
            if _cache_debug:
                print(f"ASYNC HTTP CACHE HIT: {url}")
                print(f"  Params: {params}")
                print(f"  Cache key: {cache_key}")

        return _http_cache[cache_key]  # type: ignore[no-any-return]

    return wrapper


def patch_http_clients() -> tuple[Callable, Callable]:
    """Patch HTTP clients to add caching at the _do_get level.

    Replaces the original _do_get methods in both SyncHTTPClient and
    AsyncHTTPClient with cached wrapper functions to enable HTTP-level caching
    during validation testing.

    Returns:
        A tuple containing (original_sync_do_get, original_async_do_get)
        for later restoration.

    Invariants:
        - Original methods are preserved for restoration
        - Both sync and async clients are patched consistently
        - Patching is reversible using restore_http_clients
    """
    # Patch sync client
    original_sync_do_get = SyncHTTPClient._do_get
    setattr(SyncHTTPClient, "_do_get", cached_sync_do_get(original_sync_do_get))

    # Patch async client
    original_async_do_get = AsyncHTTPClient._do_get
    setattr(AsyncHTTPClient, "_do_get", cached_async_do_get(original_async_do_get))

    return original_sync_do_get, original_async_do_get


def restore_http_clients(original_sync_do_get: Callable, original_async_do_get: Callable) -> None:
    """Restore the original HTTP client methods.

    Restores the original _do_get methods in both SyncHTTPClient and
    AsyncHTTPClient, removing the caching wrapper functions.

    Args:
        original_sync_do_get: The original synchronous _do_get method.
        original_async_do_get: The original asynchronous _do_get method.

    Invariants:
        - Complete restoration of original functionality
        - No cached data is preserved during restoration
        - Both clients are restored to their initial state
    """
    setattr(SyncHTTPClient, "_do_get", original_sync_do_get)
    setattr(AsyncHTTPClient, "_do_get", original_async_do_get)


def get_wiki(language: str, is_async: bool = False) -> Any:
    """Get a Wikipedia client configured for validation testing.

    Creates either a synchronous or asynchronous Wikipedia client with a
    specific user agent for validation purposes. HTTP-level caching is handled
    by the patched client methods.

    Args:
        language: The Wikipedia language code (e.g., 'en', 'de', 'fr').
        is_async: Whether to return an AsyncWikipedia client (True) or
            synchronous Wikipedia client (False).

    Returns:
        A Wikipedia or AsyncWikipedia client instance configured for testing.

    Invariants:
        - Client uses a consistent user agent for identification
        - Client language is set according to the parameter
        - Returned client type matches the is_async parameter
    """
    if is_async:
        return wikipediaapi.AsyncWikipedia(
            user_agent="Attribute-Mapping-Validator/1.0 (test@example.com)", language=language
        )
    else:
        return wikipediaapi.Wikipedia(
            user_agent="Attribute-Mapping-Validator/1.0 (test@example.com)", language=language
        )


def get_test_pages() -> list[tuple[str, str]]:
    """Return a diverse list of test pages for comprehensive validation.

    Provides a curated set of Wikipedia pages covering different languages,
    content types, and namespaces to ensure thorough testing of property
    mapping across various scenarios.

    Returns:
        A list of (language, page_name) tuples for testing.

    Invariants:
        - Includes multiple languages (English, German, French, Chinese, Spanish)
        - Contains both articles and category pages
        - Covers different content complexity levels
        - All pages are expected to exist and be accessible
    """
    return [
        ("en", "Python_(programming_language)"),  # Main article with rich content
        ("de", "Berlin"),  # Non-English article
        ("fr", "Paris"),  # Another non-English article
        ("en", "Category:Physics"),  # Category page (different namespace)
        ("zh", "Python"),  # Chinese language with variants
        ("es", "Inteligencia_artificial"),  # Spanish article
    ]


def get_discoverable_attributes(obj: Any) -> list[str]:
    """Get all public, non-private attributes from an object using dir().

    Filters the result of dir() to return only attributes that are suitable
    for testing, excluding private attributes, dunder methods, and internal
    implementation details.

    Args:
        obj: The object to inspect for discoverable attributes.

    Returns:
        A list of attribute names that are public and testable.

    Invariants:
        - Excludes all attributes starting with underscore
        - Excludes all dunder methods (starting and ending with double underscore)
        - Returns only attributes that can be safely accessed during testing
        - Result order follows dir() output order
    """
    return [
        attr
        for attr in dir(obj)
        if not attr.startswith("_") and not attr.startswith("__") and not attr.endswith("__")
    ]


def test_sync_page(language: str, page_name: str) -> dict[str, dict[str, Any]]:
    """Test synchronous WikipediaPage properties and track attribute population.

    Systematically tests each discoverable property on a synchronous WikipediaPage
    to determine which internal API calls are triggered and which attributes are
    populated in the internal _attributes dictionary.

    Args:
        language: The Wikipedia language code for the test.
        page_name: The name of the Wikipedia page to test.

    Returns:
        A dictionary mapping property names to test results including changed_calls,
        new_attributes, value_type, and error information if applicable.

    Invariants:
        - Each property is tested with a fresh page instance
        - Internal state is captured before and after property access
        - Results include both successful and failed property accesses
        - Test isolation ensures no cross-contamination between properties
    """
    wiki = get_wiki(language, is_async=False)

    results: dict[str, dict[str, Any]] = {}

    # Get all discoverable attributes
    attributes = get_discoverable_attributes(wikipediaapi.WikipediaPage(wiki, page_name))

    for attr_name in attributes:
        # Skip ignored attributes
        if attr_name in IGNORED_ATTRIBUTES:
            continue

        try:
            # Create fresh page for each test to ensure clean state
            page = wiki.page(page_name)

            # Capture state before access
            before_called = page._called.copy()
            before_attributes = set(page._attributes.keys())

            # Access attribute
            value = getattr(page, attr_name)

            # Capture state after access
            after_called = page._called.copy()
            after_attributes = set(page._attributes.keys())

            # Find which _called flags changed
            changed_calls = []
            for call_key, before_val in before_called.items():
                if before_val != after_called[call_key]:
                    changed_calls.append(call_key)

            # Find which attributes were added
            added_attributes: set[str] = after_attributes - before_attributes

            results[attr_name] = {
                "changed_calls": changed_calls,
                "new_attributes": list(added_attributes),
                "value_type": type(value).__name__ if value is not None else "None",
            }

        except Exception as e:
            results[attr_name] = {"error": str(e), "error_type": type(e).__name__}

    return results


async def test_async_page(language: str, page_name: str) -> dict[str, dict[str, Any]]:
    """Test asynchronous AsyncWikipediaPage properties and track attribute population.

    Systematically tests each discoverable property on an asynchronous WikipediaPage
    to determine which internal API calls are triggered and which attributes are
    populated in the internal _attributes dictionary. Handles both regular and
    coroutine properties appropriately.

    Args:
        language: The Wikipedia language code for the test.
        page_name: The name of the Wikipedia page to test.

    Returns:
        A dictionary mapping property names to test results including changed_calls,
        new_attributes, value_type, and error information if applicable.

    Invariants:
        - Each property is tested with a fresh page instance
        - Internal state is captured before and after property access
        - Coroutine properties are properly awaited before state capture
        - Results include both successful and failed property accesses
        - Test isolation ensures no cross-contamination between properties
    """
    wiki = get_wiki(language, is_async=True)

    results: dict[str, dict[str, Any]] = {}

    # Get all discoverable attributes
    attributes = get_discoverable_attributes(wikipediaapi.AsyncWikipediaPage(wiki, page_name))

    for attr_name in attributes:
        # Skip ignored attributes
        if attr_name in IGNORED_ATTRIBUTES:
            continue

        try:
            # Create fresh page for each test to ensure clean state
            page = wiki.page(page_name)

            # Capture state before access
            before_called = page._called.copy()
            before_attributes = set(page._attributes.keys())

            # Access attribute (handle both regular and coroutine properties)
            value = getattr(page, attr_name)

            # If it's awaitable, await it
            if asyncio.iscoroutine(value):
                value = await value

            # Capture state after access
            after_called = page._called.copy()
            after_attributes = set(page._attributes.keys())

            # Find which _called flags changed
            changed_calls = []
            for call_key, before_val in before_called.items():
                if before_val != after_called[call_key]:
                    changed_calls.append(call_key)

            # Find which attributes were added
            added_attributes: set[str] = after_attributes - before_attributes

            results[attr_name] = {
                "changed_calls": changed_calls,
                "new_attributes": list(added_attributes),
                "value_type": type(value).__name__ if value is not None else "None",
            }

        except Exception as e:
            results[attr_name] = {"error": str(e), "error_type": type(e).__name__}

    return results


def compare_with_reference(
    test_results: dict[str, Any], reference_mapping: dict[str, list[str]]
) -> dict[str, Any]:
    """Compare test results with the documented ATTRIBUTES_MAPPING reference.

    Analyzes the differences between observed property behavior during testing
    and the expected behavior documented in ATTRIBUTES_MAPPING to identify mismatches,
    missing properties, and unexpected behaviors.

    Args:
        test_results: Results from test_sync_page or test_async_page containing
            observed property behavior and attribute population.
        reference_mapping: The documented ATTRIBUTES_MAPPING from BaseWikipediaPage
            containing expected API calls for each property.

    Returns:
        A comprehensive comparison dictionary including missing_properties,
        missing_from_mapping, attribute_mismatches, and detailed analysis.

    Invariants:
        - All properties in test_results are analyzed against reference_mapping
        - Mismatches are categorized by type (missing, unexpected, mismatched calls)
        - Reference mapping is preserved unchanged in the results
        - Results are structured for easy programmatic analysis
    """
    comparison: dict[str, Any] = {
        "reference_mapping": reference_mapping,
        "test_results": test_results,
        "mismatches": {},
        "missing_properties": [],
        "extra_properties": [],
        "attribute_mismatches": {},
    }

    # Find missing and extra properties
    test_properties = set(test_results.keys())
    reference_properties = set(reference_mapping.keys())

    # Properties that are documented in ATTRIBUTES_MAPPING but missing from test results
    missing_props: list[str] = list(reference_properties - test_properties)
    comparison["missing_properties"] = missing_props

    # Properties that exist in test results but are missing from ATTRIBUTES_MAPPING
    missing_from_mapping: list[str] = list(test_properties - reference_properties)
    comparison["missing_from_mapping"] = missing_from_mapping

    # Compare attribute mappings for common properties
    common_properties = test_properties & reference_properties

    mismatches: dict[str, Any] = comparison["attribute_mismatches"]
    for prop in common_properties:
        if "error" in test_results[prop]:
            mismatches[prop] = {
                "status": "error",
                "error": test_results[prop]["error"],
            }
            continue

        test_calls: set[str] = set(test_results[prop]["changed_calls"])
        ref_calls: set[str] = set(reference_mapping[prop])

        # Check if test calls match any of expected calls
        # This handles the case where multiple API calls can populate the same attribute
        if not test_calls.intersection(ref_calls) and ref_calls:
            mismatches[prop] = {
                "status": "mismatch",
                "expected_calls": list(ref_calls),
                "actual_calls": list(test_calls),
                "new_attributes": test_results[prop]["new_attributes"],
            }
        elif test_calls and not ref_calls:
            # Property triggers API calls but shouldn't according to mapping
            mismatches[prop] = {
                "status": "unexpected_calls",
                "expected_calls": list(ref_calls),
                "actual_calls": list(test_calls),
                "new_attributes": test_results[prop]["new_attributes"],
            }

    return comparison


def parse_arguments() -> argparse.Namespace:
    """Parse and validate command line arguments for the validation script.

    Sets up argument parsing with support for cache debugging and custom page
    selection. Provides help messages and validates argument formats.

    Returns:
        An argparse.Namespace object containing the parsed command line arguments.

    Invariants:
        - Cache debug flag defaults to False
        - Pages argument defaults to empty list (use default test pages)
        - Help messages are provided for all options
        - Invalid arguments are handled by argparse with appropriate error messages
    """
    parser = argparse.ArgumentParser(
        description="Validate that all properties in WikipediaPage and"
        " AsyncWikipediaPage are properly defined"
    )
    parser.add_argument(
        "--cache-debug",
        action="store_true",
        help="Enable HTTP cache debugging output (default: disabled)",
    )
    parser.add_argument(
        "--pages",
        nargs="*",
        default=[],
        help="Specific pages to test in format 'language:page_name' (e.g., 'en:Python')",
    )
    return parser.parse_args()


async def main() -> int:
    """Execute the complete attribute mapping validation workflow.

    Orchestrates the entire validation process including HTTP client patching,
    testing both sync and async pages, comparing results with the reference
    mapping, and generating comprehensive reports. Handles cleanup and error recovery.

    Returns:
        Exit code (0 for success, 1 for validation failures).

    Raises:
        Exception: Propagates unexpected errors during validation.

    Invariants:
        - HTTP clients are always restored even if errors occur
        - Global cache debug flag is properly managed
        - Both sync and async tests are executed when possible
        - Results are always printed in JSON format for analysis
        - Cache statistics are reported regardless of validation outcome
    """
    args = parse_arguments()

    # Set global cache debug flag
    global _cache_debug
    _cache_debug = args.cache_debug

    print("Starting attribute mapping validation...")
    if _cache_debug:
        print("HTTP cache debugging ENABLED")
    else:
        print("HTTP cache debugging DISABLED")

    # Patch HTTP clients to add caching at the _do_get level
    original_sync_do_get, original_async_do_get = patch_http_clients()
    print("HTTP clients patched with caching at _do_get level")

    try:
        # Get reference mapping
        reference_mapping = wikipediaapi.WikipediaPage.ATTRIBUTES_MAPPING

        # Get test pages (use command line pages if provided, otherwise defaults)
        test_pages = get_test_pages()
        if args.pages:
            # Parse custom pages from command line
            custom_pages = []
            for page_spec in args.pages:
                if ":" in page_spec:
                    language, page_name = page_spec.split(":", 1)
                    custom_pages.append((language, page_name))
                else:
                    print(
                        f"Warning: Invalid page format '{page_spec}', expected 'language:page_name'"
                    )
            if custom_pages:
                test_pages = custom_pages

        print(f"Testing {len(test_pages)} pages")

        all_sync_results: dict[str, Any] = {}
        all_async_results: dict[str, Any] = {}

        # Test sync pages
        print("\n=== Testing Sync Pages ===")
        for language, page_name in test_pages:
            print(f"Testing {language}:{page_name}")
            try:
                results = test_sync_page(language, page_name)
                all_sync_results[f"{language}:{page_name}"] = results  # type: ignore[assignment]
            except Exception as e:
                print(f"Error testing {language}:{page_name}: {e}")
                all_sync_results[f"{language}:{page_name}"] = {
                    "error": str(e)
                }  # type: ignore[dict-item]

        # Test async pages
        print("\n=== Testing Async Pages ===")
        for language, page_name in test_pages:
            print(f"Testing {language}:{page_name}")
            try:
                results = await test_async_page(language, page_name)
                all_async_results[f"{language}:{page_name}"] = results  # type: ignore[assignment]
            except Exception as e:
                print(f"Error testing {language}:{page_name}: {e}")
                all_async_results[f"{language}:{page_name}"] = {
                    "error": str(e)
                }  # type: ignore[dict-item]

        # Compare results with reference
        print("\n=== Comparing with Reference ===")

        # Use first successful sync result for comparison
        sync_comparison = None
        for _page_key, results in all_sync_results.items():
            if "error" not in results:
                sync_comparison = compare_with_reference(results, reference_mapping)
                break

        # Use first successful async result for comparison
        async_comparison = None
        for _page_key, results in all_async_results.items():
            if "error" not in results:
                async_comparison = compare_with_reference(results, reference_mapping)
                break

        # Generate final report
        report = {
            "sync_comparison": sync_comparison,
            "async_comparison": async_comparison,
            "all_sync_results": all_sync_results,
            "all_async_results": all_async_results,
        }

        # Print results as JSON
        print("\n=== Validation Report ===")
        print(json.dumps(report, indent=2, default=str))

        # Check for mismatches
        has_mismatches = False

        if sync_comparison:
            missing_count = len(sync_comparison["missing_properties"])
            missing_from_mapping_count = len(sync_comparison["missing_from_mapping"])
            mismatch_count = len(sync_comparison["attribute_mismatches"])

            if missing_count > 0 or missing_from_mapping_count > 0 or mismatch_count > 0:
                has_mismatches = True
                print("\n❌ Sync validation FAILED")
                if missing_count > 0:
                    print(f"Missing properties: {sync_comparison['missing_properties']}")
                if missing_from_mapping_count > 0:
                    print(
                        "Properties missing from ATTRIBUTES_MAPPING: "
                        f"{sync_comparison['missing_from_mapping']}"
                    )
                if mismatch_count > 0:
                    print(f"Attribute mismatches: {mismatch_count}")
                    for prop, details in sync_comparison["attribute_mismatches"].items():
                        print(f"  - {prop}: {details['status']}")
                        print(f"    Expected: {details['expected_calls']}")
                        print(f"    Actual: {details['actual_calls']}")

        if async_comparison:
            missing_count = len(async_comparison["missing_properties"])
            missing_from_mapping_count = len(async_comparison["missing_from_mapping"])
            mismatch_count = len(async_comparison["attribute_mismatches"])

            if missing_count > 0 or missing_from_mapping_count > 0 or mismatch_count > 0:
                has_mismatches = True
                print("\n❌ Async validation FAILED")
                if missing_count > 0:
                    print(f"Missing properties: {async_comparison['missing_properties']}")
                if missing_from_mapping_count > 0:
                    print(
                        "Properties missing from ATTRIBUTES_MAPPING: "
                        f"{async_comparison['missing_from_mapping']}"
                    )
                if mismatch_count > 0:
                    print(f"Attribute mismatches: {mismatch_count}")
                    for prop, details in async_comparison["attribute_mismatches"].items():
                        print(f"  - {prop}: {details['status']}")
                        print(f"    Expected: {details['expected_calls']}")
                        print(f"    Actual: {details['actual_calls']}")

        if not has_mismatches:
            print("\n✅ All validations PASSED")
        else:
            print("\n📋 Summary:")
            print(
                f"   - Found "
                f"{len(sync_comparison['attribute_mismatches']) if sync_comparison else 0} sync "
                f"attribute mismatches"
            )
            print(
                f"   - Found "
                f"{len(async_comparison['attribute_mismatches']) if async_comparison else 0} async "
                f"attribute mismatches"
            )
            print("   - These appear to be issues in ATTRIBUTES_MAPPING itself")

            print("\n📊 Cache Statistics:")
            print(f"   - HTTP cache entries: {len(_http_cache)}")

            return 1 if has_mismatches else 0

    finally:
        # Restore original HTTP client methods
        restore_http_clients(original_sync_do_get, original_async_do_get)
        print("HTTP clients restored to original state")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
