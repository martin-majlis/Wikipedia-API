import pytest

import wikipediaapi
from tests.mock_data import async_wikipedia_api_request
from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request


class TestSyncAsyncPropertySymmetry:
    """Test that sync and async WikipediaPage have identical property behavior."""

    def setup_method(self):
        """Set up sync and async Wikipedia instances with mock data."""
        self.sync_wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.sync_wiki._get = wikipedia_api_request(self.sync_wiki)

        self.async_wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        self.async_wiki._get = async_wikipedia_api_request(self.async_wiki)

    @pytest.mark.asyncio
    async def test_property_symmetry_all_attributes(self):
        """Test that all properties return the same values in sync and async versions."""
        # Properties that should be available without any API call (construction-time)
        construction_props = ["title", "ns", "namespace", "language", "variant"]

        # Properties that require API calls and should be awaitable in async
        awaitable_props = [
            "pageid",
            "contentmodel",
            "pagelanguage",
            "pagelanguagehtmlcode",
            "pagelanguagedir",
            "lastrevid",
            "length",
            "protection",
            "restrictiontypes",
            "visitingwatchers",
            "notificationtimestamp",
            "talkid",
            "fullurl",
            "editurl",
            "canonicalurl",
            "readable",
            "preload",
            "displaytitle",
            "varianttitles",
            "summary",
            "text",
            "sections",
            "touched",
            "watchers",  # Added based on dir() discovery
        ]

        # Collection properties that return dicts (with different page types)
        collection_props = ["langlinks", "links", "backlinks", "categories"]

        # categorymembers only works on category pages
        category_collection_props = ["categorymembers"]

        # Methods
        methods = [
            "exists",
            "section_by_title",
            "sections_by_title",
        ]  # Added section methods based on dir() discovery

        # Test each page title with fresh instances
        test_titles = ["Test_1"]

        for title in test_titles:
            # Create fresh pages to get their full attribute lists
            sync_page = self.sync_wiki.page(title)
            async_page = self.async_wiki.page(title)

            # Get all attributes from both pages
            sync_attrs = set(dir(sync_page))
            async_attrs = set(dir(async_page))

            # Find attributes that exist in both versions
            common_attrs = sync_attrs & async_attrs

            # Filter out internal/private attributes (starting with _)
            public_attrs = {attr for attr in common_attrs if not attr.startswith("_")}

            # Verify all our expected properties are covered
            all_expected_props = set(
                construction_props
                + awaitable_props
                + collection_props
                + category_collection_props
                + methods
            )
            missing_props = all_expected_props - public_attrs
            assert len(missing_props) == 0, (
                f"Expected properties not found on pages: {missing_props}"
            )

            # Find any unexpected public attributes (excluding class-level constants)
            class_constants = {"ATTRIBUTES_MAPPING"}  # Class-level constants we don't need to test
            instance_attrs = {"wiki"}  # Instance attributes that don't need symmetry testing
            unexpected_props = public_attrs - all_expected_props - class_constants - instance_attrs
            if unexpected_props:
                print(
                    "Note: Found additional public attributes not in test lists: "
                    f"{sorted(unexpected_props)}"
                )

            # Test construction-time properties (no API call needed)
            for prop in construction_props:
                if prop in public_attrs:
                    # Create fresh pages for each property test
                    sync_page = self.sync_wiki.page(title)
                    async_page = self.async_wiki.page(title)

                    sync_value = getattr(sync_page, prop)
                    async_value = getattr(async_page, prop)
                    assert sync_value == async_value, (
                        f"Mismatch for {prop} on page '{title}': "
                        f"sync={sync_value}, async={async_value}"
                    )

            # Test awaitable properties
            for prop in awaitable_props:
                if prop in public_attrs:
                    # Create fresh pages for each property test
                    sync_page = self.sync_wiki.page(title)
                    async_page = self.async_wiki.page(title)

                    sync_value = getattr(sync_page, prop)
                    async_value = await getattr(async_page, prop)

                    # Special handling for sections - compare structure
                    # rather than exact equality
                    if prop == "sections":
                        self._compare_sections_structure(sync_value, async_value, title)
                    else:
                        assert sync_value == async_value, (
                            f"Mismatch for {prop} on page '{title}': "
                            f"sync={sync_value}, async={async_value}"
                        )

            # Test collection properties (compare keys and basic attributes, not types)
            for prop in collection_props:
                if prop in public_attrs:
                    # Create fresh pages for each property test
                    sync_page = self.sync_wiki.page(title)
                    async_page = self.async_wiki.page(title)

                    sync_collection = getattr(sync_page, prop)
                    async_collection = await getattr(async_page, prop)

                    # Compare keys
                    assert set(sync_collection.keys()) == set(async_collection.keys()), (
                        f"Keys differ for {prop} on page '{title}'"
                    )

                    # Compare basic attributes of page objects (not their types)
                    for key in sync_collection.keys():
                        if key in async_collection:  # Safety check
                            sync_item = sync_collection[key]
                            async_item = async_collection[key]

                            # Compare basic attributes that should be the same
                            basic_attrs = ["title", "ns", "language"]
                            for attr in basic_attrs:
                                if hasattr(sync_item, attr) and hasattr(async_item, attr):
                                    sync_attr_val = getattr(sync_item, attr)
                                    async_attr_val = getattr(async_item, attr)
                                    assert sync_attr_val == async_attr_val, (
                                        f"Mismatch for {prop}[{key}].{attr} on page '{title}'"
                                    )

            # Test categorymembers on a category page
            category_title = "Category:C1"
            for prop in category_collection_props:
                if prop in public_attrs:
                    # Create fresh pages for each property test
                    sync_category_page = self.sync_wiki.page(category_title)
                    async_category_page = self.async_wiki.page(category_title)

                    sync_collection = getattr(sync_category_page, prop)
                    async_collection = await getattr(async_category_page, prop)

                    # Compare keys
                    assert set(sync_collection.keys()) == set(async_collection.keys()), (
                        f"Keys differ for {prop} on page '{category_title}'"
                    )

                    # Compare basic attributes of page objects (not their types)
                    for key in sync_collection.keys():
                        if key in async_collection:  # Safety check
                            sync_item = sync_collection[key]
                            async_item = async_collection[key]

                            # Compare basic attributes that should be the same
                            basic_attrs = ["title", "ns", "language"]
                            for attr in basic_attrs:
                                if hasattr(sync_item, attr) and hasattr(async_item, attr):
                                    sync_attr_val = getattr(sync_item, attr)
                                    async_attr_val = getattr(async_item, attr)
                                    assert sync_attr_val == async_attr_val, (
                                        f"Mismatch for {prop}[{key}].{attr} "
                                        f"on page '{category_title}'"
                                    )

            # Test methods
            for method in methods:
                if method in public_attrs:
                    # Create fresh pages for each method test
                    sync_page = self.sync_wiki.page(title)
                    async_page = self.async_wiki.page(title)

                    # For section methods, ensure sections are loaded first
                    if method in ["section_by_title", "sections_by_title"]:
                        _ = sync_page.sections
                        _ = await async_page.sections
                        # Test with a section title that exists in Test_1
                        test_section_title = "Section 1"
                        sync_result = getattr(sync_page, method)(test_section_title)
                        async_result = getattr(async_page, method)(test_section_title)

                        # For section methods, compare attributes rather than objects
                        if method == "section_by_title":
                            if sync_result is None and async_result is None:
                                # Both None - good
                                pass
                            elif sync_result is not None and async_result is not None:
                                assert sync_result.title == async_result.title
                                assert sync_result.level == async_result.level
                                assert sync_result.text.strip() == async_result.text.strip()
                            else:
                                raise AssertionError(
                                    "One result is None, other is not: "
                                    f"sync={sync_result}, async={async_result}"
                                )
                        else:
                            assert len(sync_result) == len(async_result)
                            for _, (sync_sec, async_sec) in enumerate(
                                zip(sync_result, async_result, strict=False)
                            ):
                                assert sync_sec.title == async_sec.title
                                assert sync_sec.level == async_sec.level
                                assert sync_sec.text.strip() == async_sec.text.strip()
                    else:
                        # For other methods like exists()
                        sync_result = getattr(sync_page, method)()
                        async_result = await getattr(async_page, method)()
                        assert sync_result == async_result, (
                            f"Mismatch for {method}() on page '{title}': "
                            f"sync={sync_result}, async={async_result}"
                        )

    def _compare_sections_structure(self, sync_sections, async_sections, title):
        """Compare section structure rather than exact string equality."""
        assert len(sync_sections) == len(async_sections), (
            f"Section count differs for page '{title}'"
        )

        for i, (sync_sec, async_sec) in enumerate(zip(sync_sections, async_sections, strict=False)):
            assert sync_sec.title == async_sec.title, (
                f"Section {i} title differs for page '{title}'"
            )
            assert sync_sec.level == async_sec.level, (
                f"Section {i} level differs for page '{title}'"
            )
            assert sync_sec.text.strip() == async_sec.text.strip(), (
                f"Section {i} text differs for page '{title}'"
            )

            # Recursively compare subsections
            self._compare_sections_structure(
                sync_sec.sections, async_sec.sections, f"{title}-section-{i}"
            )

    @pytest.mark.asyncio
    async def test_sections_property_symmetry(self):
        """Specifically test sections property symmetry."""
        title = "Test_1"

        # Create fresh pages
        sync_page = self.sync_wiki.page(title)
        async_page = self.async_wiki.page(title)

        # Get sections from both
        sync_sections = sync_page.sections
        async_sections = await async_page.sections

        # Compare structure
        self._compare_sections_structure(sync_sections, async_sections, title)

    @pytest.mark.asyncio
    async def test_section_methods_symmetry(self):
        """Test section_by_title and sections_by_title methods."""
        title = "Test_1"  # Use a title that exists in mock data

        # Create fresh pages
        sync_page = self.sync_wiki.page(title)
        async_page = self.async_wiki.page(title)

        # Ensure sections are loaded
        _ = sync_page.sections
        _ = await async_page.sections

        # Test section_by_title
        test_title = "Section 1"  # Use a section that exists in Test_1
        sync_section = sync_page.section_by_title(test_title)
        async_section = async_page.section_by_title(test_title)

        if sync_section is None:
            assert async_section is None
        else:
            assert async_section is not None
            assert sync_section.title == async_section.title
            assert sync_section.level == async_section.level
            assert sync_section.text.strip() == async_section.text.strip()

        # Test sections_by_title - use a title that might have multiple sections
        # For Test_1, let's use a section that appears multiple times if available
        # Since Test_1 doesn't have duplicates, this will just test basic functionality
        sync_sections = sync_page.sections_by_title(test_title)
        async_sections = async_page.sections_by_title(test_title)

        assert len(sync_sections) == len(async_sections)
        for _, (sync_sec, async_sec) in enumerate(zip(sync_sections, async_sections, strict=False)):
            assert sync_sec.title == async_sec.title
            assert sync_sec.level == async_sec.level
            assert sync_sec.text.strip() == async_sec.text.strip()

    @pytest.mark.asyncio
    async def test_undocumented_attributes_symmetry(self):
        """Test that undocumented API fields are accessible in both versions."""
        title = "Test_1"

        # Create fresh pages
        sync_page = self.sync_wiki.page(title)
        async_page = self.async_wiki.page(title)

        # Trigger info fetch to load all attributes
        _ = sync_page.pageid
        _ = await async_page.pageid

        # Test access to undocumented field (present in mock data)
        undocumented_field = "api_new_experimental_field"

        # Both should allow access to undocumented fields
        sync_value = getattr(sync_page, undocumented_field, None)
        async_value = await getattr(async_page, undocumented_field, None)

        assert sync_value == async_value

    def test_property_availability(self):
        """Test that all documented properties are available in both classes."""
        # Get all documented properties from ATTRIBUTES_MAPPING
        documented_props = set(
            wikipediaapi._page._base_wikipedia_page.BaseWikipediaPage.ATTRIBUTES_MAPPING.keys()
        )

        # Check sync page has all properties
        sync_page = self.sync_wiki.page("Test_1")
        sync_props = set(dir(sync_page))
        for prop in documented_props:
            assert prop in sync_props, f"Sync page missing property: {prop}"

        # Check async page has all properties (using dir to avoid property access)
        async_page = self.async_wiki.page("Test_1")
        async_props = set(dir(async_page))
        for prop in documented_props:
            assert prop in async_props, f"Async page missing property: {prop}"

    @pytest.mark.asyncio
    async def test_text_property_symmetry(self):
        """Specifically test text property symmetry."""
        title = "Test_1"

        # Create fresh pages
        sync_page = self.sync_wiki.page(title)
        async_page = self.async_wiki.page(title)

        # Get text from both
        sync_text = sync_page.text
        async_text = await async_page.text

        assert sync_text.strip() == async_text.strip(), f"text property mismatch for page '{title}'"

    @pytest.mark.asyncio
    async def test_sections_auto_fetch_behavior(self):
        """Test that sections auto-fetches in both sync and async versions."""
        title = "Test_1"

        # Create fresh pages
        sync_page = self.sync_wiki.page(title)
        async_page = self.async_wiki.page(title)

        # Both should be able to access sections without prior API calls
        # Sync: direct access should trigger fetch
        sync_sections = sync_page.sections
        assert isinstance(sync_sections, list), "Sync sections should return a list"
        assert len(sync_sections) > 0, "Sync sections should not be empty"

        # Async: should return a coroutine that when awaited gives a list
        async_sections_coro = async_page.sections
        import asyncio

        assert asyncio.iscoroutine(async_sections_coro), "Async sections should return a coroutine"

        async_sections = await async_sections_coro
        assert isinstance(async_sections, list), "Async sections should return a list when awaited"
        assert len(async_sections) > 0, "Async sections should not be empty when awaited"

        # Compare structure
        self._compare_sections_structure(sync_sections, async_sections, title)


