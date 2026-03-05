from collections import defaultdict
import logging
import re
import time
from typing import Any, cast, Optional
from urllib import parse

import requests

from ._version import __version_str__
from .exceptions import WikiConnectionError
from .exceptions import WikiHttpError
from .exceptions import WikiHttpTimeoutError
from .exceptions import WikiInvalidJsonError
from .exceptions import WikipediaException
from .exceptions import WikiRateLimitError
from .extract_format import ExtractFormat
from .namespace import Namespace
from .namespace import WikiNamespace
from .wikipedia_page import PagesDict
from .wikipedia_page import WikipediaPage
from .wikipedia_page_section import WikipediaPageSection

USER_AGENT = (
    "Wikipedia-API/" + __version_str__ + "; https://github.com/martin-majlis/Wikipedia-API/"
)

MIN_USER_AGENT_LEN = 5
MAX_LANG_LEN = 5

log = logging.getLogger(__name__)


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
        variant: str | None = None,
        extract_format: ExtractFormat = ExtractFormat.WIKI,
        headers: dict[str, Any] | None = None,
        extra_api_params: dict[str, Any] | None = None,
        max_retries: int = 3,
        retry_wait: float = 1.0,
        **request_kwargs,
    ) -> None:
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
        request_kwargs.setdefault("timeout", 10.0)

        default_headers = {} if headers is None else headers
        if user_agent is not None:
            default_headers.setdefault(
                "User-Agent",
                user_agent,
            )
        used_language, used_variant, used_user_agent = self._check_and_correct_params(
            language,
            variant,
            default_headers.get("User-Agent"),
        )

        default_headers["User-Agent"] = used_user_agent + " (" + USER_AGENT + ")"

        self.language = used_language
        self.variant = used_variant
        self.extract_format = extract_format

        log.info(
            "Wikipedia: language=%s, user_agent: %s, extract_format=%s",
            self.language,
            default_headers["User-Agent"],
            self.extract_format,
        )

        self._extra_api_params = extra_api_params
        self._max_retries = max_retries
        self._retry_wait = retry_wait

        self._session = requests.Session()
        self._session.headers.update(default_headers)
        self._request_kwargs = request_kwargs

    def __del__(self) -> None:
        """Closes session."""
        if hasattr(self, "_session") and self._session:
            self._session.close()

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

        return WikipediaPage(self, title=title, ns=ns, language=self.language, variant=self.variant)

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
        return self.page(
            title=title,
            ns=ns,
            unquote=unquote,
        )

    def extracts(self, page: WikipediaPage, **kwargs) -> str:
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
        params = {
            "action": "query",
            "prop": "extracts",
            "titles": page.title,
        }  # type: dict[str, Any]

        if self.extract_format == ExtractFormat.HTML:
            # we do nothing, when format is HTML
            pass
        elif self.extract_format == ExtractFormat.WIKI:
            params["explaintext"] = 1
            params["exsectionformat"] = "wiki"

        used_params = params.copy()
        used_params.update(kwargs)

        raw = self._query(page, used_params)
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
                    "varianttitles",
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

    def langlinks(self, page: WikipediaPage, **kwargs) -> PagesDict:
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
        params = {
            "action": "query",
            "prop": "langlinks",
            "titles": page.title,
            "lllimit": 500,
            "llprop": "url",
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = self._query(page, used_params)
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return {}
            return self._build_langlinks(v, page)
        return {}

    def links(self, page: WikipediaPage, **kwargs) -> PagesDict:
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
        params = {
            "action": "query",
            "prop": "links",
            "titles": page.title,
            "pllimit": 500,
        }

        used_params = params.copy()
        used_params.update(kwargs)

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

    def backlinks(self, page: WikipediaPage, **kwargs) -> PagesDict:
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
        params = {
            "action": "query",
            "list": "backlinks",
            "bltitle": page.title,
            "bllimit": 500,
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = self._query(page, used_params)

        self._common_attributes(raw["query"], page)
        v = raw["query"]
        while "continue" in raw:
            params["blcontinue"] = raw["continue"]["blcontinue"]
            raw = self._query(page, params)
            v["backlinks"] += raw["query"]["backlinks"]
        return self._build_backlinks(v, page)

    def categories(self, page: WikipediaPage, **kwargs) -> PagesDict:
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
        params = {
            "action": "query",
            "prop": "categories",
            "titles": page.title,
            "cllimit": 500,
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = self._query(page, used_params)
        self._common_attributes(raw["query"], page)
        pages = raw["query"]["pages"]
        for k, v in pages.items():
            if k == "-1":
                page._attributes["pageid"] = -1
                return {}
            return self._build_categories(v, page)
        return {}

    def categorymembers(self, page: WikipediaPage, **kwargs) -> PagesDict:
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
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": page.title,
            "cmlimit": 500,
        }

        used_params = params.copy()
        used_params.update(kwargs)

        raw = self._query(page, used_params)

        self._common_attributes(raw["query"], page)
        v = raw["query"]
        while "continue" in raw:
            params["cmcontinue"] = raw["continue"]["cmcontinue"]
            raw = self._query(page, params)
            v["categorymembers"] += raw["query"]["categorymembers"]

        return self._build_categorymembers(v, page)

    def _attempt_request(
        self, base_url: str, used_params: dict[str, Any]
    ) -> tuple[Any | None, WikiConnectionError | WikiHttpTimeoutError | None, bool]:
        """Perform a single HTTP GET and convert request-layer exceptions.

        :return: ``(response, exc, retryable)`` where *response* is the
            ``requests.Response`` on success, *exc* is a
            :class:`WikipediaException` when a request-layer error occurred,
            and *retryable* indicates whether the caller may retry.
        """
        try:
            return (
                self._session.get(base_url, params=used_params, **self._request_kwargs),
                None,
                False,
            )
        except requests.exceptions.Timeout:
            return None, WikiHttpTimeoutError(base_url), True
        except requests.exceptions.ConnectionError:
            return None, WikiConnectionError(base_url), True
        except requests.exceptions.RequestException:
            raise WikiConnectionError(base_url)

    def _handle_response(
        self, r: Any, base_url: str, attempt: int
    ) -> tuple[WikiHttpError | None, bool, float]:
        """Inspect an HTTP response and decide what to do next.

        :return: ``(exc, retryable, wait)`` where *exc* is set for retryable
            errors, *retryable* is ``True`` when the caller should retry, and
            *wait* is the number of seconds to sleep before the next attempt.
            Raises immediately for non-retryable errors.
        :raises WikiHttpError: for non-retryable 4xx responses
        :raises WikiInvalidJsonError: when the 200 response body is not JSON
        """
        if r.status_code == 429:
            retry_after = r.headers.get("Retry-After")
            wait: float = (
                int(retry_after)
                if retry_after and retry_after.isdigit()
                else self._retry_wait * (2**attempt)
            )
            exc = WikiRateLimitError(
                base_url,
                int(retry_after) if retry_after and retry_after.isdigit() else None,
            )
            log.warning(
                "Rate limited (attempt %d/%d), waiting %.1fs: %s",
                attempt + 1,
                1 + self._max_retries,
                wait,
                base_url,
            )
            return exc, True, wait

        if r.status_code >= 500:
            log.warning(
                "Server error %d (attempt %d/%d): %s",
                r.status_code,
                attempt + 1,
                1 + self._max_retries,
                base_url,
            )
            return (
                WikiHttpError(r.status_code, base_url),
                True,
                self._retry_wait * (2**attempt),
            )

        if r.status_code != 200:
            raise WikiHttpError(r.status_code, base_url)

        return None, False, 0.0

    def _query(self, page: WikipediaPage, params: dict[str, Any]):
        """Queries Wikimedia API to fetch content.

        Transient errors (HTTP 429, 5xx, timeouts, connection errors) are
        retried up to ``max_retries`` times with exponential backoff.

        :param page: :class:`WikipediaPage`
        :param params: parameters used in API call
        :return: parsed JSON response as dict
        :raises WikiHttpTimeoutError: if the request times out after all retries
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429 after all retries
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        base_url = "https://" + page.language + ".wikipedia.org/w/api.php"
        used_params = self._construct_params(page, params)

        log.info(
            "Request URL: %s",
            base_url + "?" + "&".join([k + "=" + str(v) for k, v in used_params.items()]),
        )

        last_exc: WikipediaException | None = None
        for attempt in range(1 + self._max_retries):
            r, exc, retryable_req = self._attempt_request(base_url, used_params)
            if exc is not None:
                last_exc = exc
                log.warning(
                    "%s (attempt %d/%d): %s",
                    exc.__class__.__name__,
                    attempt + 1,
                    1 + self._max_retries,
                    base_url,
                )
                if retryable_req and attempt < self._max_retries:
                    time.sleep(self._retry_wait * (2**attempt))
                continue

            exc, retryable_resp, wait = self._handle_response(  # type: ignore[assignment]
                r, base_url, attempt
            )
            if retryable_resp:
                last_exc = cast(Optional[WikipediaException], exc)  # type: ignore[assignment]
                if attempt < self._max_retries:
                    time.sleep(wait)
                continue

            assert r is not None
            try:
                return r.json()
            except ValueError:
                raise WikiInvalidJsonError(base_url)

        assert last_exc is not None
        raise last_exc

    def _construct_params(self, page: WikipediaPage, params: dict[str, Any]) -> dict[str, Any]:
        used_params = {}  # type: dict[str, Any]
        if page.variant:
            used_params["variant"] = page.variant
        used_params["format"] = "json"
        used_params["redirects"] = 1
        used_params.update(params)
        if self._extra_api_params:
            used_params.update(self._extra_api_params)
        return used_params

    def _build_extracts(self, extract, page: WikipediaPage) -> str:
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

    def _build_info(self, extract, page: WikipediaPage) -> WikipediaPage:
        """Builds page from API call info."""
        self._common_attributes(extract, page)
        for k, v in extract.items():
            page._attributes[k] = v

        return page

    def _build_langlinks(self, extract, page: WikipediaPage) -> PagesDict:
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

    def _build_links(self, extract, page: WikipediaPage) -> PagesDict:
        """Builds page from API call links."""
        page._links = {}

        self._common_attributes(extract, page)

        for link in extract.get("links", []):
            page._links[link["title"]] = WikipediaPage(
                wiki=self,
                title=link["title"],
                ns=int(link["ns"]),
                language=page.language,
                variant=page.variant,
            )

        return page._links

    def _build_backlinks(self, extract, page: WikipediaPage) -> PagesDict:
        """Builds page from API call backlinks."""
        page._backlinks = {}

        self._common_attributes(extract, page)

        for backlink in extract.get("backlinks", []):
            page._backlinks[backlink["title"]] = WikipediaPage(
                wiki=self,
                title=backlink["title"],
                ns=int(backlink["ns"]),
                language=page.language,
                variant=page.variant,
            )

        return page._backlinks

    def _build_categories(self, extract, page: WikipediaPage) -> PagesDict:
        """Builds page from API call categories."""
        page._categories = {}

        self._common_attributes(extract, page)

        for category in extract.get("categories", []):
            page._categories[category["title"]] = WikipediaPage(
                wiki=self,
                title=category["title"],
                ns=int(category["ns"]),
                language=page.language,
                variant=page.variant,
            )

        return page._categories

    def _build_categorymembers(self, extract, page: WikipediaPage) -> PagesDict:
        """Builds page from API call categorymembers."""
        page._categorymembers = {}

        self._common_attributes(extract, page)

        for member in extract.get("categorymembers", []):
            p = WikipediaPage(
                wiki=self,
                title=member["title"],
                ns=int(member["ns"]),
                language=page.language,
                variant=page.variant,
            )
            p.pageid = member["pageid"]  # type: ignore

            page._categorymembers[member["title"]] = p

        return page._categorymembers

    @staticmethod
    def _common_attributes(extract, page: WikipediaPage):
        """Fills in common attributes for page."""
        common_attributes = ["title", "pageid", "ns", "redirects"]

        for attr in common_attributes:
            if attr in extract:
                page._attributes[attr] = extract[attr]

    @staticmethod
    def _check_and_correct_params(
        language: str | None, variant: str | None, user_agent: str | None
    ) -> tuple[str, str | None, str]:
        """
        Checks the constructor parameters and throws AssertionError if they are incorrect.
        Otherwise, it normalises them to easy use later on.
        :param language: Language mutation of Wikipedia
        :param variant: Language variant
        :param user_agent: HTTP User-Agent used in requests
        :return: tuple of language, variant, user_agent
        """
        if not user_agent or len(user_agent) < MIN_USER_AGENT_LEN:
            raise AssertionError(
                "Please, be nice to Wikipedia and specify user agent - "
                + "https://meta.wikimedia.org/wiki/User-Agent_policy. Current user_agent: '"
                + str(user_agent)
                + "' is not sufficient. "
                + "Use Wikipedia(user_agent='your-user-agent', language='"
                + (str(user_agent) or "your-language")
                + "')"
            )

        if not language:
            raise AssertionError(
                "Specify language. Current language: '"
                + str(language)
                + "' is not sufficient. "
                + "Use Wikipedia(user_agent='"
                + str(user_agent)
                + "', language='your-language')"
            )

        used_language = language.strip().lower()
        if len(used_language) > MAX_LANG_LEN:
            log.warning(
                "Used language '%s' is longer than %d. It is suspicious",
                used_language,
                MAX_LANG_LEN,
            )

        return (
            used_language,
            variant.strip().lower() if variant else variant,
            user_agent,
        )
