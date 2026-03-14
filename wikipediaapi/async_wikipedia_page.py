from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .async_wikipedia import AsyncWikipedia

from .namespace import Namespace
from .namespace import namespace2int
from .namespace import WikiNamespace
from .wikipedia_page import PagesDict
from .wikipedia_page import WikipediaPage
from .wikipedia_page_section import WikipediaPageSection


class AsyncWikipediaPage:
    """
    Represents a Wikipedia page with asynchronous data-fetching methods.

    Except properties mentioned as part of documentation, there are also
    these properties available:

    * `fullurl` - full URL of the page
    * `canonicalurl` - canonical URL of the page
    * `pageid` - id of the current page
    * `displaytitle` - title of the page to display
    * `talkid` - id of the page with discussion

    """

    ATTRIBUTES_MAPPING = WikipediaPage.ATTRIBUTES_MAPPING

    def __init__(
        self,
        wiki: "AsyncWikipedia",
        title: str,
        ns: WikiNamespace = Namespace.MAIN,
        language: str = "en",
        variant: str | None = None,
        url: str | None = None,
    ) -> None:
        self.wiki = wiki
        self._summary = ""  # type: str
        self._section = []  # type: list[WikipediaPageSection]
        self._section_mapping = {}  # type: dict[str, list[WikipediaPageSection]]
        self._langlinks: PagesDict = {}
        self._links: PagesDict = {}
        self._backlinks: PagesDict = {}
        self._categories: PagesDict = {}
        self._categorymembers: PagesDict = {}

        self._called = {
            "extracts": False,
            "info": False,
            "langlinks": False,
            "links": False,
            "backlinks": False,
            "categories": False,
            "categorymembers": False,
        }

        self._attributes: dict[str, Any] = {
            "title": title,
            "ns": namespace2int(ns),
            "language": language,
            "variant": variant,
        }

        if url is not None:
            self._attributes["fullurl"] = url

    def __getattr__(self, name: str) -> Any:
        if name not in self.ATTRIBUTES_MAPPING:
            return self.__getattribute__(name)

        if name in self._attributes:
            return self._attributes[name]

        return None

    @property
    def language(self) -> str:
        """
        Returns language of the current page.

        :return: language
        """
        return str(self._attributes["language"])

    @property
    def variant(self) -> str | None:
        """
        Returns language variant of the current page.

        :return: language variant
        """
        v = self._attributes.get("variant")
        return str(v) if v is not None else None

    @property
    def title(self) -> str:
        """
        Returns title of the current page.

        :return: title
        """
        return str(self._attributes["title"])

    @property
    def ns(self) -> int:
        """
        Returns namespace of the current page.

        :return: namespace
        """
        return int(self._attributes["ns"])

    @property
    def sections(self) -> list[WikipediaPageSection]:
        """
        Returns sections of the current page (only populated after calling summary()).

        :return: sections
        """
        return self._section

    async def _fetch(self, call: str) -> "AsyncWikipediaPage":
        """Fetches data via the async wiki object."""
        await getattr(self.wiki, call)(self)
        self._called[call] = True
        return self

    async def summary(self) -> str:
        """
        Returns summary of the current page.

        :return: summary
        """
        if not self._called["extracts"]:
            await self._fetch("extracts")
        return self._summary

    async def langlinks(self) -> PagesDict:
        """
        Returns langlinks of the current page.

        :return: langlinks
        """
        if not self._called["langlinks"]:
            await self._fetch("langlinks")
        return self._langlinks

    async def links(self) -> PagesDict:
        """
        Returns links of the current page.

        :return: links
        """
        if not self._called["links"]:
            await self._fetch("links")
        return self._links

    async def backlinks(self) -> PagesDict:
        """
        Returns backlinks of the current page.

        :return: backlinks
        """
        if not self._called["backlinks"]:
            await self._fetch("backlinks")
        return self._backlinks

    async def categories(self) -> PagesDict:
        """
        Returns categories of the current page.

        :return: categories
        """
        if not self._called["categories"]:
            await self._fetch("categories")
        return self._categories

    async def categorymembers(self) -> PagesDict:
        """
        Returns categorymembers of the current page.

        :return: categorymembers
        """
        if not self._called["categorymembers"]:
            await self._fetch("categorymembers")
        return self._categorymembers

    def exists(self) -> bool:
        """
        Returns True if page exists, False otherwise.

        Note: this requires pageid to be set (e.g. after calling summary() or info()).

        :return: True if page exists
        """
        pageid = self._attributes.get("pageid")
        if pageid is None:
            return False
        return int(pageid) > 0

    def section_by_title(self, title: str) -> "WikipediaPageSection | None":
        """
        Returns the last section with the given title, or None.

        :param title: section title
        :return: section if it exists
        """
        sections = self._section_mapping.get(title, [])
        if sections:
            return sections[-1]
        return None

    def __repr__(self) -> str:
        return "AsyncWikipediaPage: {}\nNS: {}\nLanguage: {}\nVariant: {}".format(
            self.title,
            self.ns,
            self.language,
            self.variant,
        )