class TestWikipediaImageSymmetry:
    """Test that WikipediaImage and AsyncWikipediaImage have symmetric interfaces."""

    IMAGE_PROPERTIES = [
        "imageinfo",
        "pageid",
        "url",
        "width",
        "height",
        "size",
        "mime",
        "mediatype",
        "sha1",
        "timestamp",
        "user",
        "descriptionurl",
        "descriptionshorturl",
        "sections",
        "title",
        "ns",
        "language",
    ]

    IMAGE_METHODS = ["exists"]

    def test_sync_image_has_all_properties(self):
        """All expected properties exist on WikipediaImage."""
        wiki = wikipediaapi.Wikipedia(user_agent, "en")
        img = wikipediaapi.WikipediaImage(wiki, title="File:Test.png", ns=6, language="en")
        img_attrs = set(dir(img))
        for prop in self.IMAGE_PROPERTIES + self.IMAGE_METHODS:
            assert prop in img_attrs, f"WikipediaImage missing property: {prop}"

    def test_async_image_has_all_properties(self):
        """All expected properties exist on AsyncWikipediaImage."""
        wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        img = wikipediaapi.AsyncWikipediaImage(wiki, title="File:Test.png", ns=6, language="en")
        img_attrs = set(dir(img))
        for prop in self.IMAGE_PROPERTIES + self.IMAGE_METHODS:
            assert prop in img_attrs, f"AsyncWikipediaImage missing property: {prop}"

    def test_both_image_classes_have_same_public_properties(self):
        """Sync and async image classes expose the same public API surface."""
        wiki_sync = wikipediaapi.Wikipedia(user_agent, "en")
        wiki_async = wikipediaapi.AsyncWikipedia(user_agent, "en")
        sync_img = wikipediaapi.WikipediaImage(
            wiki_sync, title="File:Test.png", ns=6, language="en"
        )
        async_img = wikipediaapi.AsyncWikipediaImage(
            wiki_async, title="File:Test.png", ns=6, language="en"
        )
        sync_pub = {a for a in dir(sync_img) if not a.startswith("_")}
        async_pub = {a for a in dir(async_img) if not a.startswith("_")}
        for prop in self.IMAGE_PROPERTIES + self.IMAGE_METHODS:
            assert prop in sync_pub, f"WikipediaImage missing {prop}"
            assert prop in async_pub, f"AsyncWikipediaImage missing {prop}"
