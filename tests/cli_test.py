"""Unit tests for Wikipedia-API CLI functionality."""

import json
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from tests.mock_data import create_mock_wikipedia
import wikipediaapi
from wikipediaapi.cli import create_wikipedia_instance
from wikipediaapi.cli import fetch_page
from wikipediaapi.cli import format_category_members
from wikipediaapi.cli import format_langlinks
from wikipediaapi.cli import format_page_dict
from wikipediaapi.cli import format_page_info
from wikipediaapi.cli import format_sections
from wikipediaapi.cli import get_category_members
from wikipediaapi.cli import get_langlinks
from wikipediaapi.cli import get_page_backlinks
from wikipediaapi.cli import get_page_categories
from wikipediaapi.cli import get_page_info
from wikipediaapi.cli import get_page_links
from wikipediaapi.cli import get_page_sections
from wikipediaapi.cli import get_page_summary
from wikipediaapi.cli import get_page_text
from wikipediaapi.cli import get_section_text
from wikipediaapi.cli import PageNotFoundError
from wikipediaapi.cli import SectionNotFoundError


class TestCLIFactoryFunctions(unittest.TestCase):
    """Test the factory functions that create Wikipedia instances and pages."""

    def test_create_wikipedia_instance_default_params(self):
        """Test creating Wikipedia instance with default parameters."""
        wiki = create_wikipedia_instance(
            user_agent="test-agent", language="en", variant=None, extract_format="wiki"
        )

        self.assertEqual(wiki.language, "en")
        self.assertIsNone(wiki.variant)
        self.assertEqual(wiki.extract_format, wikipediaapi.ExtractFormat.WIKI)
        # User agent is stored in session headers
        self.assertIn("test-agent", wiki._client.headers["User-Agent"])

    def test_create_wikipedia_instance_html_format(self):
        """Test creating Wikipedia instance with HTML format."""
        wiki = create_wikipedia_instance(
            user_agent="test-agent", language="en", variant=None, extract_format="html"
        )

        self.assertEqual(wiki.extract_format, wikipediaapi.ExtractFormat.HTML)

    def test_create_wikipedia_instance_with_variant(self):
        """Test creating Wikipedia instance with language variant."""
        wiki = create_wikipedia_instance(
            user_agent="test-agent", language="zh", variant="zh-cn", extract_format="wiki"
        )

        self.assertEqual(wiki.language, "zh")
        self.assertEqual(wiki.variant, "zh-cn")
        self.assertIn("test-agent", wiki._client.headers["User-Agent"])

    def test_fetch_page_success(self):
        """Test fetching a page successfully."""
        wiki = create_mock_wikipedia()
        page = fetch_page(wiki, "Test_1", 0)

        # Access a property to trigger fetch and normalization
        _ = page.pageid
        self.assertEqual(page.title, "Test 1")  # Title gets normalized after fetch
        self.assertTrue(page.exists())

    def test_fetch_page_nonexistent(self):
        """Test fetching a non-existent page."""
        wiki = create_mock_wikipedia()
        page = fetch_page(wiki, "NonExisting", 0)

        self.assertEqual(page.title, "NonExisting")
        self.assertFalse(page.exists())


class TestPageSummary(unittest.TestCase):
    """Test the get_page_summary function."""

    def test_get_page_summary_success(self):
        """Test getting summary of an existing page."""
        wiki = create_mock_wikipedia()
        summary = get_page_summary(wiki, "Test_1", 0)

        self.assertIsInstance(summary, str)
        self.assertIn("Summary text", summary)

    def test_get_page_summary_nonexistent(self):
        """Test getting summary of a non-existent page."""
        wiki = create_mock_wikipedia()

        with self.assertRaises(PageNotFoundError) as cm:
            get_page_summary(wiki, "NonExisting", 0)

        self.assertIn("does not exist", str(cm.exception))

    def test_get_page_summary_with_namespace(self):
        """Test getting summary with namespace parameter."""
        wiki = create_mock_wikipedia()
        summary = get_page_summary(wiki, "Test_1", 14)  # Category namespace

        self.assertIsInstance(summary, str)


