from collections import defaultdict
import re
from typing import Any, TYPE_CHECKING
from urllib import parse

from .extract_format import ExtractFormat
from .namespace import Namespace
from .namespace import WikiNamespace
from .wikipedia_page import PagesDict
from .wikipedia_page import WikipediaPage
from .wikipedia_page_section import WikipediaPageSection

if TYPE_CHECKING:
    from .async_wikipedia_page import AsyncWikipediaPage

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


class BaseWikipediaResource:
    """Pure data-transformation helpers shared between sync and async resources."""

    def _construct_params(self, page: WikipediaPage, params: dict[str, Any]) -> dict[str, Any]:
        used_params: dict[str, Any] = {}
        if page.variant:
            used_params["variant"] = page.variant
        used_params["format"] = "json"
        used_params["redirects"] = 1
        used_params.update(params)
        if self._extra_api_params:  # type: ignore[attr-defined]
            used_params.update(self._extra_api_params)  # type: ignore[attr-defined]
        return used_params

    def _make_page(
        self,
        title: str,
        ns: WikiNamespace,
        language: str,
        variant: str | None = None,
        url: str | None = None,
    ) -> WikipediaPage:
        return WikipediaPage(
            wiki=self,  # type: ignore[arg-type]
            title=title,
            ns=ns,
            language=language,
            variant=variant,
            url=url,
        )

    @staticmethod
    def _common_attributes(extract: Any, page: WikipediaPage) -> None:
        """Fills in common attributes for page."""
        common_attributes = ["title", "pageid", "ns", "redirects"]
        for attr in common_attributes:
            if attr in extract:
                page._attributes[attr] = extract[attr]

    def _create_section(self, match: Any) -> WikipediaPageSection:
        """Creates section."""
        sec_title = ""
        sec_level = 2
        if self.extract_format == ExtractFormat.WIKI:  # type: ignore[attr-defined]
            sec_title = match.group(2).strip()
            sec_level = len(match.group(1))
        elif self.extract_format == ExtractFormat.HTML:  # type: ignore[attr-defined]
            sec_title = match.group(5).strip()
            sec_level = int(match.group(1).strip())

        section = WikipediaPageSection(self, sec_title, sec_level - 1)  # type: ignore[arg-type]
        return section

    def _build_extracts(self, extract: Any, page: WikipediaPage) -> str:
        """Constructs summary of given page."""
        page._summary = ""
        page._section_mapping = defaultdict(list)

        self._common_attributes(extract, page)

        section_stack: list[Any] = [page]
        section = None
        prev_pos = 0

        for match in re.finditer(
            RE_SECTION[self.extract_format], extract["extract"]  # type: ignore[attr-defined]
        ):
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

    def _build_info(self, extract: Any, page: WikipediaPage) -> WikipediaPage:
        """Builds page from API call info."""
        self._common_attributes(extract, page)
        for k, v in extract.items():
            page._attributes[k] = v
        return page

    def _build_langlinks(self, extract: Any, page: WikipediaPage) -> PagesDict:
        """Builds page from API call langlinks."""
        page._langlinks = {}
        self._common_attributes(extract, page)
        for langlink in extract.get("langlinks", []):
            p = self._make_page(
                title=langlink["*"],
                ns=Namespace.MAIN,
                language=langlink["lang"],
                url=langlink["url"],
            )
            page._langlinks[p.language] = p
        return page._langlinks

    def _build_links(self, extract: Any, page: WikipediaPage) -> PagesDict:
        """Builds page from API call links."""
        page._links = {}
        self._common_attributes(extract, page)
        for link in extract.get("links", []):
            page._links[link["title"]] = self._make_page(
                title=link["title"],
                ns=int(link["ns"]),
                language=page.language,
                variant=page.variant,
            )
        return page._links

    def _build_backlinks(self, extract: Any, page: WikipediaPage) -> PagesDict:
        """Builds page from API call backlinks."""
        page._backlinks = {}
        self._common_attributes(extract, page)
        for backlink in extract.get("backlinks", []):
            page._backlinks[backlink["title"]] = self._make_page(
                title=backlink["title"],
                ns=int(backlink["ns"]),
                language=page.language,
                variant=page.variant,
            )
        return page._backlinks

    def _build_categories(self, extract: Any, page: WikipediaPage) -> PagesDict:
        """Builds page from API call categories."""
        page._categories = {}
        self._common_attributes(extract, page)
        for category in extract.get("categories", []):
            page._categories[category["title"]] = self._make_page(
                title=category["title"],
                ns=int(category["ns"]),
                language=page.language,
                variant=page.variant,
            )
        return page._categories

    def _build_categorymembers(self, extract: Any, page: WikipediaPage) -> PagesDict:
        """Builds page from API call categorymembers."""
        page._categorymembers = {}
        self._common_attributes(extract, page)
        for member in extract.get("categorymembers", []):
            p = self._make_page(
                title=member["title"],
                ns=int(member["ns"]),
                language=page.language,
                variant=page.variant,
            )
            p.pageid = member["pageid"]  # type: ignore[attr-defined]
            page._categorymembers[member["title"]] = p
        return page._categorymembers


