import wikipediaapi
from tests.mock_data import user_agent, wikipedia_api_request


class TestCategories:
    def setup_method(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_categories_count(self):
        page = self.wiki.page("Test_1")
        assert len(page.categories) == 3

    def test_categories_titles(self):
        page = self.wiki.page("Test_1")
        assert sorted(s.title for s in page.categories.values()) == [
            "Category:C" + str(i + 1) for i in range(3)
        ]

    def test_categories_nss(self):
        page = self.wiki.page("Test_1")
        assert sorted(s.ns for s in page.categories.values()) == [14] * 3

    def test_no_categories_count(self):
        page = self.wiki.page("No_Categories")
        assert len(page.categories) == 0