class TestPageText(unittest.TestCase):
    """Test the get_page_text function."""

    def test_get_page_text_success(self):
        """Test getting full text of an existing page."""
        wiki = create_mock_wikipedia()
        text = get_page_text(wiki, "Test_1", 0)

        self.assertIsInstance(text, str)
        self.assertIn("Summary text", text)
        self.assertIn("Section 1", text)

    def test_get_page_text_nonexistent(self):
        """Test getting text of a non-existent page."""
        wiki = create_mock_wikipedia()

        with self.assertRaises(PageNotFoundError):
            get_page_text(wiki, "NonExisting", 0)


class TestPageSections(unittest.TestCase):
    """Test the get_page_sections and format_sections functions."""

    def test_get_page_sections_success(self):
        """Test getting sections of an existing page."""
        wiki = create_mock_wikipedia()
        sections = get_page_sections(wiki, "Test_1", 0)

        self.assertIsInstance(sections, list)
        self.assertTrue(len(sections) > 0)

        # Check section structure
        first_section = sections[0]
        self.assertIn("title", first_section)
        self.assertIn("level", first_section)
        self.assertIn("indent", first_section)

    def test_get_page_sections_nonexistent(self):
        """Test getting sections of a non-existent page."""
        wiki = create_mock_wikipedia()

        with self.assertRaises(PageNotFoundError):
            get_page_sections(wiki, "NonExisting", 0)

    def test_format_sections_text(self):
        """Test formatting sections as text."""
        sections = [
            {"title": "Section 1", "level": 1, "indent": 0},
            {"title": "Subsection 1.1", "level": 2, "indent": 1},
            {"title": "Section 2", "level": 1, "indent": 0},
        ]

        result = format_sections(sections, "text")
        lines = result.split("\n")

        self.assertEqual(lines[0], "Section 1")
        self.assertEqual(lines[1], "  Subsection 1.1")
        self.assertEqual(lines[2], "Section 2")

    def test_format_sections_json(self):
        """Test formatting sections as JSON."""
        sections = [
            {"title": "Section 1", "level": 1, "indent": 0},
            {"title": "Subsection 1.1", "level": 2, "indent": 1},
        ]

        result = format_sections(sections, "json")
        parsed = json.loads(result)

        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["title"], "Section 1")
        self.assertEqual(parsed[1]["title"], "Subsection 1.1")


class TestSectionText(unittest.TestCase):
    """Test the get_section_text function."""

    def test_get_section_text_success(self):
        """Test getting text of a specific section."""
        wiki = create_mock_wikipedia()

        # Mock the section_by_title method
        with patch.object(wikipediaapi.WikipediaPage, "section_by_title") as mock_section:
            mock_section.return_value = MagicMock()
            mock_section.return_value.full_text.return_value = "Section content here"

            result = get_section_text(wiki, "Test_1", "Section 1", 0)

            self.assertEqual(result, "Section content here")
            mock_section.assert_called_once_with("Section 1")

    def test_get_section_text_nonexistent_page(self):
        """Test getting section text from non-existent page."""
        wiki = create_mock_wikipedia()

        with self.assertRaises(PageNotFoundError):
            get_section_text(wiki, "NonExisting", "Section 1", 0)

    def test_get_section_text_nonexistent_section(self):
        """Test getting text of non-existent section."""
        wiki = create_mock_wikipedia()

        # Mock page that exists but has no section
        page = fetch_page(wiki, "Test_1", 0)
        with patch.object(page, "section_by_title", return_value=None):

            with self.assertRaises(SectionNotFoundError) as cm:
                get_section_text(wiki, "Test_1", "Nonexistent Section", 0)

            self.assertIn("not found", str(cm.exception))


class TestPageLinks(unittest.TestCase):
    """Test the get_page_links function."""

    def test_get_page_links_success(self):
        """Test getting links from an existing page."""
        wiki = create_mock_wikipedia()
        links = get_page_links(wiki, "Test_1", 0)

        self.assertIsInstance(links, dict)

    def test_get_page_links_nonexistent(self):
        """Test getting links from a non-existent page."""
        wiki = create_mock_wikipedia()

        with self.assertRaises(PageNotFoundError):
            get_page_links(wiki, "NonExisting", 0)


class TestPageBacklinks(unittest.TestCase):
    """Test the get_page_backlinks function."""

    def test_get_page_backlinks_success(self):
        """Test getting backlinks to an existing page."""
        wiki = create_mock_wikipedia()
        backlinks = get_page_backlinks(wiki, "Test_1", 0)

        self.assertIsInstance(backlinks, dict)

    def test_get_page_backlinks_nonexistent(self):
        """Test getting backlinks to a non-existent page."""
        wiki = create_mock_wikipedia()

        with self.assertRaises(PageNotFoundError):
            get_page_backlinks(wiki, "NonExisting", 0)


