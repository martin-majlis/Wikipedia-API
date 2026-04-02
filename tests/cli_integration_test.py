"""Integration tests for CLI commands using Click's testing utilities."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

import wikipediaapi.cli
from tests.mock_data import create_mock_wikipedia


class TestCLICommands:
    """Test CLI command functions directly using Click's test runner."""

    def setup_method(self):
        self.runner = CliRunner()
        self.mock_wiki = create_mock_wikipedia()

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.page_commands.get_page_summary")
    def test_summary_command_success(self, mock_get_summary, mock_create_wiki):
        """Test summary command on successful page fetch."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_summary.return_value = "Test summary content"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["summary", "Test_Page"])

        assert result.exit_code == 0
        assert "Test summary content" in result.output
        mock_create_wiki.assert_called_once()
        mock_get_summary.assert_called_once()

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.page_commands.get_page_summary")
    def test_summary_command_page_not_found(self, mock_get_summary, mock_create_wiki):
        """Test summary command with non-existent page."""
        from wikipediaapi.commands.base import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_summary.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["summary", "Test_Page"])

        assert result.exit_code == 1
        assert "Page 'Test_Page' does not exist." in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.page_commands.get_page_text")
    def test_text_command_success(self, mock_get_text, mock_create_wiki):
        """Test text command on successful page fetch."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_text.return_value = "Full page text content"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["text", "Test_Page"])

        assert result.exit_code == 0
        assert "Full page text content" in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.page_commands.get_page_text")
    def test_text_command_page_not_found(self, mock_get_text, mock_create_wiki):
        """Test text command with non-existent page."""
        from wikipediaapi.commands.base import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_text.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["text", "Test_Page"])

        assert result.exit_code == 1
        assert "Page 'Test_Page' does not exist." in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.page_commands.get_page_sections")
    @patch("wikipediaapi.commands.base.format_sections")
    def test_sections_command_text(self, mock_format, mock_get_sections, mock_create_wiki):
        """Test sections command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_sections.return_value = [{"title": "Section 1", "level": 1, "indent": 0}]
        mock_format.return_value = "Section 1"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["sections", "Test_Page"])

        assert result.exit_code == 0
        assert "Section 1" in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.page_commands.get_page_sections")
    @patch("wikipediaapi.commands.base.format_sections")
    def test_sections_command_json(self, mock_format, mock_get_sections, mock_create_wiki):
        """Test sections command with JSON output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_sections.return_value = [{"title": "Section 1", "level": 1, "indent": 0}]
        mock_format.return_value = '[{"title": "Section 1", "level": 1, "indent": 0}]'

        result = self.runner.invoke(wikipediaapi.cli.cli, ["sections", "Test_Page", "--json"])

        assert result.exit_code == 0
        assert '"title": "Section 1"' in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.page_commands.get_page_sections")
    def test_sections_command_page_not_found(self, mock_get_sections, mock_create_wiki):
        """Test sections command with non-existent page."""
        from wikipediaapi.commands.base import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_sections.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["sections", "Test_Page"])

        assert result.exit_code == 1
        assert "Page 'Test_Page' does not exist." in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.page_commands.get_section_text")
    def test_section_command_success(self, mock_get_section, mock_create_wiki):
        """Test section command on successful fetch."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_section.return_value = "Section content here"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["section", "Test_Page", "Section_Name"])

        assert result.exit_code == 0
        assert "Section content here" in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.page_commands.get_section_text")
    def test_section_command_page_not_found(self, mock_get_section, mock_create_wiki):
        """Test section command with non-existent page."""
        from wikipediaapi.commands.base import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_section.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["section", "Test_Page", "Section_Name"])

        assert result.exit_code == 1
        assert "Page 'Test_Page' does not exist." in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.page_commands.get_section_text")
    def test_section_command_section_not_found(self, mock_get_section, mock_create_wiki):
        """Test section command with non-existent section."""
        from wikipediaapi.commands.page_commands import SectionNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_section.side_effect = SectionNotFoundError("Section 'Section_Name' not found.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["section", "Test_Page", "Section_Name"])

        assert result.exit_code == 1
        assert "Section 'Section_Name' not found." in result.output

    @patch("wikipediaapi.commands.link_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.link_commands.get_page_links")
    @patch("wikipediaapi.commands.base.format_page_dict")
    def test_links_command_text(self, mock_format, mock_get_links, mock_create_wiki):
        """Test links command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_links.return_value = {"Link 1": MagicMock(), "Link 2": MagicMock()}
        mock_format.return_value = "Link 1\nLink 2"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["links", "Test_Page"])

        assert result.exit_code == 0
        assert "Link 1" in result.output
        assert "Link 2" in result.output

    @patch("wikipediaapi.commands.link_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.link_commands.get_page_links")
    @patch("wikipediaapi.commands.base.format_page_dict")
    def test_links_command_json(self, mock_format, mock_get_links, mock_create_wiki):
        """Test links command with JSON output."""
        mock_create_wiki.return_value = self.mock_wiki

        # Create a mock page with required attributes for format_page_dict
        mock_page = MagicMock()
        mock_page.title = "Link 1"
        mock_page.language = "en"
        mock_page.namespace = 0
        mock_page._attributes = {"fullurl": "https://en.wikipedia.org/wiki/Link_1"}

        mock_get_links.return_value = {"Link 1": mock_page}
        mock_format.return_value = (
            '{\n  "Link 1": {\n    "title": "Link 1",\n    "language": "en",'
            '\n    "ns": 0,\n    "url": "https://en.wikipedia.org/wiki/Link_1"\n  }\n}'
        )

        result = self.runner.invoke(wikipediaapi.cli.cli, ["links", "Test_Page", "--json"])

        assert result.exit_code == 0
        assert '"title": "Link 1"' in result.output

    @patch("wikipediaapi.commands.link_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.link_commands.get_page_links")
    def test_links_command_page_not_found(self, mock_get_links, mock_create_wiki):
        """Test links command with non-existent page."""
        from wikipediaapi.commands.base import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_links.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["links", "Test_Page"])

        assert result.exit_code == 1
        assert "Page 'Test_Page' does not exist." in result.output

    @patch("wikipediaapi.commands.link_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.link_commands.get_page_backlinks")
    @patch("wikipediaapi.commands.base.format_page_dict")
    def test_backlinks_command_text(self, mock_format, mock_get_backlinks, mock_create_wiki):
        """Test backlinks command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_backlinks.return_value = {"Backlink 1": MagicMock(), "Backlink 2": MagicMock()}
        mock_format.return_value = "Backlink 1\nBacklink 2"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["backlinks", "Test_Page"])

        assert result.exit_code == 0
        assert "Backlink 1" in result.output
        assert "Backlink 2" in result.output

    @patch("wikipediaapi.commands.link_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.link_commands.get_page_backlinks")
    def test_backlinks_command_page_not_found(self, mock_get_backlinks, mock_create_wiki):
        """Test backlinks command with non-existent page."""
        from wikipediaapi.commands.base import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_backlinks.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["backlinks", "Test_Page"])

        assert result.exit_code == 1
        assert "Page 'Test_Page' does not exist." in result.output

    @patch("wikipediaapi.commands.link_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.link_commands.get_langlinks")
    @patch("wikipediaapi.commands.link_commands.format_langlinks")
    def test_langlinks_command_text(self, mock_format, mock_get_langlinks, mock_create_wiki):
        """Test langlinks command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_langlinks.return_value = {"de": MagicMock(), "fr": MagicMock()}
        mock_format.return_value = "de: German Title (url)\nfr: French Title (url)"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["langlinks", "Test_Page"])

        assert result.exit_code == 0
        assert "de: German Title" in result.output
        assert "fr: French Title" in result.output

    @patch("wikipediaapi.commands.link_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.link_commands.get_langlinks")
    @patch("wikipediaapi.commands.link_commands.format_langlinks")
    def test_langlinks_command_json(self, mock_format, mock_get_langlinks, mock_create_wiki):
        """Test langlinks command with JSON output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_langlinks.return_value = {"de": MagicMock()}
        mock_format.return_value = '{"de": {"title": "German Title"}}'

        result = self.runner.invoke(wikipediaapi.cli.cli, ["langlinks", "Test_Page", "--json"])

        assert result.exit_code == 0
        assert '{"de": {"title": "German Title"}}' in result.output

    @patch("wikipediaapi.commands.link_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.link_commands.get_langlinks")
    def test_langlinks_command_page_not_found(self, mock_get_langlinks, mock_create_wiki):
        """Test langlinks command with non-existent page."""
        from wikipediaapi.commands.base import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_langlinks.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["langlinks", "Test_Page"])

        assert result.exit_code == 1
        assert "Page 'Test_Page' does not exist." in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.category_commands.get_page_categories")
    @patch("wikipediaapi.commands.base.format_page_dict")
    def test_categories_command_text(self, mock_format, mock_get_categories, mock_create_wiki):
        """Test categories command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_categories.return_value = {"Category 1": MagicMock(), "Category 2": MagicMock()}
        mock_format.return_value = "Category 1\nCategory 2"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["categories", "Test_Page"])

        assert result.exit_code == 0
        assert "Category 1" in result.output
        assert "Category 2" in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.category_commands.get_page_categories")
    def test_categories_command_page_not_found(self, mock_get_categories, mock_create_wiki):
        """Test categories command with non-existent page."""
        from wikipediaapi.commands.base import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_categories.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["categories", "Test_Page"])

        assert result.exit_code == 1
        assert "Page 'Test_Page' does not exist." in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.category_commands.get_category_members")
    @patch("wikipediaapi.commands.category_commands.format_category_members")
    def test_categorymembers_command_text(self, mock_format, mock_get_members, mock_create_wiki):
        """Test categorymembers command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_members.return_value = [{"title": "Member 1", "ns": 0, "level": 0}]
        mock_format.return_value = "Member 1 (ns: 0)"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["categorymembers", "Category:Test"])

        assert result.exit_code == 0
        assert "Member 1 (ns: 0)" in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.category_commands.get_category_members")
    @patch("wikipediaapi.commands.category_commands.format_category_members")
    def test_categorymembers_command_json(self, mock_format, mock_get_members, mock_create_wiki):
        """Test categorymembers command with JSON output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_members.return_value = [{"title": "Member 1", "ns": 0, "level": 0}]
        mock_format.return_value = '[{"title": "Member 1", "ns": 0, "level": 0}]'

        result = self.runner.invoke(
            wikipediaapi.cli.cli, ["categorymembers", "Category:Test", "--json"]
        )

        assert result.exit_code == 0
        assert '[{"title": "Member 1", "ns": 0, "level": 0}]' in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.category_commands.get_category_members")
    def test_categorymembers_command_page_not_found(self, mock_get_members, mock_create_wiki):
        """Test categorymembers command with non-existent category."""
        from wikipediaapi.commands.base import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_members.side_effect = PageNotFoundError("Page 'Category:Test' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["categorymembers", "Category:Test"])

        assert result.exit_code == 1
        assert "Page 'Category:Test' does not exist." in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.page_commands.get_page_info")
    @patch("wikipediaapi.commands.base.format_page_info")
    def test_page_command_text(self, mock_format, mock_get_info, mock_create_wiki):
        """Test page command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_info.return_value = {"title": "Test Page", "exists": True, "pageid": 123}
        mock_format.return_value = "title: Test Page\nexists: True\npageid: 123"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["page", "Test_Page"])

        assert result.exit_code == 0
        assert "title: Test Page" in result.output
        assert "exists: True" in result.output

    @patch("wikipediaapi.commands.page_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.page_commands.get_page_info")
    @patch("wikipediaapi.commands.base.format_page_info")
    def test_page_command_json(self, mock_format, mock_get_info, mock_create_wiki):
        """Test page command with JSON output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_info.return_value = {"title": "Test Page", "exists": True}
        mock_format.return_value = '{"title": "Test Page", "exists": true}'

        result = self.runner.invoke(wikipediaapi.cli.cli, ["page", "Test_Page", "--json"])

        assert result.exit_code == 0
        assert '"title": "Test Page"' in result.output

    def test_cli_help_command(self):
        """Test CLI help command."""
        result = self.runner.invoke(wikipediaapi.cli.cli, ["--help"])

        assert result.exit_code == 0
        assert "Command line tool for querying Wikipedia" in result.output
        assert "summary" in result.output
        assert "text" in result.output

    def test_cli_version_command(self):
        """Test CLI version command."""
        result = self.runner.invoke(wikipediaapi.cli.cli, ["--version"])

        assert result.exit_code == 0
        # Version should be in output (format varies by click version)
        assert len(result.output.strip()) > 0

    def test_legacy_print_page_dict_function(self):
        """Test the legacy _print_page_dict function for backward compatibility."""
        from unittest.mock import patch

        from wikipediaapi.commands.base import _print_page_dict

        # Create mock pages
        page1 = MagicMock()
        page1.title = "Page 1"
        page1.language = "en"
        page1.namespace = 0
        page1._attributes = {"fullurl": "https://en.wikipedia.org/wiki/Page_1"}

        pages = {"Page 1": page1}

        with patch("wikipediaapi.commands.base.click.echo") as mock_echo:
            _print_page_dict(pages, "text")
            mock_echo.assert_called_once()

    def test_main_function(self):
        """Test the main entry point function."""
        from unittest.mock import patch

        from wikipediaapi.cli import main

        with patch("wikipediaapi.cli.cli") as mock_cli:
            main()
            mock_cli.assert_called_once()

    @patch("wikipediaapi.commands.image_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.image_commands.get_page_images")
    @patch("wikipediaapi.commands.image_commands.format_images")
    def test_images_command_text(self, mock_format, mock_get_images, mock_create_wiki):
        """Test images command with text output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_images.return_value = {"Image 1": MagicMock(), "Image 2": MagicMock()}
        mock_format.return_value = "Image 1\nImage 2"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["images", "Test_Page"])

        assert result.exit_code == 0
        assert "Image 1" in result.output
        assert "Image 2" in result.output

    @patch("wikipediaapi.commands.image_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.image_commands.get_page_images")
    @patch("wikipediaapi.commands.image_commands.format_images")
    def test_images_command_json(self, mock_format, mock_get_images, mock_create_wiki):
        """Test images command with JSON output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_images.return_value = {"Image 1": MagicMock()}

        # Create a mock image with required attributes
        mock_image = MagicMock()
        mock_image.title = "Image 1"
        mock_image.language = "en"
        mock_image.namespace = 6
        mock_image._attributes = {"fullurl": "https://example.com/Image1.jpg"}

        mock_get_images.return_value = {"Image 1": mock_image}
        mock_format.return_value = '{\n  "Image 1": {\n    "title": "Image 1"\n  }\n}'

        result = self.runner.invoke(wikipediaapi.cli.cli, ["images", "Test_Page", "--json"])

        assert result.exit_code == 0
        assert '"title": "Image 1"' in result.output

    @patch("wikipediaapi.commands.image_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.image_commands.get_page_images")
    @patch("wikipediaapi.commands.image_commands.format_images")
    def test_images_command_with_limit(self, mock_format, mock_get_images, mock_create_wiki):
        """Test images command with custom limit."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_images.return_value = {"Image 1": MagicMock()}
        mock_format.return_value = "Image 1"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["images", "Test_Page", "--limit", "5"])

        assert result.exit_code == 0
        assert "Image 1" in result.output
        mock_get_images.assert_called_once()

    @patch("wikipediaapi.commands.image_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.image_commands.get_page_images")
    @patch("wikipediaapi.commands.image_commands.format_images")
    def test_images_command_with_imageinfo(self, mock_format, mock_get_images, mock_create_wiki):
        """Test images command with imageinfo flag."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_images.return_value = {"Image 1": MagicMock()}
        mock_format.return_value = "Image 1 (https://example.com/Image1.jpg) 800x600 image/jpeg"

        result = self.runner.invoke(wikipediaapi.cli.cli, ["images", "Test_Page", "--imageinfo"])

        assert result.exit_code == 0
        assert "Image 1" in result.output

    @patch("wikipediaapi.commands.image_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.image_commands.get_page_images")
    @patch("wikipediaapi.commands.image_commands.format_images")
    def test_images_command_with_imageinfo_json(
        self, mock_format, mock_get_images, mock_create_wiki
    ):
        """Test images command with imageinfo flag and JSON output."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_images.return_value = {"Image 1": MagicMock()}
        mock_format.return_value = (
            '{\n  "Image 1": {\n    "title": "Image 1",'
            '\n    "imageinfo_url": "https://example.com/Image1.jpg"\n  }\n}'
        )

        result = self.runner.invoke(
            wikipediaapi.cli.cli, ["images", "Test_Page", "--imageinfo", "--json"]
        )

        assert result.exit_code == 0
        assert '"imageinfo_url": "https://example.com/Image1.jpg"' in result.output

    @patch("wikipediaapi.commands.image_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.image_commands.get_page_images")
    def test_images_command_page_not_found(self, mock_get_images, mock_create_wiki):
        """Test images command with non-existent page."""
        from wikipediaapi.commands.base import PageNotFoundError

        mock_create_wiki.return_value = self.mock_wiki
        mock_get_images.side_effect = PageNotFoundError("Page 'Test_Page' does not exist.")

        result = self.runner.invoke(wikipediaapi.cli.cli, ["images", "Test_Page"])

        assert result.exit_code == 1
        assert "Page 'Test_Page' does not exist." in result.output

    @patch("wikipediaapi.commands.image_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.image_commands.get_page_images")
    @patch("wikipediaapi.commands.image_commands.format_images")
    def test_images_command_with_language(self, mock_format, mock_get_images, mock_create_wiki):
        """Test images command with language option."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_images.return_value = {"Image 1": MagicMock()}
        mock_format.return_value = "Image 1"

        result = self.runner.invoke(
            wikipediaapi.cli.cli, ["images", "Test_Page", "--language", "de"]
        )

        assert result.exit_code == 0
        assert "Image 1" in result.output
        mock_create_wiki.assert_called_once()

    @patch("wikipediaapi.commands.image_commands.create_wikipedia_instance")
    @patch("wikipediaapi.commands.image_commands.get_page_images")
    @patch("wikipediaapi.commands.image_commands.format_images")
    def test_images_command_with_namespace(self, mock_format, mock_get_images, mock_create_wiki):
        """Test images command with namespace option."""
        mock_create_wiki.return_value = self.mock_wiki
        mock_get_images.return_value = {"Image 1": MagicMock()}
        mock_format.return_value = "Image 1"

        result = self.runner.invoke(
            wikipediaapi.cli.cli, ["images", "Test_Page", "--namespace", "6"]
        )

        assert result.exit_code == 0
        assert "Image 1" in result.output
