"""
Wikipedia-API is easy to use wrapper for extracting information from Wikipedia.

It supports extracting texts, sections, links, categories, translations, etc.
from Wikipedia. Documentation provides code snippets for the most common use
cases.
"""

__version__ = (0, 6, 0)
from collections import defaultdict
from enum import IntEnum
import logging
import re
from typing import Any, Dict, List, Optional, Union
from urllib import parse

import requests

USER_AGENT = (
    "Wikipedia-API/"
    + ".".join(str(s) for s in __version__)
    + "; https://github.com/martin-majlis/Wikipedia-API/"
)

log = logging.getLogger(__name__)


# https://www.mediawiki.org/wiki/API:Main_page
PagesDict = Dict[str, "WikipediaPage"]


class ExtractFormat(IntEnum):
    """Represents extraction format."""

    WIKI = 1
    """
    Allows recognizing subsections

    Example: https://goo.gl/PScNVV
    """

    HTML = 2
    """
    Alows retrieval of HTML tags

    Example: https://goo.gl/1Jwwpr
    """

    # Plain: https://goo.gl/MAv2qz
    # Doesn't allow to recognize subsections
    # PLAIN = 3


class Namespace(IntEnum):
    """
    Represents namespace in Wikipedia

    You can gen list of possible namespaces here:

    * https://en.wikipedia.org/wiki/Wikipedia:Namespace
    * https://en.wikipedia.org/wiki/Wikipedia:Namespace#Programming

    Currently following namespaces are supported:
    """

    MAIN = 0
    TALK = 1
    USER = 2
    USER_TALK = 3
    WIKIPEDIA = 4
    WIKIPEDIA_TALK = 5
    FILE = 6
    FILE_TALK = 7
    MEDIAWIKI = 8
    MEDIAWIKI_TALK = 9
    TEMPLATE = 10
    TEMPLATE_TALK = 11
    HELP = 12
    HELP_TALK = 13
    CATEGORY = 14
    CATEGORY_TALK = 15
    PORTAL = 100
    PORTAL_TALK = 101
    PROJECT = 102
    PROJECT_TALK = 103
    REFERENCE = 104
    REFERENCE_TALK = 105
    BOOK = 108
    BOOK_TALK = 109
    DRAFT = 118
    DRAFT_TALK = 119
    EDUCATION_PROGRAM = 446
    EDUCATION_PROGRAM_TALK = 447
    TIMED_TEXT = 710
    TIMED_TEXT_TALK = 711
    MODULE = 828
    MODULE_TALK = 829
    GADGET = 2300
    GADGET_TALK = 2301
    GADGET_DEFINITION = 2302
    GADGET_DEFINITION_TALK = 2303


WikiNamespace = Union[Namespace, int]


def namespace2int(namespace: WikiNamespace) -> int:
    """Converts namespace into integer"""
    if isinstance(namespace, Namespace):
        return namespace.value

    return namespace


RE_SECTION = {
    ExtractFormat.WIKI: re.compile(r"\n\n *(==+) (.*?) (==+) *\n"),
    ExtractFormat.HTML: re.compile(
        r"\n? *<h([1-9])[^>]*?>(<span[^>]*></span>)? *"
        + "(<span[^>]*>)? *(<span[^>]*></span>)? *(.*?) *"
        + "(</span>)?(<span>Edit</span>)?</h[1-9]>\n?"
        #                  ^^^^
        # Example page with 'Edit' erroneous links: https://bit.ly/2ui4FWs
    ),
    # ExtractFormat.PLAIN.value: re.compile(r'\n\n *(===*) (.*?) (===*) *\n'),
}