class WikipediaResource(BaseWikipediaResource):
    """Synchronous Wikipedia API methods."""

    def page(
        self,
        title: str,
        ns: WikiNamespace = Namespace.MAIN,
        unquote: bool = False,
    ) -> WikipediaPage:
        """
        Constructs Wikipedia object for extracting information Wikipedia.

        :param user_agent: HTTP User-Agent used in requests
                https://meta.wikimedia.org/wiki/User-Agent_policy
        :param language: Language mutation of Wikipedia -
                http://meta.wikimedia.org/wiki/List_of_Wikipedias
        :param variant: Language variant.
                Only works if the base language supports variant conversion.
        :param extract_format: Format used for extractions
                :class:`ExtractFormat` object.
        :param headers:  Headers sent as part of HTTP request
        :param extra_api_params:  Extra parameters that are used to construct
                query string when calling Wikipedia API
        :param max_retries: Maximum number of retries for transient errors
                (HTTP 429, 5xx, timeouts, connection errors). Set to 0 to
                disable retries.
        :param retry_wait: Base wait time in seconds between retries.
                Uses exponential backoff: retry_wait * 2^attempt.
                For HTTP 429, the Retry-After header is used if present.
        :param request_kwargs: Optional parameters used in -
                http://docs.python-requests.org/en/master/api/#requests.request

        Examples:

        * Proxy: ``Wikipedia('foo (merlin@example.com)', proxies={'http': 'http://proxy:1234'})``
        """
        if unquote:
            title = parse.unquote(title)
        return WikipediaPage(
            self,  # type: ignore[arg-type]
            title=title,
            ns=ns,
            language=self.language,  # type: ignore[attr-defined]
            variant=self.variant,  # type: ignore[attr-defined]
        )

    def article(
        self, title: str, ns: WikiNamespace = Namespace.MAIN, unquote: bool = False
    ) -> WikipediaPage:
        """
        Constructs Wikipedia page with title `title`.

        This function is an alias for :func:`page`

        :param title: page title as used in Wikipedia URL
        :param ns: :class:`WikiNamespace`
        :param unquote: if true it will unquote title
        :return: object representing :class:`WikipediaPage`
        """
        return self.page(title=title, ns=ns, unquote=unquote)

    def extracts(self, page: WikipediaPage, **kwargs: Any) -> str:
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
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON

        """
        params: dict[str, Any] = {
            "action": "query",
            "prop": "extracts",
            "titles": page.title,
        }

        if self.extract_format == ExtractFormat.HTML:  # type: ignore[attr-defined]
            pass
        elif self.extract_format == ExtractFormat.WIKI:  # type: ignore[attr-defined]
            params["explaintext"] = 1
            params["exsectionformat"] = "wiki"

        used_params = params.copy()
        used_params.update(kwargs)

        raw = self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, used_params)
        )
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return ""
            return self._build_extracts(v, page)
        return ""

    def info(self, page: WikipediaPage) -> WikipediaPage:
        """
        https://www.mediawiki.org/w/api.php?action=help&modules=query%2Binfo
        https://www.mediawiki.org/wiki/API:Info

        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        params: dict[str, Any] = {
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
                    "varianttitles",
                ]
            ),
        }
        raw = self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, params)
        )
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return page
            return self._build_info(v, page)
        return page

    def langlinks(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Returns langlinks of the page with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blanglinks
        - https://www.mediawiki.org/wiki/API:Langlinks

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: links to pages in other languages
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON

        """
        params: dict[str, Any] = {
            "action": "query",
            "prop": "langlinks",
            "titles": page.title,
            "lllimit": 500,
            "llprop": "url",
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, used_params)
        )
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return {}
            return self._build_langlinks(v, page)
        return {}

    def links(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Returns links to other pages with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blinks
        - https://www.mediawiki.org/wiki/API:Links

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: links to linked pages
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON

        """
        params: dict[str, Any] = {
            "action": "query",
            "prop": "links",
            "titles": page.title,
            "pllimit": 500,
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, used_params)
        )
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return {}

            while "continue" in raw:
                params["plcontinue"] = raw["continue"]["plcontinue"]
                raw = self._get(  # type: ignore[attr-defined]
                    page.language, self._construct_params(page, params)
                )
                v["links"] += raw["query"]["pages"][k]["links"]

            return self._build_links(v, page)
        return {}

    def backlinks(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Returns backlinks from other pages with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bbacklinks
        - https://www.mediawiki.org/wiki/API:Backlinks

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: backlinks from other pages
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON

        """
        params: dict[str, Any] = {
            "action": "query",
            "list": "backlinks",
            "bltitle": page.title,
            "bllimit": 500,
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, used_params)
        )
        self._common_attributes(raw["query"], page)
        v = raw["query"]
        while "continue" in raw:
            params["blcontinue"] = raw["continue"]["blcontinue"]
            raw = self._get(  # type: ignore[attr-defined]
                page.language, self._construct_params(page, params)
            )
            v["backlinks"] += raw["query"]["backlinks"]
        return self._build_backlinks(v, page)

    def categories(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Returns categories for page with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategories
        - https://www.mediawiki.org/wiki/API:Categories

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: categories for page
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        params: dict[str, Any] = {
            "action": "query",
            "prop": "categories",
            "titles": page.title,
            "cllimit": 500,
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, used_params)
        )
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return {}
            return self._build_categories(v, page)
        return {}

    def categorymembers(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Returns pages in given category with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategorymembers
        - https://www.mediawiki.org/wiki/API:Categorymembers

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: pages in given category
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        params: dict[str, Any] = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": page.title,
            "cmlimit": 500,
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, used_params)
        )
        self._common_attributes(raw["query"], page)
        v = raw["query"]
        while "continue" in raw:
            params["cmcontinue"] = raw["continue"]["cmcontinue"]
            raw = self._get(  # type: ignore[attr-defined]
                page.language, self._construct_params(page, params)
            )
            v["categorymembers"] += raw["query"]["categorymembers"]
        return self._build_categorymembers(v, page)


class AsyncWikipediaResource(BaseWikipediaResource):
    """Asynchronous Wikipedia API methods."""

    def _make_page(  # type: ignore[override]
        self,
        title: str,
        ns: WikiNamespace,
        language: str,
        variant: str | None = None,
        url: str | None = None,
    ) -> "AsyncWikipediaPage":
        from .async_wikipedia_page import AsyncWikipediaPage

        return AsyncWikipediaPage(
            wiki=self,  # type: ignore[arg-type]
            title=title,
            ns=ns,
            language=language,
            variant=variant,
            url=url,
        )

    def page(
        self,
        title: str,
        ns: WikiNamespace = Namespace.MAIN,
        unquote: bool = False,
    ) -> "AsyncWikipediaPage":
        from .async_wikipedia_page import AsyncWikipediaPage

        if unquote:
            title = parse.unquote(title)
        return AsyncWikipediaPage(
            self,  # type: ignore[arg-type]
            title=title,
            ns=ns,
            language=self.language,  # type: ignore[attr-defined]
            variant=self.variant,  # type: ignore[attr-defined]
        )

    def article(
        self, title: str, ns: WikiNamespace = Namespace.MAIN, unquote: bool = False
    ) -> "AsyncWikipediaPage":
        """
        Constructs Wikipedia page with title `title`.

        This function is an alias for :func:`page`

        :param title: page title as used in Wikipedia URL
        :param ns: :class:`WikiNamespace`
        :param unquote: if true it will unquote title
        :return: object representing :class:`AsyncWikipediaPage`
        """
        return self.page(title=title, ns=ns, unquote=unquote)

    async def extracts(self, page: WikipediaPage, **kwargs: Any) -> str:
        """
        Returns summary of the page with respect to parameters.

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: summary of the page
        """
        params: dict[str, Any] = {
            "action": "query",
            "prop": "extracts",
            "titles": page.title,
        }

        if self.extract_format == ExtractFormat.HTML:  # type: ignore[attr-defined]
            pass
        elif self.extract_format == ExtractFormat.WIKI:  # type: ignore[attr-defined]
            params["explaintext"] = 1
            params["exsectionformat"] = "wiki"

        used_params = params.copy()
        used_params.update(kwargs)

        raw = await self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, used_params)
        )
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return ""
            return self._build_extracts(v, page)
        return ""

    async def info(self, page: WikipediaPage) -> WikipediaPage:
        """
        https://www.mediawiki.org/w/api.php?action=help&modules=query%2Binfo

        :param page: :class:`WikipediaPage`
        :return: populated :class:`WikipediaPage`
        """
        params: dict[str, Any] = {
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
                    "varianttitles",
                ]
            ),
        }
        raw = await self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, params)
        )
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return page
            return self._build_info(v, page)
        return page

    async def langlinks(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Returns langlinks of the page with respect to parameters.

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: links to pages in other languages
        """
        params: dict[str, Any] = {
            "action": "query",
            "prop": "langlinks",
            "titles": page.title,
            "lllimit": 500,
            "llprop": "url",
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = await self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, used_params)
        )
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return {}
            return self._build_langlinks(v, page)
        return {}

    async def links(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Returns links to other pages with respect to parameters.

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: links to linked pages
        """
        params: dict[str, Any] = {
            "action": "query",
            "prop": "links",
            "titles": page.title,
            "pllimit": 500,
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = await self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, used_params)
        )
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return {}

            while "continue" in raw:
                params["plcontinue"] = raw["continue"]["plcontinue"]
                raw = await self._get(  # type: ignore[attr-defined]
                    page.language, self._construct_params(page, params)
                )
                v["links"] += raw["query"]["pages"][k]["links"]

            return self._build_links(v, page)
        return {}

    async def backlinks(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Returns backlinks from other pages with respect to parameters.

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: backlinks from other pages
        """
        params: dict[str, Any] = {
            "action": "query",
            "list": "backlinks",
            "bltitle": page.title,
            "bllimit": 500,
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = await self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, used_params)
        )
        self._common_attributes(raw["query"], page)
        v = raw["query"]
        while "continue" in raw:
            params["blcontinue"] = raw["continue"]["blcontinue"]
            raw = await self._get(  # type: ignore[attr-defined]
                page.language, self._construct_params(page, params)
            )
            v["backlinks"] += raw["query"]["backlinks"]
        return self._build_backlinks(v, page)

    async def categories(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Returns categories for page with respect to parameters.

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: categories for page
        """
        params: dict[str, Any] = {
            "action": "query",
            "prop": "categories",
            "titles": page.title,
            "cllimit": 500,
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = await self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, used_params)
        )
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return {}
            return self._build_categories(v, page)
        return {}

    async def categorymembers(self, page: WikipediaPage, **kwargs: Any) -> PagesDict:
        """
        Returns pages in given category with respect to parameters.

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: pages in given category
        """
        params: dict[str, Any] = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": page.title,
            "cmlimit": 500,
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = await self._get(  # type: ignore[attr-defined]
            page.language, self._construct_params(page, used_params)
        )
        self._common_attributes(raw["query"], page)
        v = raw["query"]
        while "continue" in raw:
            params["cmcontinue"] = raw["continue"]["cmcontinue"]
            raw = await self._get(  # type: ignore[attr-defined]
                page.language, self._construct_params(page, params)
            )
            v["categorymembers"] += raw["query"]["categorymembers"]
        return self._build_categorymembers(v, page)
