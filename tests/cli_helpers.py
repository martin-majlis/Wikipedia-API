"""Helper utilities for testing Wikipedia-API CLI functionality."""

import json
from typing import Any
from unittest.mock import MagicMock

from tests.mock_data import create_mock_wikipedia


class CLITestHelper:
    """Helper class for CLI testing with common utilities."""

    def __init__(self):
        self.mock_wiki = create_mock_wikipedia()

    def create_mock_page_with_content(
        self, title: str, content: str, exists: bool = True
    ) -> MagicMock:
        """Create a mock page with specific content."""
        page = MagicMock()
        page.title = title
        page.wiki = self.mock_wiki

        if exists:
            page._attributes = {
                "fullurl": f"https://en.wikipedia.org/wiki/{title}",
                "pageid": 1,
                "displaytitle": title,
            }
            page.summary = content.split("\n\n")[0] if content else ""
            page.text = content
            page.exists.return_value = True
        else:
            page._attributes = {"missing": ""}
            page.summary = ""
            page.text = ""
            page.exists.return_value = False

        return page

    def create_mock_page_with_sections(
        self, title: str, sections_data: list[dict[str, Any]]
    ) -> MagicMock:
        """Create a mock page with specific sections."""
        page = self.create_mock_page_with_content(title, "Mock content", True)

        # Create mock section objects
        mock_sections = []
        for section_data in sections_data:
            mock_section = MagicMock()
            mock_section.title = section_data["title"]
            mock_section.level = section_data["level"]
            mock_section.sections = section_data.get("sections", [])
            mock_sections.append(mock_section)

        page.sections = mock_sections
        return page

    def create_mock_page_with_links(self, title: str, links: dict[str, str]) -> MagicMock:
        """Create a mock page with specific links."""
        page = self.create_mock_page_with_content(title, "Mock content", True)

        # Create mock linked pages
        mock_links = {}
        for link_title, link_url in links.items():
            linked_page = MagicMock()
            linked_page.title = link_title
            linked_page._attributes = {"fullurl": link_url}
            mock_links[link_title] = linked_page

        page.links = mock_links
        return page

    def create_mock_page_with_langlinks(
        self, title: str, langlinks: dict[str, dict[str, str]]
    ) -> MagicMock:
        """Create a mock page with specific language links."""
        page = self.create_mock_page_with_content(title, "Mock content", True)

        # Create mock language-linked pages
        mock_langlinks = {}
        for lang, lang_data in langlinks.items():
            lang_page = MagicMock()
            lang_page.title = lang_data["title"]
            lang_page.language = lang
            lang_page._attributes = {"fullurl": lang_data["url"]}
            mock_langlinks[lang] = lang_page

        page.langlinks = mock_langlinks
        return page

    def create_mock_page_with_categories(self, title: str, categories: list[str]) -> MagicMock:
        """Create a mock page with specific categories."""
        page = self.create_mock_page_with_content(title, "Mock content", True)

        # Create mock category pages
        mock_categories = {}
        for category in categories:
            cat_page = MagicMock()
            cat_page.title = category
            cat_page.namespace = 14  # Category namespace
            mock_categories[category] = cat_page

        page.categories = mock_categories
        return page

    def create_mock_category_with_members(
        self, title: str, members: list[dict[str, Any]]
    ) -> MagicMock:
        """Create a mock category page with specific members."""
        page = self.create_mock_page_with_content(title, "Category content", True)

        # Create mock member pages
        mock_members = {}
        for member_data in members:
            member_page = MagicMock()
            member_page.title = member_data["title"]
            member_page.namespace = member_data["ns"]

            # If member is a subcategory, add categorymembers
            if member_data["ns"] == 14:
                subcategory_members = {}
                for sub_member in member_data.get("subcategory_members", []):
                    sub_page = MagicMock()
                    sub_page.title = sub_member["title"]
                    sub_page.namespace = sub_member["ns"]
                    subcategory_members[sub_member["title"]] = sub_page
                member_page.categorymembers = subcategory_members

            mock_members[member_data["title"]] = member_page

        page.categorymembers = mock_members
        return page

    def assert_json_output(self, output: str, expected_keys: list[str]) -> bool:
        """Assert that JSON output contains expected keys."""
        try:
            parsed = json.loads(output)
            for key in expected_keys:
                if key not in parsed:
                    return False
            return True
        except json.JSONDecodeError:
            return False

    def assert_text_output_contains(self, output: str, expected_strings: list[str]) -> bool:
        """Assert that text output contains expected strings."""
        for expected in expected_strings:
            if expected not in output:
                return False
        return True

    def normalize_output(self, output: str) -> str:
        """Normalize output for comparison (remove extra whitespace)."""
        return "\n".join(line.strip() for line in output.strip().split("\n") if line.strip())