class TestLangLinks(unittest.TestCase):
    """Test the get_langlinks and format_langlinks functions."""

    def test_get_langlinks_success(self):
        """Test getting language links from an existing page."""
        wiki = create_mock_wikipedia()
        langlinks = get_langlinks(wiki, "Test_1", 0)

        self.assertIsInstance(langlinks, dict)

    def test_get_langlinks_nonexistent(self):
        """Test getting language links from a non-existent page."""
        wiki = create_mock_wikipedia()

        with self.assertRaises(PageNotFoundError):
            get_langlinks(wiki, "NonExisting", 0)

    def test_format_langlinks_text(self):
        """Test formatting language links as text."""
        # Create mock pages
        page_de = MagicMock()
        page_de.title = "Test Seite"
        page_de.language = "de"
        page_de._attributes = {"fullurl": "https://de.wikipedia.org/wiki/Test"}

        page_fr = MagicMock()
        page_fr.title = "Page de test"
        page_fr.language = "fr"
        page_fr._attributes = {"fullurl": "https://fr.wikipedia.org/wiki/Test"}

        langlinks = {"de": page_de, "fr": page_fr}

        result = format_langlinks(langlinks, "text")
        lines = result.split("\n")

        self.assertIn("de: Test Seite", lines[0])
        self.assertIn("fr: Page de test", lines[1])

    def test_format_langlinks_json(self):
        """Test formatting language links as JSON."""
        page_de = MagicMock()
        page_de.title = "Test Seite"
        page_de.language = "de"
        page_de._attributes = {"fullurl": "https://de.wikipedia.org/wiki/Test"}

        langlinks = {"de": page_de}

        result = format_langlinks(langlinks, "json")
        parsed = json.loads(result)

        self.assertIn("de", parsed)
        self.assertEqual(parsed["de"]["title"], "Test Seite")
        self.assertEqual(parsed["de"]["language"], "de")


class TestPageCategories(unittest.TestCase):
    """Test the get_page_categories function."""

    def test_get_page_categories_success(self):
        """Test getting categories from an existing page."""
        wiki = create_mock_wikipedia()
        categories = get_page_categories(wiki, "Test_1", 0)

        self.assertIsInstance(categories, dict)

    def test_get_page_categories_nonexistent(self):
        """Test getting categories from a non-existent page."""
        wiki = create_mock_wikipedia()

        with self.assertRaises(PageNotFoundError):
            get_page_categories(wiki, "NonExisting", 0)


class TestCategoryMembers(unittest.TestCase):
    """Test the get_category_members and format_category_members functions."""

    def test_get_category_members_success(self):
        """Test getting members of a category."""
        wiki = create_mock_wikipedia()
        members = get_category_members(wiki, "Category:CLI_Test", 0, 14)

        self.assertIsInstance(members, list)

    def test_get_category_members_nonexistent(self):
        """Test getting members of a non-existent category."""
        wiki = create_mock_wikipedia()

        with self.assertRaises(PageNotFoundError):
            get_category_members(wiki, "Category:Nonexistent", 0, 14)

    def test_get_category_members_with_max_level(self):
        """Test getting category members with recursion depth."""
        wiki = create_mock_wikipedia()
        members = get_category_members(wiki, "Category:CLI_Test", 1, 14)

        self.assertIsInstance(members, list)

    def test_format_category_members_text(self):
        """Test formatting category members as text."""
        members = [
            {"title": "Page 1", "ns": 0, "level": 0},
            {"title": "Subcategory", "ns": 14, "level": 0},
            {"title": "Subcategory Page", "ns": 0, "level": 1},
        ]

        result = format_category_members(members, "text")
        lines = result.split("\n")

        self.assertEqual(lines[0], "Page 1 (ns: 0)")
        self.assertEqual(lines[1], "Subcategory (ns: 14)")
        self.assertEqual(lines[2], "  Subcategory Page (ns: 0)")

    def test_format_category_members_json(self):
        """Test formatting category members as JSON."""
        members = [
            {"title": "Page 1", "ns": 0, "level": 0},
            {"title": "Subcategory", "ns": 14, "level": 0},
        ]

        result = format_category_members(members, "json")
        parsed = json.loads(result)

        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["title"], "Page 1")
        self.assertEqual(parsed[1]["ns"], 14)


