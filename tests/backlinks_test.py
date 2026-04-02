import wikipediaapi
from tests.mock_data import user_agent, wikipedia_api_request


class TestBackLinks:
    def setup_method(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_backlinks_nonexistent_count(self):
        page = self.wiki.page("Non_Existent")
        assert len(page.backlinks) == 0

    def test_backlinks_single_page_count(self):
        page = self.wiki.page("Test_1")
        assert len(page.backlinks) == 3

    def test_backlinks_single_page_titles(self):
        page = self.wiki.page("Test_1")
        assert sorted(s.title for s in page.backlinks.values()) == [
            "Title - " + str(i + 1) for i in range(3)
        ]

    def test_backlinks_multi_page_count(self):
        page = self.wiki.page("Test_2")
        assert len(page.backlinks) == 5

    def test_backlinks_multi_page_titles(self):
        page = self.wiki.page("Test_2")
        assert sorted(s.title for s in page.backlinks.values()) == [
            "Title - " + str(i + 1) for i in range(5)
        ]
