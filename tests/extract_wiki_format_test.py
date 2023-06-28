# -*- coding: utf-8 -*-
import unittest

from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi


class TestWikiFormatExtracts(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._query = wikipedia_api_request

    def test_title_before_fetching(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.title, "Test_1")

    def test_pageid(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.pageid, 4)

    def test_title_after_fetching(self):
        page = self.wiki.page("Test_1")
        page._fetch("extracts")
        self.assertEqual(page.title, "Test 1")

    def test_summary(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(page.summary, "Summary text")

    def test_section_count(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(len(page.sections), 5)

    def test_top_level_section_titles(self):
        page = self.wiki.page("Test_1")
        self.assertEqual(
            list(map(lambda s: s.title, page.sections)),
            ["Section " + str(i + 1) for i in range(5)],
        )

    def test_subsection_by_title(self):
        page = self.wiki.page("Test_1")
        section = page.section_by_title("Section 4")
        self.assertEqual(section.title, "Section 4")
        self.assertEqual(section.level, 1)

    def test_subsection(self):
        page = self.wiki.page("Test_1")
        section = page.section_by_title("Section 4")
        self.assertEqual(section.title, "Section 4")
        self.assertEqual(section.text, "")
        self.assertEqual(len(section.sections), 2)

    def test_subsubsection(self):
        page = self.wiki.page("Test_1")
        section = page.section_by_title("Section 4.2.2")
        self.assertEqual(section.title, "Section 4.2.2")
        self.assertEqual(section.text, "Text for section 4.2.2")
        self.assertEqual(
            repr(section),
            "Section: Section 4.2.2 (3):\n"
            + "Text for section 4.2.2\n"
            + "Subsections (0):\n",
        )
        self.assertEqual(len(section.sections), 0)

    def test_text(self):
        page = self.wiki.page("Test_1")
        self.maxDiff = None
        self.assertEqual(
            page.text,
            (
                "Summary text\n\n"
                + "Section 1\n"
                + "Text for section 1\n\n"
                + "Section 1.1\n"
                + "Text for section 1.1\n\n"
                + "Section 1.2\n"
                + "Text for section 1.2\n\n"
                + "Section 2\n"
                + "Text for section 2\n\n"
                + "Section 3\n"
                + "Text for section 3\n\n"
                + "Section 4\n"
                + "Section 4.1\n"
                + "Text for section 4.1\n\n"
                + "Section 4.2\n"
                + "Text for section 4.2\n\n"
                + "Section 4.2.1\n"
                + "Text for section 4.2.1\n\n"
                + "Section 4.2.2\n"
                + "Text for section 4.2.2\n\n"
                + "Section 5\n"
                + "Text for section 5\n\n"
                + "Section 5.1\n"
                + "Text for section 5.1"
            ),
        )

    def test_text_and_summary_without_sections(self):
        page = self.wiki.page("No_Sections")
        self.maxDiff = None
        self.assertEqual(page.text, ("Summary text"))
        self.assertEqual(page.summary, ("Summary text"))
