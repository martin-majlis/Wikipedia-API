import wikipediaapi
from tests.mock_data import user_agent, wikipedia_api_request


class TestCategoryMembers:
    def setup_method(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_links_single_page_count(self):
        page = self.wiki.page("Category:C1")
        assert len(page.categorymembers) == 3

    def test_links_single_page_titles(self):
        page = self.wiki.page("Category:C1")
        assert sorted(s.title for s in page.categorymembers.values()) == [
            "Title - " + str(i + 1) for i in range(3)
        ]

    def test_links_multi_page_count(self):
        page = self.wiki.page("Category:C2")
        assert len(page.categorymembers) == 5

    def test_links_multi_page_titles(self):
        page = self.wiki.page("Category:C2")
        assert sorted(s.title for s in page.categorymembers.values()) == [
            "Title - " + str(i + 1) for i in range(5)
        ]
