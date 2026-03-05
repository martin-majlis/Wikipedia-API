from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .wikipedia import Wikipedia

from .namespace import Namespace
from .namespace import namespace2int
from .namespace import WikiNamespace
from .wikipedia_page_section import WikipediaPageSection

PagesDict = dict[str, "WikipediaPage"]


class WikipediaPage:
    """
    Represents Wikipedia page.

    Except properties mentioned as part of documentation, there are also
    these properties available:

    * `fullurl` - full URL of the page
    * `canonicalurl` - canonical URL of the page
    * `pageid` - id of the current page
    * `displaytitle` - title of the page to display
    * `talkid` - id of the page with discussion

    """

    ATTRIBUTES_MAPPING = {
        "language": [],
        "variant": [],
        "pageid": ["info", "extracts", "langlinks"],
        "ns": ["info", "extracts", "langlinks"],
        "title": ["info", "extracts", "langlinks"],
        "contentmodel": ["info"],
        "pagelanguage": ["info"],
        "pagelanguagehtmlcode": ["info"],
        "pagelanguagedir": ["info"],
        "touched": ["info"],
        "lastrevid": ["info"],
        "length": ["info"],
        "protection": ["info"],
        "restrictiontypes": ["info"],
        "watchers": ["info"],
        "visitingwatchers": ["info"],
        "notificationtimestamp": ["info"],
        "talkid": ["info"],
        "fullurl": ["info"],
        "editurl": ["info"],
        "canonicalurl": ["info"],
        "readable": ["info"],
        "preload": ["info"],
        "displaytitle": ["info"],
        "varianttitles": ["info"],
    }

    def __init__(
        self,
        wiki: "Wikipedia",
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
        self._langlinks = {}  # type: PagesDict
        self._links = {}  # type: PagesDict
        self._backlinks = {}  # type: PagesDict
        self._categories = {}  # type: PagesDict
        self._categorymembers = {}  # type: PagesDict

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

    def __getattr__(self, name):
        if name not in self.ATTRIBUTES_MAPPING:
            return self.__getattribute__(name)

        if name in self._attributes:
            return self._attributes[name]

        for call in self.ATTRIBUTES_MAPPING[name]:
            if not self._called[call]:
                self._fetch(call)
                return self._attributes[name]

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
        v = self._attributes["variant"]
        return str(v) if v else None

    @property
    def title(self) -> str:
        """
        Returns title of the current page.

        :return: title
        """
        return str(self._attributes["title"])

    @property
    def namespace(self) -> int:
        """
        Returns namespace of the current page.

        :return: namespace
        """
        return int(self._attributes["ns"])

    def exists(self) -> bool:
        """
        Returns `True` if the current page exists, otherwise `False`.

        :return: if current page existst or not
        """
        return bool(self.pageid != -1)

    @property
    def summary(self) -> str:
        """
        Returns summary of the current page.

        :return: summary
        """
        if not self._called["extracts"]:
            self._fetch("extracts")
        return self._summary

    @property
    def sections(self) -> list[WikipediaPageSection]:
        """
        Returns all sections of the curent page.

        :return: List of :class:`WikipediaPageSection`
        """
        if not self._called["extracts"]:
            self._fetch("extracts")
        return self._section

    def section_by_title(
        self,
        title: str,
    ) -> WikipediaPageSection | None:
        """
        Returns last section of the current page with given `title`.

        :param title: section title
        :return: :class:`WikipediaPageSection`
        """
        if not self._called["extracts"]:
            self._fetch("extracts")
        sections = self._section_mapping.get(title)
        if sections:
            return sections[-1]
        return None

    def sections_by_title(
        self,
        title: str,
    ) -> list[WikipediaPageSection]:
        """
        Returns all section of the current page with given `title`.

        :param title: section title
        :return: :class:`WikipediaPageSection`
        """
        if not self._called["extracts"]:
            self._fetch("extracts")
        sections = self._section_mapping.get(title)
        if sections is None:
            return []
        return sections

    @property
    def text(self) -> str:
        """
        Returns text of the current page.

        :return: text of the current page
        """
        txt = self.summary
        if len(txt) > 0:
            txt += "\n\n"
        for sec in self.sections:
            txt += sec.full_text(level=2)
        return txt.strip()

    @property
    def langlinks(self) -> PagesDict:
        """
        Returns all language links to pages in other languages.

        This is wrapper for:

        * https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blanglinks
        * https://www.mediawiki.org/wiki/API:Langlinks

        :return: :class:`PagesDict`
        """
        if not self._called["langlinks"]:
            self._fetch("langlinks")
        return self._langlinks

    @property
    def links(self) -> PagesDict:
        """
        Returns all pages linked from the current page.

        This is wrapper for:

        * https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blinks
        * https://www.mediawiki.org/wiki/API:Links

        :return: :class:`PagesDict`
        """
        if not self._called["links"]:
            self._fetch("links")
        return self._links

    @property
    def backlinks(self) -> PagesDict:
        """
        Returns all pages linking to the current page.

        This is wrapper for:

        * https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bbacklinks
        * https://www.mediawiki.org/wiki/API:Backlinks

        :return: :class:`PagesDict`
        """
        if not self._called["backlinks"]:
            self._fetch("backlinks")
        return self._backlinks

    @property
    def categories(self) -> PagesDict:
        """
        Returns categories associated with the current page.

        This is wrapper for:

        * https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategories
        * https://www.mediawiki.org/wiki/API:Categories

        :return: :class:`PagesDict`
        """
        if not self._called["categories"]:
            self._fetch("categories")
        return self._categories

    @property
    def categorymembers(self) -> PagesDict:
        """
        Returns all pages belonging to the current category.

        This is wrapper for:

        * https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategorymembers
        * https://www.mediawiki.org/wiki/API:Categorymembers

        :return: :class:`PagesDict`
        """
        if not self._called["categorymembers"]:
            self._fetch("categorymembers")
        return self._categorymembers

    def _fetch(self, call) -> "WikipediaPage":
        """Fetches some data?."""
        getattr(self.wiki, call)(self)
        self._called[call] = True
        return self

    def __repr__(self):
        r = f"{self.title} (lang: {self.language}, variant: {self.variant}, "
        if any(self._called.values()):
            r += f"id: {self.pageid}, "
        else:
            r += "id: ??, "

        r += f"ns: {self.ns})"
        return r
