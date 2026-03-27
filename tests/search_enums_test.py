#!/usr/bin/env python3
"""Unit tests for search enums and converters.

Tests the new SearchProp, SearchInfo, SearchWhat, and SearchQiProfile enums
along with their corresponding type aliases and converter functions.
"""

import unittest

from tests.mock_data import wikipedia_api_request
import wikipediaapi


class TestSearchEnums(unittest.TestCase):
    """Test search enum values and converter functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.wiki = wikipediaapi.Wikipedia(user_agent="UnitTests (bot@example.com)", language="en")
        self.wiki._session = wikipedia_api_request(self.wiki)

    def test_search_prop_enum_values(self):
        """Test SearchProp enum has correct values."""
        from wikipediaapi import SearchProp

        # Test all enum values exist and have correct string representations
        expected_values = {
            SearchProp.SIZE: "size",
            SearchProp.WORDCOUNT: "wordcount",
            SearchProp.TIMESTAMP: "timestamp",
            SearchProp.SNIPPET: "snippet",
            SearchProp.TITLE_SNIPPET: "titlesnippet",
            SearchProp.REDIRECT_TITLE: "redirecttitle",
            SearchProp.REDIRECT_SNIPPET: "redirectsnippet",
            SearchProp.SECTION_TITLE: "sectiontitle",
            SearchProp.SECTION_SNIPPET: "sectionsnippet",
            SearchProp.IS_FILE_MATCH: "isfilematch",
            SearchProp.CATEGORY_SNIPPET: "categorysnippet",
            SearchProp.SCORE: "score",
            SearchProp.HAS_RELATED: "hasrelated",
            SearchProp.EXTENSION_DATA: "extensiondata",
        }

        for enum_member, expected_value in expected_values.items():
            self.assertEqual(enum_member.value, expected_value)
            # Note: str(enum_member) returns "EnumName.VALUE" not the value itself

    def test_search_info_enum_values(self):
        """Test SearchInfo enum has correct values."""
        from wikipediaapi import SearchInfo

        expected_values = {
            SearchInfo.TOTAL_HITS: "totalhits",
            SearchInfo.SUGGESTION: "suggestion",
            SearchInfo.REWRITTEN_QUERY: "rewrittenquery",
        }

        for enum_member, expected_value in expected_values.items():
            self.assertEqual(enum_member.value, expected_value)
            # Note: str(enum_member) returns "EnumName.VALUE" not the value itself

    def test_search_what_enum_values(self):
        """Test SearchWhat enum has correct values."""
        from wikipediaapi import SearchWhat

        expected_values = {
            SearchWhat.TEXT: "text",
            SearchWhat.TITLE: "title",
            SearchWhat.NEAR_MATCH: "nearmatch",
        }

        for enum_member, expected_value in expected_values.items():
            self.assertEqual(enum_member.value, expected_value)
            # Note: str(enum_member) returns "EnumName.VALUE" not the value itself

    def test_search_qi_profile_enum_values(self):
        """Test SearchQiProfile enum has correct values."""
        from wikipediaapi import SearchQiProfile

        expected_values = {
            SearchQiProfile.CLASSIC: "classic",
            SearchQiProfile.CLASSIC_NO_BOOST_LINKS: "classic_noboostlinks",
            SearchQiProfile.EMPTY: "empty",
            SearchQiProfile.ENGINE_AUTO_SELECT: "engine_autoselect",
            SearchQiProfile.GROWTH_UNDERLINKED: "growth_underlinked",
            SearchQiProfile.MLR_1024RS: "mlr-1024rs",
            SearchQiProfile.MLR_1024RS_NEXT: "mlr-1024rs-next",
            SearchQiProfile.POPULAR_INCLINKS: "popular_inclinks",
            SearchQiProfile.POPULAR_INCLINKS_PV: "popular_inclinks_pv",
            SearchQiProfile.WSUM_INCLINKS: "wsum_inclinks",
            SearchQiProfile.WSUM_INCLINKS_PV: "wsum_inclinks_pv",
        }

        for enum_member, expected_value in expected_values.items():
            self.assertEqual(enum_member.value, expected_value)
            # Note: str(enum_member) returns "EnumName.VALUE" not the value itself

    def test_search_prop_converter(self):
        """Test search_prop2str converter function."""
        from wikipediaapi import search_prop2str
        from wikipediaapi import SearchProp

        # Test enum to string conversion
        self.assertEqual(search_prop2str(SearchProp.SIZE), "size")
        self.assertEqual(search_prop2str(SearchProp.WORDCOUNT), "wordcount")
        self.assertEqual(search_prop2str(SearchProp.TIMESTAMP), "timestamp")

        # Test string pass-through
        self.assertEqual(search_prop2str("size"), "size")
        self.assertEqual(search_prop2str("wordcount"), "wordcount")
        self.assertEqual(search_prop2str("custom_prop"), "custom_prop")

        # Test case sensitivity preservation for strings
        self.assertEqual(search_prop2str("Size"), "Size")
        self.assertEqual(search_prop2str("WORDCOUNT"), "WORDCOUNT")

    def test_search_info_converter(self):
        """Test search_info2str converter function."""
        from wikipediaapi import search_info2str
        from wikipediaapi import SearchInfo

        # Test enum to string conversion
        self.assertEqual(search_info2str(SearchInfo.TOTAL_HITS), "totalhits")
        self.assertEqual(search_info2str(SearchInfo.SUGGESTION), "suggestion")
        self.assertEqual(search_info2str(SearchInfo.REWRITTEN_QUERY), "rewrittenquery")

        # Test string pass-through
        self.assertEqual(search_info2str("totalhits"), "totalhits")
        self.assertEqual(search_info2str("suggestion"), "suggestion")
        self.assertEqual(search_info2str("custom_info"), "custom_info")

    def test_search_what_converter(self):
        """Test search_what2str converter function."""
        from wikipediaapi import search_what2str
        from wikipediaapi import SearchWhat

        # Test enum to string conversion
        self.assertEqual(search_what2str(SearchWhat.TEXT), "text")
        self.assertEqual(search_what2str(SearchWhat.TITLE), "title")
        self.assertEqual(search_what2str(SearchWhat.NEAR_MATCH), "nearmatch")

        # Test string pass-through
        self.assertEqual(search_what2str("text"), "text")
        self.assertEqual(search_what2str("title"), "title")
        self.assertEqual(search_what2str("custom_what"), "custom_what")

    def test_search_qi_profile_converter(self):
        """Test search_qi_profile2str converter function."""
        from wikipediaapi import search_qi_profile2str
        from wikipediaapi import SearchQiProfile

        # Test enum to string conversion
        self.assertEqual(
            search_qi_profile2str(SearchQiProfile.ENGINE_AUTO_SELECT), "engine_autoselect"
        )
        self.assertEqual(search_qi_profile2str(SearchQiProfile.CLASSIC), "classic")
        self.assertEqual(search_qi_profile2str(SearchQiProfile.EMPTY), "empty")

        # Test string pass-through
        self.assertEqual(search_qi_profile2str("engine_autoselect"), "engine_autoselect")
        self.assertEqual(search_qi_profile2str("classic"), "classic")
        self.assertEqual(search_qi_profile2str("custom_profile"), "custom_profile")

    def test_type_aliases_accept_enums(self):
        """Test Wiki* type aliases accept enum members."""
        from wikipediaapi import SearchInfo
        from wikipediaapi import SearchProp
        from wikipediaapi import SearchQiProfile
        from wikipediaapi import SearchWhat
        from wikipediaapi import WikiSearchInfo
        from wikipediaapi import WikiSearchProp
        from wikipediaapi import WikiSearchQiProfile
        from wikipediaapi import WikiSearchWhat

        # These should all be valid assignments
        prop: WikiSearchProp = SearchProp.SIZE
        info: WikiSearchInfo = SearchInfo.TOTAL_HITS
        what: WikiSearchWhat = SearchWhat.TEXT
        qi_profile: WikiSearchQiProfile = SearchQiProfile.ENGINE_AUTO_SELECT

        self.assertIsInstance(prop, SearchProp)
        self.assertIsInstance(info, SearchInfo)
        self.assertIsInstance(what, SearchWhat)
        self.assertIsInstance(qi_profile, SearchQiProfile)

    def test_type_aliases_accept_strings(self):
        """Test Wiki* type aliases accept strings."""
        from wikipediaapi import WikiSearchInfo
        from wikipediaapi import WikiSearchProp
        from wikipediaapi import WikiSearchQiProfile
        from wikipediaapi import WikiSearchWhat

        # These should all be valid assignments
        prop: WikiSearchProp = "size"
        info: WikiSearchInfo = "totalhits"
        what: WikiSearchWhat = "text"
        qi_profile: WikiSearchQiProfile = "engine_autoselect"

        self.assertEqual(prop, "size")
        self.assertEqual(info, "totalhits")
        self.assertEqual(what, "text")
        self.assertEqual(qi_profile, "engine_autoselect")

    def test_search_with_enum_parameters(self):
        """Test search method accepts enum parameters."""
        from wikipediaapi import SearchInfo
        from wikipediaapi import SearchProp
        from wikipediaapi import SearchQiProfile
        from wikipediaapi import SearchSort
        from wikipediaapi import SearchWhat

        # This should work without errors
        results = self.wiki.search(
            "test",
            prop=[SearchProp.SIZE, SearchProp.WORDCOUNT],
            info=[SearchInfo.TOTAL_HITS],
            what=SearchWhat.TEXT,
            qi_profile=SearchQiProfile.ENGINE_AUTO_SELECT,
            sort=SearchSort.RELEVANCE,
        )

        # Verify we get results (mock data should return something)
        self.assertIsNotNone(results)
        self.assertGreaterEqual(len(results.pages), 1)  # Should have at least 1 result

    def test_search_with_string_parameters(self):
        """Test search method accepts string parameters (backward compatibility)."""
        # This should work without errors
        results = self.wiki.search(
            "test",
            prop=["size", "wordcount"],
            info=["totalhits"],
            what="text",
            qi_profile="engine_autoselect",
            sort="relevance",
        )

        # Verify we get results
        self.assertIsNotNone(results)
        self.assertGreaterEqual(len(results.pages), 1)

    def test_search_with_mixed_parameters(self):
        """Test search method accepts mixed enum and string parameters."""
        from wikipediaapi import SearchInfo
        from wikipediaapi import SearchProp
        from wikipediaapi import SearchWhat

        # This should work without errors
        results = self.wiki.search(
            "test",
            prop=[SearchProp.SIZE, "wordcount"],  # Mixed
            info=[SearchInfo.TOTAL_HITS, "suggestion"],  # Mixed
            what=SearchWhat.TEXT,
            qi_profile="engine_autoselect",  # String
            sort="relevance",  # String
        )

        # Verify we get results
        self.assertIsNotNone(results)
        self.assertGreaterEqual(len(results.pages), 1)

    def test_enum_immutability(self):
        """Test enum values are immutable."""
        from wikipediaapi import SearchInfo
        from wikipediaapi import SearchProp
        from wikipediaapi import SearchQiProfile
        from wikipediaapi import SearchWhat

        # Enums should be immutable
        with self.assertRaises(AttributeError):
            SearchProp.SIZE = "invalid"

        with self.assertRaises(AttributeError):
            SearchInfo.TOTAL_HITS = "invalid"

        with self.assertRaises(AttributeError):
            SearchWhat.TEXT = "invalid"

        with self.assertRaises(AttributeError):
            SearchQiProfile.ENGINE_AUTO_SELECT = "invalid"

    def test_enum_completeness(self):
        """Test all expected enum values are present."""
        from wikipediaapi import SearchInfo
        from wikipediaapi import SearchProp
        from wikipediaapi import SearchQiProfile
        from wikipediaapi import SearchWhat

        # SearchProp should have 14 values
        self.assertEqual(len(SearchProp), 14)
        expected_props = {
            "SIZE",
            "WORDCOUNT",
            "TIMESTAMP",
            "SNIPPET",
            "TITLE_SNIPPET",
            "REDIRECT_TITLE",
            "REDIRECT_SNIPPET",
            "SECTION_TITLE",
            "SECTION_SNIPPET",
            "IS_FILE_MATCH",
            "CATEGORY_SNIPPET",
            "SCORE",
            "HAS_RELATED",
            "EXTENSION_DATA",
        }
        actual_props = {member.name for member in SearchProp}
        self.assertEqual(actual_props, expected_props)

        # SearchInfo should have 3 values
        self.assertEqual(len(SearchInfo), 3)
        expected_infos = {"TOTAL_HITS", "SUGGESTION", "REWRITTEN_QUERY"}
        actual_infos = {member.name for member in SearchInfo}
        self.assertEqual(actual_infos, expected_infos)

        # SearchWhat should have 3 values
        self.assertEqual(len(SearchWhat), 3)
        expected_whats = {"TEXT", "TITLE", "NEAR_MATCH"}
        actual_whats = {member.name for member in SearchWhat}
        self.assertEqual(actual_whats, expected_whats)

        # SearchQiProfile should have 11 values
        self.assertEqual(len(SearchQiProfile), 11)
        expected_profiles = {
            "CLASSIC",
            "CLASSIC_NO_BOOST_LINKS",
            "EMPTY",
            "ENGINE_AUTO_SELECT",
            "GROWTH_UNDERLINKED",
            "MLR_1024RS",
            "MLR_1024RS_NEXT",
            "POPULAR_INCLINKS",
            "POPULAR_INCLINKS_PV",
            "WSUM_INCLINKS",
            "WSUM_INCLINKS_PV",
        }
        actual_profiles = {member.name for member in SearchQiProfile}
        self.assertEqual(actual_profiles, expected_profiles)


if __name__ == "__main__":
    unittest.main()
