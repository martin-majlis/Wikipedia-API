#!/usr/bin/env python3
"""Unit tests for CoordinatesProp enum and related functionality.

Tests the new CoordinatesProp enum, WikiCoordinatesProp type alias,
and coordinates_prop2str converter function with comprehensive coverage
including edge cases and integration with coordinate methods.
"""

import unittest

from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi
from wikipediaapi import coordinates_prop2str
from wikipediaapi import CoordinatesProp
from wikipediaapi import WikiCoordinatesProp


class TestCoordinatesPropEnum(unittest.TestCase):
    """Test the CoordinatesProp enum definition and values."""

    def test_enum_values(self):
        """Test that all expected enum values are present."""
        expected_values = {
            CoordinatesProp.COUNTRY: "country",
            CoordinatesProp.DIM: "dim",
            CoordinatesProp.GLOBE: "globe",
            CoordinatesProp.NAME: "name",
            CoordinatesProp.REGION: "region",
            CoordinatesProp.TYPE: "type",
        }

        for enum_member, expected_value in expected_values.items():
            self.assertEqual(enum_member.value, expected_value)
            self.assertIsInstance(enum_member.value, str)

    def test_enum_completeness(self):
        """Test that we have exactly the expected number of enum values."""
        all_values = list(CoordinatesProp)
        self.assertEqual(len(all_values), 6, "Should have exactly 6 CoordinatesProp values")

        expected_names = {"COUNTRY", "DIM", "GLOBE", "NAME", "REGION", "TYPE"}
        actual_names = {prop.name for prop in all_values}
        self.assertEqual(actual_names, expected_names)

    def test_enum_iteration(self):
        """Test that enum can be iterated and values are consistent."""
        values = list(CoordinatesProp)
        self.assertEqual(len(values), 6)

        # Test that iteration is deterministic
        values1 = list(CoordinatesProp)
        values2 = list(CoordinatesProp)
        self.assertEqual(values1, values2)

    def test_enum_membership(self):
        """Test enum membership operations."""
        self.assertIn(CoordinatesProp.GLOBE, CoordinatesProp)

        # Test that invalid string is not in enum values (compatible with all Python versions)
        try:
            self.assertNotIn("invalid", CoordinatesProp)
        except TypeError:
            # In Python < 3.12, string membership in enum raises TypeError
            # Check against enum values instead
            enum_values = [prop.value for prop in CoordinatesProp]
            self.assertNotIn("invalid", enum_values)

        # Test that all expected values are in the enum
        expected_values = ["country", "dim", "globe", "name", "region", "type"]
        actual_values = [prop.value for prop in CoordinatesProp]
        for expected in expected_values:
            self.assertIn(expected, actual_values)


class TestCoordinatesPropConverter(unittest.TestCase):
    """Test the coordinates_prop2str converter function."""

    def test_enum_to_string_conversion(self):
        """Test converting enum values to strings."""
        test_cases = [
            (CoordinatesProp.COUNTRY, "country"),
            (CoordinatesProp.DIM, "dim"),
            (CoordinatesProp.GLOBE, "globe"),
            (CoordinatesProp.NAME, "name"),
            (CoordinatesProp.REGION, "region"),
            (CoordinatesProp.TYPE, "type"),
        ]

        for enum_val, expected_str in test_cases:
            with self.subTest(enum_val=enum_val):
                result = coordinates_prop2str(enum_val)
                self.assertEqual(result, expected_str)
                self.assertIsInstance(result, str)

    def test_string_passthrough(self):
        """Test that strings are returned unchanged."""
        test_strings = [
            "country",
            "dim",
            "globe",
            "name",
            "region",
            "type",
            "custom_property",
            "UPPERCASE",
            "MiXeDcAsE",
            "",
            "special-chars_123",
        ]

        for test_str in test_strings:
            with self.subTest(test_str=test_str):
                result = coordinates_prop2str(test_str)
                self.assertEqual(result, test_str)

    def test_mixed_input_types(self):
        """Test converter with both enum and string inputs."""
        enum_input = CoordinatesProp.GLOBE
        string_input = "globe"
        custom_string = "custom_prop"

        self.assertEqual(coordinates_prop2str(enum_input), "globe")
        self.assertEqual(coordinates_prop2str(string_input), "globe")
        self.assertEqual(coordinates_prop2str(custom_string), "custom_prop")

    def test_type_alias_compatibility(self):
        """Test that WikiCoordinatesProp accepts both enums and strings."""
        # These should all be valid WikiCoordinatesProp values
        valid_inputs: list[WikiCoordinatesProp] = [
            CoordinatesProp.GLOBE,
            "globe",
            CoordinatesProp.NAME,
            "name",
            "custom_property",
        ]

        for valid_input in valid_inputs:
            with self.subTest(input=valid_input):
                result = coordinates_prop2str(valid_input)
                self.assertIsInstance(result, str)

                # If it's an enum, verify the conversion
                if isinstance(valid_input, CoordinatesProp):
                    self.assertEqual(result, valid_input.value)
                else:
                    # If it's a string, it should pass through unchanged
                    self.assertEqual(result, valid_input)