class TestPageInfo(unittest.TestCase):
    """Test the get_page_info and format_page_info functions."""

    def test_get_page_info_existing(self):
        """Test getting info about an existing page."""
        wiki = create_mock_wikipedia()
        info = get_page_info(wiki, "Test_1", 0)

        self.assertIsInstance(info, dict)
        self.assertIn("title", info)
        self.assertIn("exists", info)
        self.assertIn("language", info)
        self.assertIn("namespace", info)
        self.assertTrue(info["exists"])
        self.assertIn("pageid", info)

    def test_get_page_info_nonexistent(self):
        """Test getting info about a non-existent page."""
        wiki = create_mock_wikipedia()
        info = get_page_info(wiki, "NonExisting", 0)

        self.assertIsInstance(info, dict)
        self.assertFalse(info["exists"])
        self.assertNotIn("pageid", info)

    def test_format_page_info_text(self):
        """Test formatting page info as text."""
        info = {
            "title": "Test Page",
            "exists": True,
            "language": "en",
            "namespace": 0,
            "pageid": 123,
        }

        result = format_page_info(info, "text")

        self.assertIn("title: Test Page", result)
        self.assertIn("exists: True", result)
        self.assertIn("pageid: 123", result)

    def test_format_page_info_json(self):
        """Test formatting page info as JSON."""
        info = {
            "title": "Test Page",
            "exists": True,
            "language": "en",
            "namespace": 0,
        }

        result = format_page_info(info, "json")
        parsed = json.loads(result)

        self.assertEqual(parsed["title"], "Test Page")
        self.assertTrue(parsed["exists"])


class TestFormatPageDict(unittest.TestCase):
    """Test the format_page_dict function."""

    def test_format_page_dict_text(self):
        """Test formatting page dictionary as text."""
        page1 = MagicMock()
        page1.title = "Page 1"
        page1.language = "en"
        page1.namespace = 0

        page2 = MagicMock()
        page2.title = "Page 2"
        page2.language = "en"
        page2.namespace = 0

        pages = {"Page 1": page1, "Page 2": page2}

        result = format_page_dict(pages, "text")
        lines = result.split("\n")

        self.assertEqual(lines[0], "Page 1")
        self.assertEqual(lines[1], "Page 2")

    def test_format_page_dict_json(self):
        """Test formatting page dictionary as JSON."""
        page1 = MagicMock()
        page1.title = "Page 1"
        page1.language = "en"
        page1.namespace = 0
        page1._attributes = {"fullurl": "https://en.wikipedia.org/wiki/Page_1"}

        pages = {"Page 1": page1}

        result = format_page_dict(pages, "json")
        parsed = json.loads(result)

        self.assertIn("Page 1", parsed)
        self.assertEqual(parsed["Page 1"]["title"], "Page 1")
        self.assertEqual(parsed["Page 1"]["language"], "en")
        self.assertEqual(parsed["Page 1"]["ns"], 0)
        self.assertEqual(parsed["Page 1"]["url"], "https://en.wikipedia.org/wiki/Page_1")

    def test_format_page_dict_json_without_url(self):
        """Test formatting page dictionary as JSON without URL."""
        page1 = MagicMock()
        page1.title = "Page 1"
        page1.language = "en"
        page1.namespace = 0
        # No _attributes or no fullurl

        pages = {"Page 1": page1}

        result = format_page_dict(pages, "json")
        parsed = json.loads(result)

        self.assertNotIn("url", parsed["Page 1"])


class TestCLIExceptions(unittest.TestCase):
    """Test CLI-specific exception classes."""

    def test_page_not_found_error(self):
        """Test PageNotFoundError exception."""
        error = PageNotFoundError("Page not found")
        self.assertEqual(str(error), "Page not found")

        with self.assertRaises(PageNotFoundError):
            raise PageNotFoundError("Test message")

    def test_section_not_found_error(self):
        """Test SectionNotFoundError exception."""
        error = SectionNotFoundError("Section not found")
        self.assertEqual(str(error), "Section not found")

        with self.assertRaises(SectionNotFoundError):
            raise SectionNotFoundError("Test message")


if __name__ == "__main__":
    unittest.main()