class Wikipedia:
    """Wikipedia is wrapper for Wikipedia API."""

    def __init__(
        self,
        user_agent: str,
        language: str = "en",
        extract_format: ExtractFormat = ExtractFormat.WIKI,
        headers: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """
        Constructs Wikipedia object for extracting information Wikipedia.

        :param user_agent: HTTP User-Agent used in requests
                https://meta.wikimedia.org/wiki/User-Agent_policy
        :param language: Language mutation of Wikipedia -
                http://meta.wikimedia.org/wiki/List_of_Wikipedias
        :param extract_format: Format used for extractions
                :class:`ExtractFormat` object.
        :param headers:  Headers sent as part of HTTP request
        :param kwargs: Optional parameters used in -
                http://docs.python-requests.org/en/master/api/#requests.request

        Examples:

        * Proxy: ``Wikipedia('foo (merlin@example.com)', proxies={'http': 'http://proxy:1234'})``
        """
        kwargs.setdefault("timeout", 10.0)

        default_headers = {} if headers is None else headers
        if user_agent:
            default_headers.setdefault(
                "User-Agent",
                user_agent,
            )
        used_user_agent = default_headers.get("User-Agent")
        if not (used_user_agent and len(used_user_agent) > 5):
            raise AssertionError(
                "Please, be nice to Wikipedia and specify user agent - "
                + "https://meta.wikimedia.org/wiki/User-Agent_policy. Current user_agent: '"
                + str(used_user_agent)
                + "' is not sufficient."
            )
        default_headers["User-Agent"] += " (" + USER_AGENT + ")"

        self.language = language.strip().lower()
        if not self.language:
            raise AssertionError(
                "Specify language. Current language: '"
                + str(self.language)
                + "' is not sufficient."
            )
        self.extract_format = extract_format

        log.info(
            "Wikipedia: language=%s, user_agent: %s, extract_format=%s",
            self.language,
            default_headers["User-Agent"],
            self.extract_format,
        )

        self._session = requests.Session()
        self._session.headers.update(default_headers)
        self._request_kwargs = kwargs

    def __del__(self) -> None:
        """Closes session."""
        if hasattr(self, "_session") and self._session:
            self._session.close()

    def page(
        self,
        title: str,
        ns: WikiNamespace = Namespace.MAIN,
        unquote: bool = False,
    ) -> "WikipediaPage":
        """
        Constructs Wikipedia page with title `title`.

        Creating `WikipediaPage` object is always the first step for extracting
        any information.

        Example::

            wiki_wiki = wikipediaapi.Wikipedia('en')
            page_py = wiki_wiki.page('Python_(programming_language)')
            print(page_py.title)
            # Python (programming language)

            wiki_hi = wikipediaapi.Wikipedia('hi')

            page_hi_py = wiki_hi.article(
                title='%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8',
                unquote=True,
            )
            print(page_hi_py.title)
            # पाइथन

        :param title: page title as used in Wikipedia URL
        :param ns: :class:`WikiNamespace`
        :param unquote: if true it will unquote title
        :return: object representing :class:`WikipediaPage`
        """
        if unquote:
            title = parse.unquote(title)

        return WikipediaPage(self, title=title, ns=ns, language=self.language)

    def article(
        self, title: str, ns: WikiNamespace = Namespace.MAIN, unquote: bool = False
    ) -> "WikipediaPage":
        """
        Constructs Wikipedia page with title `title`.

        This function is an alias for :func:`page`

        :param title: page title as used in Wikipedia URL
        :param ns: :class:`WikiNamespace`
        :param unquote: if true it will unquote title
        :return: object representing :class:`WikipediaPage`
        """
        return self.page(
            title=title,
            ns=ns,
            unquote=unquote,
        )

    def extracts(self, page: "WikipediaPage", **kwargs) -> str:
        """
        Returns summary of the page with respect to parameters

        Parameter `exsectionformat` is taken from `Wikipedia` constructor.

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bextracts
        - https://www.mediawiki.org/wiki/Extension:TextExtracts#API

        Example::

            import wikipediaapi
            wiki = wikipediaapi.Wikipedia('en')

            page = wiki.page('Python_(programming_language)')
            print(wiki.extracts(page, exsentences=1))
            print(wiki.extracts(page, exsentences=2))

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: summary of the page

        """
        params = {
            "action": "query",
            "prop": "extracts",
            "titles": page.title,
        }  # type: Dict[str, Any]

        if self.extract_format == ExtractFormat.HTML:
            # we do nothing, when format is HTML
            pass
        elif self.extract_format == ExtractFormat.WIKI:
            params["explaintext"] = 1
            params["exsectionformat"] = "wiki"

        used_params = kwargs
        used_params.update(params)

        raw = self._query(page, used_params)
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return ""
            return self._build_extracts(v, page)
        return ""

    def info(self, page: "WikipediaPage") -> "WikipediaPage":
        """
        https://www.mediawiki.org/w/api.php?action=help&modules=query%2Binfo
        https://www.mediawiki.org/wiki/API:Info
        """
        params = {
            "action": "query",
            "prop": "info",
            "titles": page.title,
            "inprop": "|".join(
                [
                    "protection",
                    "talkid",
                    "watched",
                    "watchers",
                    "visitingwatchers",
                    "notificationtimestamp",
                    "subjectid",
                    "url",
                    "readable",
                    "preload",
                    "displaytitle",
                ]
            ),
        }
        raw = self._query(page, params)
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return page

            return self._build_info(v, page)
        return page

    def langlinks(self, page: "WikipediaPage", **kwargs) -> PagesDict:
        """
        Returns langlinks of the page with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blanglinks
        - https://www.mediawiki.org/wiki/API:Langlinks

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: links to pages in other languages

        """
        params = {
            "action": "query",
            "prop": "langlinks",
            "titles": page.title,
            "lllimit": 500,
            "llprop": "url",
        }

        used_params = kwargs
        used_params.update(params)

        raw = self._query(page, used_params)
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return {}
            return self._build_langlinks(v, page)
        return {}

    def links(self, page: "WikipediaPage", **kwargs) -> PagesDict:
        """
        Returns links to other pages with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blinks
        - https://www.mediawiki.org/wiki/API:Links

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: links to linked pages

        """
        params = {
            "action": "query",
            "prop": "links",
            "titles": page.title,
            "pllimit": 500,
        }

        used_params = kwargs
        used_params.update(params)

        raw = self._query(page, used_params)
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return {}

            while "continue" in raw:
                params["plcontinue"] = raw["continue"]["plcontinue"]
                raw = self._query(page, params)
                v["links"] += raw["query"]["pages"][k]["links"]

            return self._build_links(v, page)
        return {}

    def backlinks(self, page: "WikipediaPage", **kwargs) -> PagesDict:
        """
        Returns backlinks from other pages with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bbacklinks
        - https://www.mediawiki.org/wiki/API:Backlinks

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: backlinks from other pages

        """
        params = {
            "action": "query",
            "list": "backlinks",
            "bltitle": page.title,
            "bllimit": 500,
        }

        used_params = kwargs
        used_params.update(params)

        raw = self._query(page, used_params)

        self._common_attributes(raw["query"], page)
        v = raw["query"]
        while "continue" in raw:
            params["blcontinue"] = raw["continue"]["blcontinue"]
            raw = self._query(page, params)
            v["backlinks"] += raw["query"]["backlinks"]
        return self._build_backlinks(v, page)

    def categories(self, page: "WikipediaPage", **kwargs) -> PagesDict:
        """
        Returns categories for page with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategories
        - https://www.mediawiki.org/wiki/API:Categories

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: categories for page
        """
        params = {
            "action": "query",
            "prop": "categories",
            "titles": page.title,
            "cllimit": 500,
        }

        used_params = kwargs
        used_params.update(params)

        raw = self._query(page, used_params)
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return {}
            return self._build_categories(v, page)
        return {}

    def categorymembers(self, page: "WikipediaPage", **kwargs) -> PagesDict:
        """
        Returns pages in given category with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategorymembers
        - https://www.mediawiki.org/wiki/API:Categorymembers

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: pages in given category
        """
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": page.title,
            "cmlimit": 500,
        }

        used_params = kwargs
        used_params.update(params)

        raw = self._query(page, used_params)

        self._common_attributes(raw["query"], page)
        v = raw["query"]
        while "continue" in raw:
            params["cmcontinue"] = raw["continue"]["cmcontinue"]
            raw = self._query(page, params)
            v["categorymembers"] += raw["query"]["categorymembers"]

        return self._build_categorymembers(v, page)

    def _query(self, page: "WikipediaPage", params: Dict[str, Any]):
        """Queries Wikimedia API to fetch content."""
        base_url = "https://" + page.language + ".wikipedia.org/w/api.php"
        log.info(
            "Request URL: %s",
            base_url + "?" + "&".join([k + "=" + str(v) for k, v in params.items()]),
        )
        params["format"] = "json"
        params["redirects"] = 1
        r = self._session.get(base_url, params=params, **self._request_kwargs)
        return r.json()

    def _build_extracts(self, extract, page: "WikipediaPage") -> str:
        """Constructs summary of given page."""
        page._summary = ""
        page._section_mapping = defaultdict(list)

        self._common_attributes(extract, page)

        section_stack = [page]
        section = None
        prev_pos = 0

        for match in re.finditer(RE_SECTION[self.extract_format], extract["extract"]):
            if len(page._section_mapping) == 0:
                page._summary = extract["extract"][0 : match.start()].strip()
            elif section is not None:
                section._text = (extract["extract"][prev_pos : match.start()]).strip()

            section = self._create_section(match)
            sec_level = section.level + 1

            if sec_level > len(section_stack):
                section_stack.append(section)
            elif sec_level == len(section_stack):
                section_stack.pop()
                section_stack.append(section)
            else:
                for _ in range(len(section_stack) - sec_level + 1):
                    section_stack.pop()
                section_stack.append(section)

            section_stack[len(section_stack) - 2]._section.append(section)
            # section_stack[sec_level - 1]._section.append(section)

            prev_pos = match.end()
            page._section_mapping[section.title].append(section)

        # pages without sections have only summary
        if page._summary == "":
            page._summary = extract["extract"].strip()

        if prev_pos > 0 and section is not None:
            section._text = extract["extract"][prev_pos:]

        return page._summary

    def _create_section(self, match):
        """Creates section."""
        sec_title = ""
        sec_level = 2
        if self.extract_format == ExtractFormat.WIKI:
            sec_title = match.group(2).strip()
            sec_level = len(match.group(1))
        elif self.extract_format == ExtractFormat.HTML:
            sec_title = match.group(5).strip()
            sec_level = int(match.group(1).strip())

        section = WikipediaPageSection(self, sec_title, sec_level - 1)
        return section

    def _build_info(self, extract, page: "WikipediaPage") -> "WikipediaPage":
        """Builds page from API call info."""
        self._common_attributes(extract, page)
        for k, v in extract.items():
            page._attributes[k] = v

        return page

    def _build_langlinks(self, extract, page) -> PagesDict:
        """Builds page from API call langlinks."""
        page._langlinks = {}

        self._common_attributes(extract, page)

        for langlink in extract.get("langlinks", []):
            p = WikipediaPage(
                wiki=self,
                title=langlink["*"],
                ns=Namespace.MAIN,
                language=langlink["lang"],
                url=langlink["url"],
            )
            page._langlinks[p.language] = p

        return page._langlinks

    def _build_links(self, extract, page) -> PagesDict:
        """Builds page from API call links."""
        page._links = {}

        self._common_attributes(extract, page)

        for link in extract.get("links", []):
            page._links[link["title"]] = WikipediaPage(
                wiki=self,
                title=link["title"],
                ns=int(link["ns"]),
                language=page.language,
            )

        return page._links

    def _build_backlinks(self, extract, page) -> PagesDict:
        """Builds page from API call backlinks."""
        page._backlinks = {}

        self._common_attributes(extract, page)

        for backlink in extract.get("backlinks", []):
            page._backlinks[backlink["title"]] = WikipediaPage(
                wiki=self,
                title=backlink["title"],
                ns=int(backlink["ns"]),
                language=page.language,
            )

        return page._backlinks

    def _build_categories(self, extract, page) -> PagesDict:
        """Builds page from API call categories."""
        page._categories = {}

        self._common_attributes(extract, page)

        for category in extract.get("categories", []):
            page._categories[category["title"]] = WikipediaPage(
                wiki=self,
                title=category["title"],
                ns=int(category["ns"]),
                language=page.language,
            )

        return page._categories

    def _build_categorymembers(self, extract, page) -> PagesDict:
        """Builds page from API call categorymembers."""
        page._categorymembers = {}

        self._common_attributes(extract, page)

        for member in extract.get("categorymembers", []):
            p = WikipediaPage(
                wiki=self,
                title=member["title"],
                ns=int(member["ns"]),
                language=page.language,
            )
            p.pageid = member["pageid"]  # type: ignore

            page._categorymembers[member["title"]] = p

        return page._categorymembers

    @staticmethod
    def _common_attributes(extract, page: "WikipediaPage"):
        """Fills in common attributes for page."""
        common_attributes = ["title", "pageid", "ns", "redirects"]

        for attr in common_attributes:
            if attr in extract:
                page._attributes[attr] = extract[attr]


