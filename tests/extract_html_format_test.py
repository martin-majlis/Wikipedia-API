# -*- coding: utf-8 -*-
from collections import defaultdict
import unittest
from wikipedia import wikipedia

from mock_data import wikipedia_api_request


class TestHtmlFormatExtracts(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipedia.Wikipedia(
            "en",
            extract_format=wikipedia.ExtractFormat.HTML
        )
        self.wiki._query = wikipedia_api_request

    def test_title_before_fetching(self):
        page = self.wiki.article('Test_1')
        self.assertEqual(page.title, 'Test_1')

    def test_pageid(self):
        page = self.wiki.article('Test_1')
        self.assertEqual(page.pageid, 4)

    def test_title_after_fetching(self):
        page = self.wiki.article('Test_1')
        page.structured()
        self.assertEqual(page.title, 'Test 1')

    def test_summary(self):
        page = self.wiki.article('Test_1')
        self.assertEqual(page.summary, '<p><b>Summary</b> text\n\n</p>')

    def test_section_count(self):
        page = self.wiki.article('Test_1')
        self.assertEqual(len(page.sections), 5)

    def test_top_level_section_titles(self):
        page = self.wiki.article('Test_1')
        self.assertEqual(
            list(map(lambda s: s.title, page.sections)),
            ['Section ' + str(i + 1) for i in range(5)]
        )

    def test_subsection_by_title(self):
        page = self.wiki.article('Test_1')
        section = page.section_by_title('Section 4')
        self.assertEqual(section.title, 'Section 4')

    def test_subsection_by_title_with_multiple_spans(self):
        page = self.wiki.article('Test_1')
        section = page.section_by_title('Section 5')
        self.assertEqual(section.title, 'Section 5')

    def test_subsection(self):
        page = self.wiki.article('Test_1')
        section = page.section_by_title('Section 4')
        self.assertEqual(section.title, 'Section 4')
        self.assertEqual(section.text, '')
        self.assertEqual(len(section.sections), 2)

    def test_subsubsection(self):
        page = self.wiki.article('Test_1')
        section = page.section_by_title('Section 4.2.2')
        self.assertEqual(section.title, 'Section 4.2.2')
        self.assertEqual(
            section.text,
            '<p><b>Text for section 4.2.2</b>\n\n\n</p>'
        )
        self.assertEqual(len(section.sections), 0)
