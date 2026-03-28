from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi


class TestErrorsExtracts:
    def setup_method(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_title_before_fetching(self):
        page = self.wiki.page("NonExisting")
        assert page.title == "NonExisting"

    def test_pageid(self):
        page = self.wiki.page("NonExisting")
        assert page.pageid < 0
