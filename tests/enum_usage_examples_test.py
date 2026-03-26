"""
Comprehensive tests and examples for enum usage with string and enum inputs.

This module demonstrates how to use the new enum-based API parameters
with both enum members (type-safe) and string values (backward compatibility).
"""

import unittest

from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi
from wikipediaapi._enums import coordinate_type2str
from wikipediaapi._enums import CoordinateType
from wikipediaapi._enums import geosearch_sort2str
from wikipediaapi._enums import GeoSearchSort
from wikipediaapi._enums import Globe
from wikipediaapi._enums import globe2str
from wikipediaapi._enums import redirect_filter2str
from wikipediaapi._enums import RedirectFilter
from wikipediaapi._enums import search_sort2str
from wikipediaapi._enums import SearchSort
from wikipediaapi._enums import WikiCoordinateType
from wikipediaapi._enums import WikiGeoSearchSort
from wikipediaapi._enums import WikiGlobe
from wikipediaapi._enums import WikiRedirectFilter
from wikipediaapi._enums import WikiSearchSort
from wikipediaapi._types import GeoPoint


class TestEnumUsageExamples(unittest.TestCase):
    """Test cases demonstrating enum usage patterns."""

    def setUp(self):
        """Set up test fixtures."""
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)
        self.test_point = GeoPoint(lat=51.5074, lon=-0.1278)  # London coordinates

    def test_coordinate_type_converter_examples(self):
        """Test CoordinateType converter with various inputs."""
        print("\n=== CoordinateType Converter Examples ===")

        # Enum inputs (type-safe)
        examples = [
            (CoordinateType.ALL, "all"),
            (CoordinateType.PRIMARY, "primary"),
            (CoordinateType.SECONDARY, "secondary"),
        ]

        for enum_val, expected_str in examples:
            result = coordinate_type2str(enum_val)
            print(f"  coordinate_type2str({enum_val}) -> '{result}'")
            self.assertEqual(result, expected_str)

        # String inputs (backward compatibility)
        string_examples = ["all", "primary", "secondary", "custom"]
        for string_val in string_examples:
            result = coordinate_type2str(string_val)
            print(f"  coordinate_type2str('{string_val}') -> '{result}'")
            self.assertEqual(result, string_val)

    def test_globe_converter_examples(self):
        """Test Globe converter with various inputs."""
        print("\n=== Globe Converter Examples ===")

        # Enum inputs (type-safe)
        examples = [
            (Globe.EARTH, "earth"),
            (Globe.MARS, "mars"),
            (Globe.MOON, "moon"),
            (Globe.VENUS, "venus"),
        ]

        for enum_val, expected_str in examples:
            result = globe2str(enum_val)
            print(f"  globe2str({enum_val}) -> '{result}'")
            self.assertEqual(result, expected_str)

        # String inputs (backward compatibility)
        string_examples = ["earth", "mars", "moon", "venus", "custom_planet"]
        for string_val in string_examples:
            result = globe2str(string_val)
            print(f"  globe2str('{string_val}') -> '{result}'")
            self.assertEqual(result, string_val)

    def test_search_sort_converter_examples(self):
        """Test SearchSort converter with various inputs."""
        print("\n=== SearchSort Converter Examples ===")

        # Test common enum values
        common_enums = [
            (SearchSort.RELEVANCE, "relevance"),
            (SearchSort.NONE, "none"),
            (SearchSort.RANDOM, "random"),
            (SearchSort.JUST_MATCH, "just_match"),
        ]

        for enum_val, expected_str in common_enums:
            result = search_sort2str(enum_val)
            print(f"  search_sort2str({enum_val}) -> '{result}'")
            self.assertEqual(result, expected_str)

        # Test all enum values
        all_enums = list(SearchSort)
        all_strings = [search_sort2str(enum_val) for enum_val in all_enums]
        print(f"  All SearchSort values: {all_strings}")

        # String inputs (backward compatibility)
        string_examples = ["relevance", "none", "random", "custom_sort"]
        for string_val in string_examples:
            result = search_sort2str(string_val)
            print(f"  search_sort2str('{string_val}') -> '{result}'")
            self.assertEqual(result, string_val)

    def test_geosearch_sort_converter_examples(self):
        """Test GeoSearchSort converter with various inputs."""
        print("\n=== GeoSearchSort Converter Examples ===")

        # Enum inputs (type-safe)
        examples = [
            (GeoSearchSort.DISTANCE, "distance"),
            (GeoSearchSort.RELEVANCE, "relevance"),
        ]

        for enum_val, expected_str in examples:
            result = geosearch_sort2str(enum_val)
            print(f"  geosearch_sort2str({enum_val}) -> '{result}'")
            self.assertEqual(result, expected_str)

        # String inputs (backward compatibility)
        string_examples = ["distance", "relevance", "custom_geo_sort"]
        for string_val in string_examples:
            result = geosearch_sort2str(string_val)
            print(f"  geosearch_sort2str('{string_val}') -> '{result}'")
            self.assertEqual(result, string_val)

    def test_redirect_filter_converter_examples(self):
        """Test RedirectFilter converter with various inputs."""
        print("\n=== RedirectFilter Converter Examples ===")

        # Enum inputs (type-safe)
        examples = [
            (RedirectFilter.ALL, "all"),
            (RedirectFilter.REDIRECTS, "redirects"),
            (RedirectFilter.NONREDIRECTS, "nonredirects"),
        ]

        for enum_val, expected_str in examples:
            result = redirect_filter2str(enum_val)
            print(f"  redirect_filter2str({enum_val}) -> '{result}'")
            self.assertEqual(result, expected_str)

        # String inputs (backward compatibility)
        string_examples = ["all", "redirects", "nonredirects", "custom_filter"]
        for string_val in string_examples:
            result = redirect_filter2str(string_val)
            print(f"  redirect_filter2str('{string_val}') -> '{result}'")
            self.assertEqual(result, string_val)

    @unittest.skip("Skipping actual API calls to avoid network dependency")
    def test_api_usage_with_enums(self):
        """Test actual API usage with enum parameters."""
        print("\n=== API Usage with Enum Parameters ===")
        print("  ⚠️  SKIPPED: This test would make network calls")

    def test_coordinates_api_with_enums(self):
        """Test coordinates API with enum parameters using mock data."""
        print("\n=== Coordinates API with Enum Parameters ===")

        # Get a test page that exists in mock data
        page = self.wiki.page("Test_1")

        # Trigger pageid fetch to ensure page exists() works correctly
        _ = page.pageid
        self.assertTrue(page.exists())

        # Test that we can create CoordinatesParams with enum values
        from wikipediaapi._enums import CoordinatesProp
        from wikipediaapi._enums import CoordinateType
        from wikipediaapi._params import CoordinatesParams

        # Test creating params with enum values
        params_enum = CoordinatesParams(
            limit=5, primary=CoordinateType.ALL, prop=[CoordinatesProp.GLOBE, CoordinatesProp.NAME]
        )
        self.assertEqual(params_enum.limit, 5)
        self.assertEqual(params_enum.prop, "globe|name")  # Converted by __post_init__

        # Test creating params with string values (backward compatibility)
        params_str = CoordinatesParams(limit=5, primary="all", prop=["globe", "name"])
        self.assertEqual(params_str.limit, 5)
        self.assertEqual(params_str.prop, "globe|name")  # Converted by __post_init__

        # Test mixed enum and string values
        params_mixed = CoordinatesParams(
            limit=5,
            primary=CoordinateType.PRIMARY,
            prop=[CoordinatesProp.GLOBE, "name", CoordinatesProp.TYPE],
        )
        self.assertEqual(params_mixed.limit, 5)
        self.assertEqual(params_mixed.prop, "globe|name|type")  # Converted by __post_init__

        print("  ✓ CoordinatesParams handles enum and string values correctly")

    def test_type_alias_examples(self):
        """Test usage of type aliases with both enums and strings."""
        print("\n=== Type Alias Usage Examples ===")

        # These assignments should all be valid
        coord_type_enum: WikiCoordinateType = CoordinateType.PRIMARY
        coord_type_str: WikiCoordinateType = "primary"

        globe_enum: WikiGlobe = Globe.EARTH
        globe_str: WikiGlobe = "earth"

        sort_enum: WikiSearchSort = SearchSort.RELEVANCE
        sort_str: WikiSearchSort = "relevance"

        geo_sort_enum: WikiGeoSearchSort = GeoSearchSort.DISTANCE
        geo_sort_str: WikiGeoSearchSort = "distance"

        filter_enum: WikiRedirectFilter = RedirectFilter.NONREDIRECTS
        filter_str: WikiRedirectFilter = "nonredirects"

        # Test that converters work with type alias inputs
        self.assertEqual(coordinate_type2str(coord_type_enum), "primary")
        self.assertEqual(coordinate_type2str(coord_type_str), "primary")

        self.assertEqual(globe2str(globe_enum), "earth")
        self.assertEqual(globe2str(globe_str), "earth")

        self.assertEqual(search_sort2str(sort_enum), "relevance")
        self.assertEqual(search_sort2str(sort_str), "relevance")

        self.assertEqual(geosearch_sort2str(geo_sort_enum), "distance")
        self.assertEqual(geosearch_sort2str(geo_sort_str), "distance")

        self.assertEqual(redirect_filter2str(filter_enum), "nonredirects")
        self.assertEqual(redirect_filter2str(filter_str), "nonredirects")

        print("  All type alias assignments and conversions work correctly")

    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling."""
        print("\n=== Edge Cases and Error Handling ===")

        # Test with None values (should not be used in practice, but test behavior)
        try:
            result = coordinate_type2str(None)  # type: ignore[arg-type]
            print(f"  coordinate_type2str(None) -> {repr(result)}")
        except (AttributeError, TypeError) as e:
            print(f"  coordinate_type2str(None) raises {type(e).__name__}")

        # Test with empty strings
        self.assertEqual(coordinate_type2str(""), "")
        self.assertEqual(globe2str(""), "")
        self.assertEqual(search_sort2str(""), "")
        self.assertEqual(geosearch_sort2str(""), "")
        self.assertEqual(redirect_filter2str(""), "")
        print("  Correctly handles empty strings")

        # Test with mixed case strings
        self.assertEqual(coordinate_type2str("PRIMARY"), "PRIMARY")
        self.assertEqual(globe2str("EARTH"), "EARTH")
        print("  Preserves string case (as expected)")

        # Test with whitespace strings
        self.assertEqual(coordinate_type2str(" primary "), " primary ")
        self.assertEqual(globe2str(" earth "), " earth ")
        print("  Preserves whitespace in strings")

    def test_comprehensive_enum_coverage(self):
        """Test that all enum values are covered."""
        print("\n=== Comprehensive Enum Coverage ===")

        # Test all CoordinateType values
        for coord_type in CoordinateType:
            result = coordinate_type2str(coord_type)
            self.assertEqual(result, coord_type.value)
        print(f"  All {len(CoordinateType)} CoordinateType values work")

        # Test all Globe values
        for globe in Globe:
            result = globe2str(globe)
            self.assertEqual(result, globe.value)
        print(f"  All {len(Globe)} Globe values work")

        # Test all SearchSort values
        for sort in SearchSort:
            result = search_sort2str(sort)
            self.assertEqual(result, sort.value)
        print(f"  All {len(SearchSort)} SearchSort values work")

        # Test all GeoSearchSort values
        for geo_sort in GeoSearchSort:
            result = geosearch_sort2str(geo_sort)
            self.assertEqual(result, geo_sort.value)
        print(f"  All {len(GeoSearchSort)} GeoSearchSort values work")

        # Test all RedirectFilter values
        for filter_redirect in RedirectFilter:
            result = redirect_filter2str(filter_redirect)
            self.assertEqual(result, filter_redirect.value)
        print(f"  All {len(RedirectFilter)} RedirectFilter values work")


def run_examples():
    """Run the examples as a demonstration."""
    print("🎯 Enum Usage Examples and Tests")
    print("=" * 50)

    # Create test suite and run with verbose output
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnumUsageExamples)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n🎉 All examples and tests passed!")
    else:
        print(f"\n❌ {len(result.failures)} failures, {len(result.errors)} errors")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_examples()
