"""
Unit tests for enum converter edge cases and error handling.

These tests complement the comprehensive usage examples by focusing on
edge cases, error conditions, and boundary testing for the converter functions.
"""

import unittest

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


class TestEnumConvertersEdgeCases(unittest.TestCase):
    """Test edge cases and error handling for enum converter functions."""

    def test_coordinate_type2str_edge_cases(self):
        """Test coordinate_type2str with edge cases."""
        # Test None handling
        result = coordinate_type2str(None)  # type: ignore[arg-type]
        self.assertIsNone(result)

        # Test empty string
        self.assertEqual(coordinate_type2str(""), "")

        # Test whitespace handling
        self.assertEqual(coordinate_type2str(" "), " ")
        self.assertEqual(coordinate_type2str("\tprimary\n"), "\tprimary\n")

        # Test case sensitivity
        self.assertEqual(coordinate_type2str("PRIMARY"), "PRIMARY")
        self.assertEqual(coordinate_type2str("Primary"), "Primary")

        # Test unknown strings (pass-through)
        self.assertEqual(coordinate_type2str("unknown_type"), "unknown_type")
        self.assertEqual(coordinate_type2str("123"), "123")

        # Test all enum values explicitly
        enum_values = [
            (CoordinateType.ALL, "all"),
            (CoordinateType.PRIMARY, "primary"),
            (CoordinateType.SECONDARY, "secondary"),
        ]
        for enum_val, expected in enum_values:
            self.assertEqual(coordinate_type2str(enum_val), expected)

    def test_globe2str_edge_cases(self):
        """Test globe2str with edge cases."""
        # Test None handling
        result = globe2str(None)  # type: ignore[arg-type]
        self.assertIsNone(result)

        # Test empty string
        self.assertEqual(globe2str(""), "")

        # Test whitespace handling
        self.assertEqual(globe2str(" "), " ")
        self.assertEqual(globe2str("\tearth\n"), "\tearth\n")

        # Test case sensitivity
        self.assertEqual(globe2str("EARTH"), "EARTH")
        self.assertEqual(globe2str("Earth"), "Earth")

        # Test unknown strings (pass-through)
        self.assertEqual(globe2str("unknown_planet"), "unknown_planet")
        self.assertEqual(globe2str("pluto"), "pluto")

        # Test all enum values explicitly
        enum_values = [
            (Globe.EARTH, "earth"),
            (Globe.MARS, "mars"),
            (Globe.MOON, "moon"),
            (Globe.VENUS, "venus"),
        ]
        for enum_val, expected in enum_values:
            self.assertEqual(globe2str(enum_val), expected)

    def test_search_sort2str_edge_cases(self):
        """Test search_sort2str with edge cases."""
        # Test None handling
        result = search_sort2str(None)  # type: ignore[arg-type]
        self.assertIsNone(result)

        # Test empty string
        self.assertEqual(search_sort2str(""), "")

        # Test whitespace handling
        self.assertEqual(search_sort2str(" "), " ")
        self.assertEqual(search_sort2str("\trelevance\n"), "\trelevance\n")

        # Test case sensitivity
        self.assertEqual(search_sort2str("RELEVANCE"), "RELEVANCE")
        self.assertEqual(search_sort2str("Relevance"), "Relevance")

        # Test unknown strings (pass-through)
        self.assertEqual(search_sort2str("unknown_sort"), "unknown_sort")
        self.assertEqual(search_sort2str("custom"), "custom")

        # Test all enum values explicitly
        enum_values = [
            (SearchSort.CREATE_TIMESTAMP_ASC, "create_timestamp_asc"),
            (SearchSort.CREATE_TIMESTAMP_DESC, "create_timestamp_desc"),
            (SearchSort.INCOMING_LINKS_ASC, "incoming_links_asc"),
            (SearchSort.INCOMING_LINKS_DESC, "incoming_links_desc"),
            (SearchSort.JUST_MATCH, "just_match"),
            (SearchSort.LAST_EDIT_ASC, "last_edit_asc"),
            (SearchSort.LAST_EDIT_DESC, "last_edit_desc"),
            (SearchSort.NONE, "none"),
            (SearchSort.RANDOM, "random"),
            (SearchSort.RELEVANCE, "relevance"),
            (SearchSort.TITLE_NATURAL_ASC, "title_natural_asc"),
            (SearchSort.TITLE_NATURAL_DESC, "title_natural_desc"),
            (SearchSort.USER_RANDOM, "user_random"),
        ]
        for enum_val, expected in enum_values:
            self.assertEqual(search_sort2str(enum_val), expected)

    def test_geosearch_sort2str_edge_cases(self):
        """Test geosearch_sort2str with edge cases."""
        # Test None handling
        result = geosearch_sort2str(None)  # type: ignore[arg-type]
        self.assertIsNone(result)

        # Test empty string
        self.assertEqual(geosearch_sort2str(""), "")

        # Test whitespace handling
        self.assertEqual(geosearch_sort2str(" "), " ")
        self.assertEqual(geosearch_sort2str("\tdistance\n"), "\tdistance\n")

        # Test case sensitivity
        self.assertEqual(geosearch_sort2str("DISTANCE"), "DISTANCE")
        self.assertEqual(geosearch_sort2str("Distance"), "Distance")

        # Test unknown strings (pass-through)
        self.assertEqual(geosearch_sort2str("unknown_sort"), "unknown_sort")
        self.assertEqual(geosearch_sort2str("custom"), "custom")

        # Test all enum values explicitly
        enum_values = [
            (GeoSearchSort.DISTANCE, "distance"),
            (GeoSearchSort.RELEVANCE, "relevance"),
        ]
        for enum_val, expected in enum_values:
            self.assertEqual(geosearch_sort2str(enum_val), expected)

    def test_redirect_filter2str_edge_cases(self):
        """Test redirect_filter2str with edge cases."""
        # Test None handling
        result = redirect_filter2str(None)  # type: ignore[arg-type]
        self.assertIsNone(result)

        # Test empty string
        self.assertEqual(redirect_filter2str(""), "")

        # Test whitespace handling
        self.assertEqual(redirect_filter2str(" "), " ")
        self.assertEqual(redirect_filter2str("\tall\n"), "\tall\n")

        # Test case sensitivity
        self.assertEqual(redirect_filter2str("ALL"), "ALL")
        self.assertEqual(redirect_filter2str("All"), "All")

        # Test unknown strings (pass-through)
        self.assertEqual(redirect_filter2str("unknown_filter"), "unknown_filter")
        self.assertEqual(redirect_filter2str("custom"), "custom")

        # Test all enum values explicitly
        enum_values = [
            (RedirectFilter.ALL, "all"),
            (RedirectFilter.REDIRECTS, "redirects"),
            (RedirectFilter.NONREDIRECTS, "nonredirects"),
        ]
        for enum_val, expected in enum_values:
            self.assertEqual(redirect_filter2str(enum_val), expected)

    def test_converter_consistency(self):
        """Test that converters are consistent across multiple calls."""
        # Test enum consistency
        enum_inputs = [
            (coordinate_type2str, CoordinateType.PRIMARY),
            (globe2str, Globe.EARTH),
            (search_sort2str, SearchSort.RELEVANCE),
            (geosearch_sort2str, GeoSearchSort.DISTANCE),
            (redirect_filter2str, RedirectFilter.NONREDIRECTS),
        ]

        for converter, enum_val in enum_inputs:
            result1 = converter(enum_val)
            result2 = converter(enum_val)
            self.assertEqual(result1, result2)
            self.assertEqual(result1, enum_val.value)

        # Test string consistency
        string_inputs = [
            (coordinate_type2str, "primary"),
            (globe2str, "earth"),
            (search_sort2str, "relevance"),
            (geosearch_sort2str, "distance"),
            (redirect_filter2str, "nonredirects"),
        ]

        for converter, string_val in string_inputs:
            result1 = converter(string_val)
            result2 = converter(string_val)
            self.assertEqual(result1, result2)
            self.assertEqual(result1, string_val)

    def test_converter_return_types(self):
        """Test that converters always return strings or None."""
        converters_and_enums = [
            (coordinate_type2str, CoordinateType.ALL),
            (globe2str, Globe.EARTH),
            (search_sort2str, SearchSort.RELEVANCE),
            (geosearch_sort2str, GeoSearchSort.DISTANCE),
            (redirect_filter2str, RedirectFilter.ALL),
        ]

        for converter, enum_val in converters_and_enums:
            # Test with enum
            enum_result = converter(enum_val)
            self.assertIsInstance(enum_result, str)

            # Test with string
            string_result = converter("test")
            self.assertIsInstance(string_result, str)

            # Test with None
            none_result = converter(None)  # type: ignore[arg-type]
            self.assertIsNone(none_result)

    def test_converter_performance_basic(self):
        """Basic performance test to ensure converters are not overly slow."""
        import time

        converters = [
            (coordinate_type2str, CoordinateType.PRIMARY),
            (globe2str, Globe.EARTH),
            (search_sort2str, SearchSort.RELEVANCE),
            (geosearch_sort2str, GeoSearchSort.DISTANCE),
            (redirect_filter2str, RedirectFilter.NONREDIRECTS),
        ]

        # Test 1000 conversions each
        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            for converter, enum_val in converters:
                converter(enum_val)
                converter("test_string")

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete in reasonable time (less than 1 second for 10,000 operations)
        self.assertLess(
            total_time,
            1.0,
            f"Converters too slow: {total_time:.3f}s for {iterations * len(converters) * 2} operations",
        )

    def test_enum_value_immutability(self):
        """Test that enum values remain immutable after conversion."""
        # Get original enum values
        original_coord = CoordinateType.PRIMARY
        original_globe = Globe.EARTH
        original_sort = SearchSort.RELEVANCE
        original_geo_sort = GeoSearchSort.DISTANCE
        original_filter = RedirectFilter.NONREDIRECTS

        # Convert them
        coordinate_type2str(original_coord)
        globe2str(original_globe)
        search_sort2str(original_sort)
        geosearch_sort2str(original_geo_sort)
        redirect_filter2str(original_filter)

        # Verify they haven't changed
        self.assertEqual(original_coord.value, "primary")
        self.assertEqual(original_globe.value, "earth")
        self.assertEqual(original_sort.value, "relevance")
        self.assertEqual(original_geo_sort.value, "distance")
        self.assertEqual(original_filter.value, "nonredirects")

    def test_special_characters_in_strings(self):
        """Test converters with special characters in string inputs."""
        special_strings = [
            "test\nwith\nnewlines",
            "test\twith\ttabs",
            "test with spaces",
            "test-with-dashes",
            "test_with_underscores",
            "test.with.dots",
            "test/with/slashes",
            "test\\with\\backslashes",
            "test@with@symbols",
            "test#with#hash",
            "test$with$dollar",
            "test%with%percent",
            "test&with&ampersand",
            "test*with*asterisk",
            "test(with)parentheses",
            "test[with]brackets",
            "test{with}braces",
            "test|with|pipes",
            "test+with+plus",
            "test=with=equals",
        ]

        converters = [
            coordinate_type2str,
            globe2str,
            search_sort2str,
            geosearch_sort2str,
            redirect_filter2str,
        ]

        for converter in converters:
            for special_string in special_strings:
                result = converter(special_string)
                self.assertEqual(
                    result,
                    special_string,
                    f"Converter {converter.__name__} should pass through special characters unchanged",
                )


if __name__ == "__main__":
    unittest.main()
