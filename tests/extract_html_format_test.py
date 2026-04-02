import wikipediaapi
from tests.mock_data import user_agent, wikipedia_api_request


class TestHtmlFormatExtracts:
    def setup_method(self):
        self.wiki = wikipediaapi.Wikipedia(
            user_agent, "en", extract_format=wikipediaapi.ExtractFormat.HTML
        )
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_title_before_fetching(self):
        page = self.wiki.page("Test_1")
        assert page.title == "Test_1"

    def test_pageid(self):
        page = self.wiki.page("Test_1")
        assert page.pageid == 4

    def test_title_after_fetching(self):
        page = self.wiki.page("Test_1")
        page._fetch("extracts")
        assert page.title == "Test 1"

    def test_summary(self):
        page = self.wiki.page("Test_1")
        assert page.summary == "<p><b>Summary</b> text\n\n</p>"

    def test_section_count(self):
        page = self.wiki.page("Test_1")
        assert len(page.sections) == 5

    def test_top_level_section_titles(self):
        page = self.wiki.page("Test_1")
        assert [s.title for s in page.sections] == ["Section " + str(i + 1) for i in range(5)]

    def test_subsection_by_title(self):
        page = self.wiki.page("Test_1")
        section = page.section_by_title("Section 4")
        assert section.title == "Section 4"
        assert section.level == 1

    def test_subsection_by_title_with_multiple_spans(self):
        page = self.wiki.page("Test_1")
        section = page.section_by_title("Section 5")
        assert section.title == "Section 5"

    def test_subsection(self):
        page = self.wiki.page("Test_1")
        section = page.section_by_title("Section 4")
        assert section.title == "Section 4"
        assert section.text == ""
        assert len(section.sections) == 2

    def test_subsubsection(self):
        page = self.wiki.page("Test_1")
        section = page.section_by_title("Section 4.2.2")
        assert section.title == "Section 4.2.2"
        assert section.text == "<p><b>Text for section 4.2.2</b>\n\n\n</p>"
        assert (
            repr(section)
            == "Section: Section 4.2.2 (3):\n"
            + "<p><b>Text for section 4.2.2</b>\n\n\n</p>\n"
            + "Subsections (0):\n"
        )
        assert len(section.sections) == 0

    def test_subsection_by_title_return_last(self):
        page = self.wiki.page("Test_Nested")
        section = page.section_by_title("Subsection B")
        assert section.title == "Subsection B"
        assert section.text == "<p><b>Text for section 3.B</b>\n\n\n</p>"
        assert len(section.sections) == 0

    def test_subsections_by_title(self):
        page = self.wiki.page("Test_Nested")
        sections = page.sections_by_title("Subsection B")
        assert len(sections) == 3
        assert [s.text for s in sections] == [
            "<p><b>Text for section 1.B</b>\n\n\n</p>",
            "<p><b>Text for section 2.B</b>\n\n\n</p>",
            "<p><b>Text for section 3.B</b>\n\n\n</p>",
        ]

    def test_text(self):
        page = self.wiki.page("Test_1")
        expected = (
            "<p><b>Summary</b> text\n\n</p>\n\n"
            + "<h2>Section 1</h2>\n"
            + "<p>Text for section 1</p>\n\n"
            + "<h3>Section 1.1</h3>\n"
            + "<p><b>Text for section 1.1</b>\n\n\n</p>\n\n"
            + "<h3>Section 1.2</h3>\n"
            + "<p><b>Text for section 1.2</b>\n\n\n</p>\n\n"
            + "<h2>Section 2</h2>\n"
            + "<p><b>Text for section 2</b>\n\n\n</p>\n\n"
            + "<h2>Section 3</h2>\n"
            + "<p><b>Text for section 3</b>\n\n\n</p>\n\n"
            + "<h2>Section 4</h2>\n"
            + "<h3>Section 4.1</h3>\n"
            + "<p><b>Text for section 4.1</b>\n\n\n</p>\n\n"
            + "<h3>Section 4.2</h3>\n"
            + "<p><b>Text for section 4.2</b>\n\n\n</p>\n\n"
            + "<h4>Section 4.2.1</h4>\n"
            + "<p><b>Text for section 4.2.1</b>\n\n\n</p>\n\n"
            + "<h4>Section 4.2.2</h4>\n"
            + "<p><b>Text for section 4.2.2</b>\n\n\n</p>\n\n"
            + "<h2>Section 5</h2>\n"
            + "<p><b>Text for section 5</b>\n\n\n</p>\n\n"
            + "<h3>Section 5.1</h3>\n"
            + "<p>Text for section 5.1\n\n\n</p>"
        )
        assert page.text == expected

    def test_with_erroneous_edit(self):
        page = self.wiki.page("Test_Edit")
        self.maxDiff = None
        section = page.section_by_title("Section with Edit")
        assert section.title == "Section with Edit"
        expected = (
            "<p><b>Summary</b> text\n\n</p>\n\n"
            + "<h2>Section 1</h2>\n"
            + "<p>Text for section 1</p>\n\n"
            "<h3>Section with Edit</h3>\n" + "<p>Text for section with edit\n\n\n</p>"
        )
        assert page.text == expected