class TestCoordinatesPropIntegration(unittest.TestCase):
    """Test integration of CoordinatesProp with actual coordinate methods."""

    def setUp(self):
        """Set up test fixtures with mock data."""
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)
        self.test_page = self.wiki.page("Test_1")  # Use existing mock data page

    def test_coordinates_with_single_enum_prop(self):
        """Test coordinates method with single enum property."""
        # This should work without errors
        coords = self.wiki.coordinates(self.test_page, prop=[CoordinatesProp.GLOBE])
        self.assertIsInstance(coords, list)

    def test_coordinates_with_multiple_enum_props(self):
        """Test coordinates method with multiple enum properties."""
        props = [CoordinatesProp.GLOBE, CoordinatesProp.NAME, CoordinatesProp.TYPE]
        coords = self.wiki.coordinates(self.test_page, prop=props)
        self.assertIsInstance(coords, list)

    def test_coordinates_with_mixed_props(self):
        """Test coordinates method with mixed enum and string properties."""
        props = [CoordinatesProp.GLOBE, "name", "type"]  # Mixed enum and strings
        coords = self.wiki.coordinates(self.test_page, prop=props)
        self.assertIsInstance(coords, list)

    def test_coordinates_with_all_enum_props(self):
        """Test coordinates method with all available enum properties."""
        all_props = list(CoordinatesProp)
        coords = self.wiki.coordinates(self.test_page, prop=all_props)
        self.assertIsInstance(coords, list)

    def test_batch_coordinates_with_enum_props(self):
        """Test batch coordinates with enum properties."""
        pages = self.wiki.pages(["Test_1", "NonExistent"])  # Use existing mock data pages
        props = [CoordinatesProp.GLOBE, CoordinatesProp.NAME]

        batch_coords = pages.coordinates(prop=props)
        self.assertIsInstance(batch_coords, dict)

        # Should have results for both pages (including empty result for NonExistent)
        self.assertGreaterEqual(len(batch_coords), 1)

        for page, coord_list in batch_coords.items():
            self.assertIsInstance(coord_list, list)

    def test_backward_compatibility_strings_still_work(self):
        """Test that string-based property specification still works."""
        # Traditional string approach should still work
        coords_strings = self.wiki.coordinates(self.test_page, prop=["globe", "name"])
        self.assertIsInstance(coords_strings, list)

        # Should produce similar results to enum approach
        coords_enums = self.wiki.coordinates(
            self.test_page, prop=[CoordinatesProp.GLOBE, CoordinatesProp.NAME]
        )
        self.assertIsInstance(coords_enums, list)


class TestCoordinatesPropEdgeCases(unittest.TestCase):
    """Test edge cases and error handling for CoordinatesProp."""

    def test_converter_with_none(self):
        """Test converter behavior with None input."""
        # The converter should handle None gracefully
        result = coordinates_prop2str(None)
        self.assertIsNone(result)

    def test_converter_with_empty_string(self):
        """Test converter behavior with empty string."""
        result = coordinates_prop2str("")
        self.assertEqual(result, "")

    def test_converter_with_whitespace(self):
        """Test converter behavior with whitespace strings."""
        test_cases = [" ", "  ", "\t", "\n", "  \t\n  "]

        for test_str in test_cases:
            with self.subTest(test_str=repr(test_str)):
                result = coordinates_prop2str(test_str)
                self.assertEqual(result, test_str)

    def test_enum_immutability(self):
        """Test that enum values are immutable."""
        prop = CoordinatesProp.GLOBE

        # Enum values should be immutable
        with self.assertRaises(AttributeError):
            prop.value = "modified"

    def test_type_alias_annotations(self):
        """Test that type annotations work correctly."""

        def test_function(prop: WikiCoordinatesProp) -> str:
            return coordinates_prop2str(prop)

        # These should all be valid calls
        self.assertEqual(test_function(CoordinatesProp.GLOBE), "globe")
        self.assertEqual(test_function("globe"), "globe")
        self.assertEqual(test_function("custom"), "custom")

    def test_all_enum_values_in_mediawiki_spec(self):
        """Test that all enum values match MediaWiki API specification."""
        # According to the MediaWiki API spec, valid coprop values are:
        # country, dim, globe, name, region, type
        expected_api_values = {"country", "dim", "globe", "name", "region", "type"}

        actual_enum_values = {prop.value for prop in CoordinatesProp}
        self.assertEqual(actual_enum_values, expected_api_values)

    def test_performance_with_large_prop_lists(self):
        """Test converter performance with large property lists."""
        import time

        # Create a large list of mixed enum and string values
        large_props = []
        for i in range(1000):
            if i % 2 == 0:
                large_props.append(CoordinatesProp.GLOBE)
            else:
                large_props.append("name")

        # Time the conversion
        start_time = time.time()
        for prop in large_props:
            coordinates_prop2str(prop)
        end_time = time.time()

        # Should complete quickly (less than 1 second for 1000 conversions)
        self.assertLess(end_time - start_time, 1.0)


if __name__ == "__main__":
    unittest.main()