class MockCLIRunner:
    """Mock CLI runner for testing CLI commands without actual subprocess calls."""

    def __init__(self):
        self.test_helper = CLITestHelper()

    def run_cli_command_test(self, command_func, *args, **kwargs):
        """Run a CLI command function for testing."""
        try:
            result = command_func(*args, **kwargs)
            return {"success": True, "output": result, "error": None}
        except Exception as e:
            return {"success": False, "output": None, "error": str(e)}

    def create_test_scenarios(self) -> dict[str, Any]:
        """Create common test scenarios for CLI testing."""
        return {
            "existing_page": {
                "title": "Test Page",
                "content": "This is a test summary.\n\n== Section 1 ==\nSection content.",
                "exists": True,
            },
            "nonexistent_page": {
                "title": "Nonexistent Page",
                "content": "",
                "exists": False,
            },
            "page_with_sections": {
                "title": "Page with Sections",
                "sections": [
                    {"title": "Introduction", "level": 1, "sections": []},
                    {
                        "title": "History",
                        "level": 1,
                        "sections": [
                            {"title": "Early History", "level": 2, "sections": []},
                            {"title": "Modern History", "level": 2, "sections": []},
                        ],
                    },
                ],
                "exists": True,
            },
            "page_with_links": {
                "title": "Page with Links",
                "links": {
                    "Related Page 1": "https://en.wikipedia.org/wiki/Related_Page_1",
                    "Related Page 2": "https://en.wikipedia.org/wiki/Related_Page_2",
                },
                "exists": True,
            },
            "page_with_langlinks": {
                "title": "Page with LangLinks",
                "langlinks": {
                    "de": {"title": "Test Seite", "url": "https://de.wikipedia.org/wiki/Test"},
                    "fr": {"title": "Page de test", "url": "https://fr.wikipedia.org/wiki/Test"},
                },
                "exists": True,
            },
            "page_with_categories": {
                "title": "Page with Categories",
                "categories": ["Category:Test", "Category:Example"],
                "exists": True,
            },
            "category_with_members": {
                "title": "Category:Test",
                "members": [
                    {"title": "Test Page 1", "ns": 0},
                    {"title": "Test Page 2", "ns": 0},
                    {
                        "title": "Subcategory",
                        "ns": 14,
                        "subcategory_members": [
                            {"title": "Subcategory Page", "ns": 0},
                        ],
                    },
                ],
                "exists": True,
            },
        }


# Test data fixtures for common scenarios
TEST_SCENARIOS = {
    "basic_page": {
        "title": "Test Page",
        "summary": "This is a test summary.",
        "text": (
            "This is a test summary.\n\n"
            "== Section 1 ==\n"
            "Content for section 1.\n\n"
            "== Section 2 ==\n"
            "Content for section 2."
        ),
        "exists": True,
        "pageid": 123,
        "language": "en",
        "namespace": 0,
    },
    "nonexistent_page": {
        "title": "Nonexistent Page",
        "summary": "",
        "text": "",
        "exists": False,
        "pageid": None,
        "language": "en",
        "namespace": 0,
    },
    "page_with_complex_sections": {
        "title": "Complex Page",
        "sections": [
            {"title": "Introduction", "level": 1, "indent": 0},
            {"title": "Background", "level": 1, "indent": 0},
            {"title": "Early Background", "level": 2, "indent": 1},
            {"title": "Recent Background", "level": 2, "indent": 1},
            {"title": "Methods", "level": 1, "indent": 0},
            {"title": "Results", "level": 1, "indent": 0},
            {"title": "Discussion", "level": 1, "indent": 0},
            {"title": "Conclusion", "level": 1, "indent": 0},
        ],
        "exists": True,
    },
    "page_with_links": {
        "title": "Linked Page",
        "links": {
            "Target Page 1": {"title": "Target Page 1", "language": "en", "ns": 0},
            "Target Page 2": {"title": "Target Page 2", "language": "en", "ns": 0},
            "Related Category": {"title": "Category:Related", "language": "en", "ns": 14},
        },
        "exists": True,
    },
    "page_with_langlinks": {
        "title": "Multilingual Page",
        "langlinks": {
            "de": {
                "title": "Test Seite",
                "language": "de",
                "url": "https://de.wikipedia.org/wiki/Test",
            },
            "fr": {
                "title": "Page de test",
                "language": "fr",
                "url": "https://fr.wikipedia.org/wiki/Test",
            },
            "es": {
                "title": "Página de prueba",
                "language": "es",
                "url": "https://es.wikipedia.org/wiki/Test",
            },
            "zh": {
                "title": "测试页面",
                "language": "zh",
                "url": "https://zh.wikipedia.org/wiki/Test",
            },
        },
        "exists": True,
    },
    "category_with_nested_members": {
        "title": "Category:Test Category",
        "members": [
            {"title": "Test Article 1", "ns": 0, "level": 0},
            {"title": "Test Article 2", "ns": 0, "level": 0},
            {"title": "Subcategory 1", "ns": 14, "level": 0},
            {"title": "Subcategory Article", "ns": 0, "level": 1},
            {"title": "Subcategory 2", "ns": 14, "level": 0},
            {"title": "Nested Article", "ns": 0, "level": 1},
        ],
        "exists": True,
    },
}


def create_mock_wiki_for_testing():
    """Create a standardized mock Wikipedia instance for testing."""
    return create_mock_wikipedia()


def setup_cli_test_mocks():
    """Set up common mocks for CLI testing."""
    import wikipediaapi.cli as cli_module

    # Mock the CLI exceptions for testing
    cli_module.PageNotFoundError = Exception
    cli_module.SectionNotFoundError = Exception

    return create_mock_wikipedia()


def compare_cli_output(actual: str, expected: str, format_type: str = "text") -> bool:
    """Compare CLI output, handling format-specific differences."""
    if format_type == "json":
        try:
            actual_data = json.loads(actual)
            expected_data = json.loads(expected)
            return bool(actual_data == expected_data)
        except json.JSONDecodeError:
            return False
    else:
        # Normalize text output
        def normalize(s: str) -> str:
            return "\n".join(line.strip() for line in s.strip().split("\n") if line.strip())

        result = normalize(actual) == normalize(expected)
        return bool(result)
