"""Integration tests for CLI commands using Click's testing utilities."""

import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from click.testing import CliRunner

from tests.mock_data import create_mock_wikipedia
import wikipediaapi.cli


class TestCLICommands(unittest.TestCase):
    """Test CLI command functions directly using Click's test runner."""

    def setUp(self):
        self.runner = CliRunner()
        self.mock_wiki = create_mock_wikipedia()

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_summary")
    def test_summary_command_success(self, mock_get_summary, mock_create_wiki):
        """Test summary command on successful page fetch."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_summary.return_value = "Test summary content"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["summary", "Test_Page"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Test summary content", result.output)
        mock_create_wiki.assert_called_once()
        mock_get_summary.assert_called_once()

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_summary")
    def test_summary_command_page_not_found(self, mock_get_summary, mock_create_wiki):
        """Test summary command with non-existent page."""
        from wikipediaapi.cli import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_summary.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["summary", "Test_Page"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Page 'Test_Page' does not exist.", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_text")
    def test_text_command_success(self, mock_get_text, mock_create_wiki):
        """Test text command on successful page fetch."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_text.return_value = "Full page text content"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["text", "Test_Page"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Full page text content", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_text")
    def test_text_command_page_not_found(self, mock_get_text, mock_create_wiki):
        """Test text command with non-existent page."""
        from wikipediaapi.cli import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_text.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["text", "Test_Page"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Page 'Test_Page' does not exist.", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_sections")
    @patch("wikipediaapi.cli.format_sections")
    def test_sections_command_text(self, mock_format, mock_get_sections, mock_create_wiki):
        """Test sections command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_sections.return_value = [{"title": "Section 1", "level": 1, "indent": 0}]
        mock_format.return_value = "Section 1"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["sections", "Test_Page"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Section 1", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_sections")
    @patch("wikipediaapi.cli.format_sections")
    def test_sections_command_json(self, mock_format, mock_get_sections, mock_create_wiki):
        """Test sections command with JSON output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_sections.return_value = [{"title": "Section 1", "level": 1, "indent": 0}]
        mock_format.return_value = '[{"title": "Section 1", "level": 1, "indent": 0}]'

        result = self.runner.invoke(wikipediaapi.cli.cli, ["sections", "Test_Page", "--json"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn('[{"title": "Section 1", "level": 1, "indent": 0}]', result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_sections")
    def test_sections_command_page_not_found(self, mock_get_sections, mock_create_wiki):
        """Test sections command with non-existent page."""
        from wikipediaapi.cli import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_sections.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["sections", "Test_Page"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Page 'Test_Page' does not exist.", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_section_text")
    def test_section_command_success(self, mock_get_section, mock_create_wiki):
        """Test section command on successful fetch."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_section.return_value = "Section content here"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["section", "Test_Page", "Section_Name"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Section content here", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_section_text")
    def test_section_command_page_not_found(self, mock_get_section, mock_create_wiki):
        """Test section command with non-existent page."""
        from wikipediaapi.cli import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_section.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["section", "Test_Page", "Section_Name"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Page 'Test_Page' does not exist.", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_section_text")
    def test_section_command_section_not_found(self, mock_get_section, mock_create_wiki):
        """Test section command with non-existent section."""
        from wikipediaapi.cli import SectionNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_section.side_effect = SectionNotFoundError("Section 'Section_Name' not found.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["section", "Test_Page", "Section_Name"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Section 'Section_Name' not found.", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_links")
    @patch("wikipediaapi.cli.format_page_dict")
    def test_links_command_text(self, mock_format, mock_get_links, mock_create_wiki):
        """Test links command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_links.return_value = {"Link 1": MagicMock(), "Link 2": MagicMock()}
        mock_format.return_value = "Link 1\nLink 2"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["links", "Test_Page"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Link 1", result.output)
        self.assertIn("Link 2", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_links")
    @patch("wikipediaapi.cli.format_page_dict")
    def test_links_command_json(self, mock_format, mock_get_links, mock_create_wiki):
        """Test links command with JSON output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_links.return_value = {"Link 1": MagicMock()}
        mock_format.return_value = '{"Link 1": {"title": "Link 1"}}'

        result = self.runner.invoke(wikipediaapi.cli.cli, ["links", "Test_Page", "--json"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn('{"Link 1": {"title": "Link 1"}}', result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_links")
    def test_links_command_page_not_found(self, mock_get_links, mock_create_wiki):
        """Test links command with non-existent page."""
        from wikipediaapi.cli import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_links.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["links", "Test_Page"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Page 'Test_Page' does not exist.", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_backlinks")
    @patch("wikipediaapi.cli.format_page_dict")
    def test_backlinks_command_text(self, mock_format, mock_get_backlinks, mock_create_wiki):
        """Test backlinks command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_backlinks.return_value = {"Backlink 1": MagicMock(), "Backlink 2": MagicMock()}
        mock_format.return_value = "Backlink 1\nBacklink 2"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["backlinks", "Test_Page"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Backlink 1", result.output)
        self.assertIn("Backlink 2", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_backlinks")
    def test_backlinks_command_page_not_found(self, mock_get_backlinks, mock_create_wiki):
        """Test backlinks command with non-existent page."""
        from wikipediaapi.cli import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_backlinks.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["backlinks", "Test_Page"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Page 'Test_Page' does not exist.", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_langlinks")
    @patch("wikipediaapi.cli.format_langlinks")
    def test_langlinks_command_text(self, mock_format, mock_get_langlinks, mock_create_wiki):
        """Test langlinks command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_langlinks.return_value = {"de": MagicMock(), "fr": MagicMock()}
        mock_format.return_value = "de: German Title (url)\nfr: French Title (url)"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["langlinks", "Test_Page"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("de: German Title", result.output)
        self.assertIn("fr: French Title", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_langlinks")
    @patch("wikipediaapi.cli.format_langlinks")
    def test_langlinks_command_json(self, mock_format, mock_get_langlinks, mock_create_wiki):
        """Test langlinks command with JSON output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_langlinks.return_value = {"de": MagicMock()}
        mock_format.return_value = '{"de": {"title": "German Title"}}'

        result = self.runner.invoke(wikipediaapi.cli.cli, ["langlinks", "Test_Page", "--json"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn('{"de": {"title": "German Title"}}', result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_langlinks")
    def test_langlinks_command_page_not_found(self, mock_get_langlinks, mock_create_wiki):
        """Test langlinks command with non-existent page."""
        from wikipediaapi.cli import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_langlinks.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["langlinks", "Test_Page"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Page 'Test_Page' does not exist.", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_categories")
    @patch("wikipediaapi.cli.format_page_dict")
    def test_categories_command_text(self, mock_format, mock_get_categories, mock_create_wiki):
        """Test categories command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_categories.return_value = {"Category 1": MagicMock(), "Category 2": MagicMock()}
        mock_format.return_value = "Category 1\nCategory 2"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["categories", "Test_Page"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Category 1", result.output)
        self.assertIn("Category 2", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_categories")
    def test_categories_command_page_not_found(self, mock_get_categories, mock_create_wiki):
        """Test categories command with non-existent page."""
        from wikipediaapi.cli import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_categories.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["categories", "Test_Page"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Page 'Test_Page' does not exist.", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_category_members")
    @patch("wikipediaapi.cli.format_category_members")
    def test_categorymembers_command_text(self, mock_format, mock_get_members, mock_create_wiki):
        """Test categorymembers command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_members.return_value = [{"title": "Member 1", "ns": 0, "level": 0}]
        mock_format.return_value = "Member 1 (ns: 0)"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["categorymembers", "Category:Test"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Member 1 (ns: 0)", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_category_members")
    @patch("wikipediaapi.cli.format_category_members")
    def test_categorymembers_command_json(self, mock_format, mock_get_members, mock_create_wiki):
        """Test categorymembers command with JSON output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_members.return_value = [{"title": "Member 1", "ns": 0, "level": 0}]
        mock_format.return_value = '[{"title": "Member 1", "ns": 0, "level": 0}]'

        result = self.runner.invoke(
            wikipediaapi.cli.cli, ["categorymembers", "Category:Test", "--json"]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn('[{"title": "Member 1", "ns": 0, "level": 0}]', result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_category_members")
    def test_categorymembers_command_page_not_found(self, mock_get_members, mock_create_wiki):
        """Test categorymembers command with non-existent category."""
        from wikipediaapi.cli import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_members.side_effect = PageNotFoundError("Page 'Category:Test' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["categorymembers", "Category:Test"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Page 'Category:Test' does not exist.", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_info")
    @patch("wikipediaapi.cli.format_page_info")
    def test_page_command_text(self, mock_format, mock_get_info, mock_create_wiki):
        """Test page command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_info.return_value = {"title": "Test Page", "exists": True, "pageid": 123}
        mock_format.return_value = "title: Test Page\nexists: True\npageid: 123"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["page", "Test_Page"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("title: Test Page", result.output)
        self.assertIn("exists: True", result.output)

    @patch("wikipediaapi.cli.create_wikipedia_instance")
    @patch("wikipediaapi.cli.get_page_info")
    @patch("wikipediaapi.cli.format_page_info")
    def test_page_command_json(self, mock_format, mock_get_info, mock_create_wiki):
        """Test page command with JSON output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_info.return_value = {"title": "Test Page", "exists": True}
        mock_format.return_value = '{"title": "Test Page", "exists": true}'

        result = self.runner.invoke(wikipediaapi.cli.cli, ["page", "Test_Page", "--json"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn('{"title": "Test Page", "exists": true}', result.output)

    def test_cli_help_command(self):
        """Test CLI help command."""
        result = self.runner.invoke(wikipediaapi.cli.cli, ["--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Command line tool for querying Wikipedia", result.output)
        self.assertIn("summary", result.output)
        self.assertIn("text", result.output)

    def test_cli_version_command(self):
        """Test CLI version command."""
        result = self.runner.invoke(wikipediaapi.cli.cli, ["--version"])

        self.assertEqual(result.exit_code, 0)
        # Version should be in output (format varies by click version)
        self.assertTrue(len(result.output.strip()) > 0)

    def test_legacy_print_page_dict_function(self):
        """Test the legacy _print_page_dict function for backward compatibility."""
        from unittest.mock import patch

        from wikipediaapi.cli import _print_page_dict

        # Create mock pages
        page1 = MagicMock()
        page1.title = "Page 1"
        page1.language = "en"
        page1.namespace = 0
        page1._attributes = {"fullurl": "https://en.wikipedia.org/wiki/Page_1"}

        pages = {"Page 1": page1}

        with patch("wikipediaapi.cli.click.echo") as mock_echo:
            _print_page_dict(pages, "text")
            mock_echo.assert_called_once()

    def test_main_function(self):
        """Test the main entry point function."""
        from unittest.mock import patch

        from wikipediaapi.cli import main

        with patch("wikipediaapi.cli.cli") as mock_cli:
            main()
            mock_cli.assert_called_once()


if __name__ == "__main__":
    unittest.main()
