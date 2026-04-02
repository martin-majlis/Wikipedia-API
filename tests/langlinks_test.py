import wikipediaapi
from tests.mock_data import user_agent, wikipedia_api_request


class TestLangLinks:
    def setup_method(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_langlinks_count(self):
        page = self.wiki.page("Test_1")
        assert len(page.langlinks) == 3

    def test_langlinks_titles(self):
        page = self.wiki.page("Test_1")
        assert sorted(s.title for s in page.langlinks.values()) == [
            "Test 1 - " + str(i + 1) for i in range(3)
        ]

    def test_langlinks_lang_values(self):
        page = self.wiki.page("Test_1")
        assert sorted(s.language for s in page.langlinks.values()) == [
            "l" + str(i + 1) for i in range(3)
        ]

    def test_langlinks_lang_keys(self):
        page = self.wiki.page("Test_1")
        assert sorted(page.langlinks.keys()) == ["l" + str(i + 1) for i in range(3)]

    def test_langlinks_urls(self):
        page = self.wiki.page("Test_1")
        assert sorted(s.fullurl for s in page.langlinks.values()) == [
            ("https://l" + str(i + 1) + ".wikipedia.org/wiki/Test_1_-_" + str(i + 1))
            for i in range(3)
        ]

    def test_jump_between_languages(self):
        page = self.wiki.page("Test_1")
        langlinks = page.langlinks
        p1 = langlinks["l1"]
        assert p1.language == "l1"
        assert p1.pageid == 10

    def test_langlinks_no_langlink_count(self):
        page = self.wiki.page("No_LangLinks")
        assert len(page.langlinks) == 0
