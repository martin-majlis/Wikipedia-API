"""Unit tests for Wikipedia page section functionality."""

import unittest
from unittest.mock import MagicMock

from tests.mock_data import create_mock_wikipedia
import wikipediaapi


class TestWikipediaPageSection(unittest.TestCase):
    """Test cases for WikipediaPageSection functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.wiki = create_mock_wikipedia()
        # Set the extract format to WIKI for consistent testing
        self.wiki.extract_format = wikipediaapi.ExtractFormat.WIKI

    def test_subsection_by_title_found(self):
        """Test getting a subsection when it exists."""
        # Create mock subsections
        subsection1 = MagicMock()
        subsection1.title = "Subsection 1"
        subsection1.level = 2
        subsection1.full_text.return_value = "Subsection 1 content"

        subsection2 = MagicMock()
        subsection2.title = "Subsection 2"
        subsection2.level = 2
        subsection2.full_text.return_value = "Subsection 2 content"

        # Create main section with subsections
        section = wikipediaapi.WikipediaPageSection(wiki=self.wiki, title="Main Section", level=1)
        section._section = [subsection1, subsection2]

        # Test getting existing subsection
        result = section.section_by_title("Subsection 2")
        self.assertEqual(result, subsection2)

        # Test getting first subsection when multiple exist
        result = section.section_by_title("Subsection 1")
        self.assertEqual(result, subsection1)

    def test_subsection_by_title_not_found(self):
        """Test getting a subsection when it doesn't exist."""
        section = wikipediaapi.WikipediaPageSection(wiki=self.wiki, title="Main Section", level=1)
        section._section = []

        result = section.section_by_title("Nonexistent")
        self.assertIsNone(result)

    def test_subsection_by_title_multiple_returns_last(self):
        """Test that section_by_title returns the last matching subsection."""
        subsection1 = MagicMock()
        subsection1.title = "Same Name"
        subsection1.level = 2
        subsection1.full_text.return_value = "First content"

        subsection2 = MagicMock()
        subsection2.title = "Same Name"
        subsection2.level = 3
        subsection2.full_text.return_value = "Second content"

        section = wikipediaapi.WikipediaPageSection(wiki=self.wiki, title="Main Section", level=1)
        section._section = [subsection1, subsection2]

        result = section.section_by_title("Same Name")
        self.assertEqual(result, subsection2)  # Should return the last one

    def test_full_text_wiki_format(self):
        """Test full_text method with WIKI format."""
        section = wikipediaapi.WikipediaPageSection(
            wiki=self.wiki, title="Test Section", level=2, text="Section content"
        )

        result = section.full_text()
        expected = "Test Section\nSection content\n\n"
        self.assertEqual(result, expected)

    def test_full_text_html_format(self):
        """Test full_text method with HTML format."""
        # Create a wiki with HTML format
        wiki_html = create_mock_wikipedia()
        wiki_html.extract_format = wikipediaapi.ExtractFormat.HTML

        section = wikipediaapi.WikipediaPageSection(
            wiki=wiki_html,
            title="Test Section",
            level=1,  # Use level 1 since full_text starts from level 1
            text="Section content",
        )

        result = section.full_text()
        expected = "<h1>Test Section</h1>\nSection content\n\n"
        self.assertEqual(result, expected)

    def test_full_text_unknown_format_raises_error(self):
        """Test that full_text raises NotImplementedError for unknown format."""
        # Create a wiki with unknown format
        wiki_unknown = create_mock_wikipedia()
        wiki_unknown.extract_format = "unknown"

        section = wikipediaapi.WikipediaPageSection(
            wiki=wiki_unknown, title="Test Section", level=1, text="Section content"
        )

        with self.assertRaises(NotImplementedError) as cm:
            section.full_text()

        self.assertIn("Unknown ExtractFormat type", str(cm.exception))

    def test_full_text_no_text(self):
        """Test full_text method when section has no text."""
        section = wikipediaapi.WikipediaPageSection(
            wiki=self.wiki, title="Empty Section", level=1, text=""
        )

        result = section.full_text()
        expected = "Empty Section\n"
        self.assertEqual(result, expected)

    def test_full_text_level_1(self):
        """Test full_text method with level 1 section."""
        section = wikipediaapi.WikipediaPageSection(
            wiki=self.wiki, title="Top Level", level=1, text="Top level content"
        )

        result = section.full_text()
        expected = "Top Level\nTop level content\n\n"
        self.assertEqual(result, expected)

    def test_full_text_level_4(self):
        """Test full_text method with level 4 section."""
        section = wikipediaapi.WikipediaPageSection(
            wiki=self.wiki, title="Deep Section", level=4, text="Deep content"
        )

        result = section.full_text()
        expected = "Deep Section\nDeep content\n\n"
        self.assertEqual(result, expected)

    def test_full_text_with_subsections(self):
        """Test full_text method includes subsections."""
        # Create mock subsection
        subsection = MagicMock()
        subsection.title = "Subsection"
        subsection.level = 2
        subsection.full_text.return_value = "Subsection\nSub content\n\n"

        section = wikipediaapi.WikipediaPageSection(
            wiki=self.wiki, title="Main Section", level=1, text="Main content"
        )
        section._section = [subsection]

        result = section.full_text()
        expected = "Main Section\nMain content\n\nSubsection\nSub content\n\n"
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