class WikipediaPageSection:
    """WikipediaPageSection represents section in the page."""

    def __init__(
        self, wiki: Wikipedia, title: str, level: int = 0, text: str = ""
    ) -> None:
        """Constructs WikipediaPageSection."""
        self.wiki = wiki
        self._title = title
        self._level = level
        self._text = text
        self._section = []  # type: List['WikipediaPageSection']

    @property
    def title(self) -> str:
        """
        Returns title of the current section.

        :return: title of the current section
        """
        return self._title

    @property
    def level(self) -> int:
        """
        Returns indentation level of the current section.

        :return: indentation level of the current section
        """
        return self._level

    @property
    def text(self) -> str:
        """
        Returns text of the current section.

        :return: text of the current section
        """
        return self._text

    @property
    def sections(self) -> List["WikipediaPageSection"]:
        """
        Returns subsections of the current section.

        :return: subsections of the current section
        """
        return self._section

    def section_by_title(self, title: str) -> Optional["WikipediaPageSection"]:
        """
        Returns subsections of the current section with given title.

        :param title: title of the subsection
        :return: subsection if it exists
        """
        sections = [s for s in self._section if s.title == title]
        if sections:
            return sections[-1]
        return None

    def full_text(self, level: int = 1) -> str:
        """
        Returns text of the current section as well as all its subsections.

        :param level: indentation level
        :return: text of the current section as well as all its subsections
        """
        res = ""
        if self.wiki.extract_format == ExtractFormat.WIKI:
            res += self.title
        elif self.wiki.extract_format == ExtractFormat.HTML:
            res += f"<h{level}>{self.title}</h{level}>"
        else:
            raise NotImplementedError("Unknown ExtractFormat type")

        res += "\n"
        res += self._text
        if len(self._text) > 0:
            res += "\n\n"
        for sec in self.sections:
            res += sec.full_text(level + 1)
        return res

    def __repr__(self):
        return "Section: {} ({}):\n{}\nSubsections ({}):\n{}".format(
            self._title,
            self._level,
            self._text,
            len(self._section),
            "\n".join(map(repr, self._section)),
        )


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
    }

    def __init__(
        self,
        wiki: Wikipedia,
        title: str,
        ns: WikiNamespace = Namespace.MAIN,
        language: str = "en",
        url: Optional[str] = None,
    ) -> None:
        self.wiki = wiki
        self._summary = ""  # type: str
        self._section = []  # type: List[WikipediaPageSection]
        self._section_mapping = {}  # type: Dict[str, List[WikipediaPageSection]]
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

        self._attributes = {
            "title": title,
            "ns": namespace2int(ns),
            "language": language,
        }  # type: Dict[str, Any]

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
    def sections(self) -> List[WikipediaPageSection]:
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
    ) -> Optional[WikipediaPageSection]:
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
    ) -> List[WikipediaPageSection]:
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
        if any(self._called.values()):
            return f"{self.title} (id: {self.pageid}, ns: {self.ns})"
        return f"{self.title} (id: ??, ns: {self.ns})"
