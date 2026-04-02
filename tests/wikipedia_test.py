from unittest.mock import MagicMock

import pytest

import wikipediaapi
from tests.mock_data import user_agent


class TestWikipedia:
    def test_missing_user_agent_should_fail(self):
        with pytest.raises(AssertionError) as e:
            wikipediaapi.Wikipedia("en")
        assert str(e.value) == str(
            AssertionError(
                "Please, be nice to Wikipedia and specify user agent - "
                + "https://meta.wikimedia.org/wiki/User-Agent_policy. "
                + "Current user_agent: 'en' is not sufficient. "
                + "Use Wikipedia(user_agent='your-user-agent', language='en')"
            )
        )

    def test_swapped_parameters_in_constructor(self):
        with pytest.raises(AssertionError) as e:
            wikipediaapi.Wikipedia("en", "my-user-agent")
        assert str(e.value) == str(
            AssertionError(
                "Please, be nice to Wikipedia and specify user agent - "
                + "https://meta.wikimedia.org/wiki/User-Agent_policy. "
                + "Current user_agent: 'en' is not sufficient. "
                + "Use Wikipedia(user_agent='your-user-agent', language='en')"
            )
        )

    def test_empty_parameters_in_constructor(self):
        with pytest.raises(AssertionError) as e:
            wikipediaapi.Wikipedia("", "")
        assert str(e.value) == str(
            AssertionError(
                "Please, be nice to Wikipedia and specify user agent - "
                + "https://meta.wikimedia.org/wiki/User-Agent_policy. "
                + "Current user_agent: '' is not sufficient. "
                + "Use Wikipedia(user_agent='your-user-agent', language='your-language')"
            )
        )

    def test_empty_language_in_constructor(self):
        with pytest.raises(AssertionError) as e:
            wikipediaapi.Wikipedia("test-user-agent", "")
        assert str(e.value) == str(
            AssertionError(
                "Specify language. Current language: '' is not sufficient. "
                + "Use Wikipedia(user_agent='test-user-agent', language='your-language')"
            )
        )

    def test_long_language_and_user_agent(self):
        wiki = wikipediaapi.Wikipedia(user_agent="param-user-agent", language="very-long-language")
        assert wiki is not None
        assert wiki.language == "very-long-language"
        assert wiki.variant is None

    def test_user_agent_is_used(self):
        wiki = wikipediaapi.Wikipedia(
            user_agent="param-user-agent",
        )
        assert wiki is not None
        user_agent = wiki._client.headers.get("User-Agent")
        assert user_agent == "param-user-agent (" + wikipediaapi.USER_AGENT + ")"
        assert wiki.language == "en"

    def test_user_agent_in_headers_is_fine(self):
        wiki = wikipediaapi.Wikipedia(
            "en",
            headers={"User-Agent": "header-user-agent"},
        )
        assert wiki is not None
        user_agent = wiki._client.headers.get("User-Agent")
        assert user_agent == "header-user-agent (" + wikipediaapi.USER_AGENT + ")"

    def test_user_agent_in_headers_win(self):
        wiki = wikipediaapi.Wikipedia(
            user_agent="param-user-agent",
            headers={"User-Agent": "header-user-agent"},
        )
        assert wiki is not None
        user_agent = wiki._client.headers.get("User-Agent")
        assert user_agent == "header-user-agent (" + wikipediaapi.USER_AGENT + ")"

    def test_extracts_nonexistent_page(self):
        """Test extracts method when page doesn't exist (pageid is negative)."""
        wiki = wikipediaapi.Wikipedia(user_agent, "en")

        page = MagicMock()
        page.language = "en"
        page._attributes = {}

        # Mock the API response to return missing page marker (nonexistent page)
        def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get  # ty: ignore[invalid-assignment]

        result = wiki.extracts(page)
        assert result == ""
        # The pageid should be set to a negative value in the attributes
        assert "pageid" in page._attributes
        assert page._attributes["pageid"] < 0

    def test_info_nonexistent_page(self):
        """Test info method when page doesn't exist (pageid is negative)."""
        wiki = wikipediaapi.Wikipedia(user_agent, "en")

        page = MagicMock()
        page.language = "en"
        page._attributes = {}

        # Mock the API response to return missing page marker (nonexistent page)
        def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get  # ty: ignore[invalid-assignment]

        result = wiki.info(page)
        assert result == page

    def test_langlinks_nonexistent_page(self):
        """Test langlinks method when page doesn't exist (pageid is negative)."""
        wiki = wikipediaapi.Wikipedia(user_agent, "en")

        page = MagicMock()
        page.language = "en"
        page._attributes = {}

        # Mock the API response to return missing page marker (nonexistent page)
        def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get  # ty: ignore[invalid-assignment]

        result = wiki.langlinks(page)
        assert result == {}
        # The pageid should be set to a negative value in the attributes
        assert "pageid" in page._attributes
        assert page._attributes["pageid"] < 0

    def test_links_nonexistent_page(self):
        """Test links method when page doesn't exist (pageid is negative)."""
        wiki = wikipediaapi.Wikipedia(user_agent, "en")

        page = MagicMock()
        page.language = "en"
        page._attributes = {}

        # Mock the API response to return missing page marker (nonexistent page)
        def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get  # ty: ignore[invalid-assignment]

        result = wiki.links(page)
        assert result == {}
        # The pageid should be set to a negative value in the attributes
        assert "pageid" in page._attributes
        assert page._attributes["pageid"] < 0

    def test_backlinks_nonexistent_page(self):
        """Test backlinks method when page doesn't exist (pageid is negative)."""
        wiki = wikipediaapi.Wikipedia(user_agent, "en")

        page = MagicMock()
        page.language = "en"
        page._attributes = {}

        # Mock the API response to return missing page marker (nonexistent page)
        def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get  # ty: ignore[invalid-assignment]

        result = wiki.backlinks(page)
        assert result == {}

    def test_categories_nonexistent_page(self):
        """Test categories method when page doesn't exist (pageid is negative)."""
        wiki = wikipediaapi.Wikipedia(user_agent, "en")

        page = MagicMock()
        page.language = "en"
        page._attributes = {}

        # Mock the API response to return missing page marker (nonexistent page)
        def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get  # ty: ignore[invalid-assignment]

        result = wiki.categories(page)
        assert result == {}

    def test_categorymembers_nonexistent_page(self):
        """Test categorymembers method when page doesn't exist (pageid is negative)."""
        wiki = wikipediaapi.Wikipedia(user_agent, "en")

        page = MagicMock()
        page.language = "en"
        page._attributes = {}

        # Mock the API response to return missing page marker (nonexistent page)
        def mock_get(language, params):
            return {"query": {"pages": {"-1": {}}}}

        wiki._get = mock_get  # ty: ignore[invalid-assignment]

        result = wiki.categorymembers(page)
        assert result == {}
