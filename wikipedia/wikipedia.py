import logging
import re
import requests
log = logging.getLogger(__name__)

# https://www.mediawiki.org/wiki/API:Main_page


class ExtractFormat(object):  # (Enum):
    # Wiki: https://goo.gl/PScNVV
    # Allows recognizing subsections
    WIKI = 1

    # HTML: https://goo.gl/1Jwwpr
    # Text contains HTML tags
    HTML = 2

    # Plain: https://goo.gl/MAv2qz
    # Doesn't allow to recognize subsections
    # PLAIN = 3


RE_SECTION = {
    ExtractFormat.WIKI: re.compile(r'\n\n *(===*) (.*?) (===*) *\n'),
    ExtractFormat.HTML: re.compile(r'\n? *<h(\d)[^>]*?>(<span[^>]*><\/span>)? *(<span[^>]*>)? *(<span[^>]*><\/span>)? *(.*?) *(<\/span>)?<\/h\d>\n?'),
    # ExtractFormat.PLAIN.value: re.compile(r'\n\n *(===*) (.*?) (===*) *\n'),
}


class Wikipedia(object):
    def __init__(
            self,
            language='en',
            extract_format=ExtractFormat.WIKI,
            user_agent='Wikipedia-API (https://github.com/martin-majlis/Wikipedia-API)',
    ):
        '''
        Language of the API being requested.
        Select language from `list of all Wikipedias <http://meta.wikimedia.org/wiki/List_of_Wikipedias>`_.
        '''
        self.language = language.strip().lower()
        self.user_agent = user_agent
        self.extract_format = extract_format

    def page(
            self,
            title: str,
            ns: int = 0
    ):
        return WikipediaPage(self, title, ns)

    def _structured(
        self,
        page: 'WikipediaPage'
    ) -> 'WikipediaPage':
        """
        https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bextracts
        https://www.mediawiki.org/wiki/Extension:TextExtracts#API
        """
        params = {
            'action': 'query',
            'prop': 'extracts',
            'titles': page.title
        }

        if self.extract_format == ExtractFormat.HTML:
            # we do nothing, when format is HTML
            pass
        elif self.extract_format == ExtractFormat.WIKI:
            params['explaintext'] = 1
            params['exsectionformat'] = 'wiki'
        # elif self.extract_format == ExtractFormat.PLAIN:
        #    params['explaintext'] = 1
        #    params['exsectionformat'] = 'plain'

        raw = self._query(
            params
        )
        pages = raw['query']['pages']
        for k, v in pages.items():
            if k == '-1':
                page._attributes['pageid'] = -1
                return page
            else:
                return self._build_structured(v, page)

    def _info(
        self,
        page: 'WikipediaPage'
    ) -> 'WikipediaPage':
        """
        https://www.mediawiki.org/w/api.php?action=help&modules=query%2Binfo
        https://www.mediawiki.org/wiki/API:Info
        """
        params = {
            'action': 'query',
            'prop': 'info',
            'titles': page.title,
            'inprop': '|'.join([
                'protection',
                'talkid',
                'watched',
                'watchers',
                'visitingwatchers',
                'notificationtimestamp',
                'subjectid',
                'url',
                'readable',
                'preload',
                'displaytitle'
            ])
        }
        raw = self._query(
            params
        )
        pages = raw['query']['pages']
        for k, v in pages.items():
            if k == '-1':
                page._attributes['pageid'] = -1
                return page
            else:
                return self._build_info(v, page)

    def _langlinks(
        self,
        page: 'WikipediaPage'
    ) -> 'WikipediaPage':
        """
        https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blanglinks
        https://www.mediawiki.org/wiki/API:Langlinks
        """

        params = {
            'action': 'query',
            'prop': 'langlinks',
            'titles': page.title,
            'lllimit': 500,
            'llprop': 'url',
        }
        raw = self._query(
            params
        )
        pages = raw['query']['pages']
        for k, v in pages.items():
            if k == '-1':
                page._attributes['pageid'] = -1
                return page
            else:
                return self._build_langlinks(v, page)

    def _links(
        self,
        page: 'WikipediaPage'
    ) -> 'WikipediaPage':
        """
        https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blinks
        https://www.mediawiki.org/wiki/API:Links
        """

        params = {
            'action': 'query',
            'prop': 'links',
            'titles': page.title,
            'pllimit': 500,
        }
        raw = self._query(
            params
        )
        pages = raw['query']['pages']
        for k, v in pages.items():
            if k == '-1':
                page._attributes['pageid'] = -1
                return page
            else:
                while 'continue' in raw:
                    params['plcontinue'] = raw['continue']['plcontinue']
                    raw = self._query(
                        params
                    )
                    v['links'] += raw['query']['pages'][k]['links']

                return self._build_links(v, page)

    def _query(
        self,
        params: {}
    ):
        base_url = 'http://' + self.language + '.wikipedia.org/w/api.php'
        headers = {
            'User-Agent': self.user_agent
        }
        logging.info(
            "Request URL: %s",
            base_url + "?" + "&".join(
                [k + "=" + str(v) for k, v in params.items()]
            )
        )
        params['format'] = 'json'
        r = requests.get(
            base_url,
            params=params,
            headers=headers
        )
        return r.json()

    def _build_structured(
        self,
        extract,
        page
    ):
        # print(extract)
        page._attributes['title'] = extract['title']
        page._attributes['pageid'] = extract['pageid']
        page._attributes['ns'] = extract['ns']

        section_stack = [page]
        section = None
        prev_pos = 0

        for match in re.finditer(
            RE_SECTION[self.extract_format],
            extract['extract']
        ):
            # print(match.start(), match.end())
            if page._summary == '':
                page._summary = extract['extract'][0:match.start()].strip()
            else:
                section._text = (
                    extract['extract'][prev_pos:match.start()]
                ).strip()

            sec_title = ''
            sec_level = 2
            if self.extract_format == ExtractFormat.WIKI:
                sec_title = match.group(2).strip()
                sec_level = len(match.group(1))
            elif self.extract_format == ExtractFormat.HTML:
                sec_title = match.group(5).strip()
                sec_level = int(match.group(1).strip())

            section = WikipediaPageSection(
                sec_title,
                sec_level - 1
            )

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

            # section_stack_pos = sec_level

            prev_pos = match.end()
            page._section_mapping[section._title] = section

        if prev_pos > 0:
            section._text = extract['extract'][prev_pos:]

        return page

    def _build_info(
        self,
        extract,
        page
    ):
        for k, v in extract.items():
            page._attributes[k] = v

        return page

    def _build_langlinks(
        self,
        extract,
        page
    ):
        for langlink in extract['langlinks']:
            page._langlinks[langlink['lang']] = WikipediaLangLink(
                lang=langlink['lang'],
                title=langlink['*'],
                url=langlink['url']
            )

        return page

    def _build_links(
        self,
        extract,
        page
    ):
        for link in extract['links']:
            page._links[link['title']] = self.page(
                title=link['title'],
                ns=link['ns']
            )

        return page

    def article(
            self,
            title: str,
            ns: int = 0
    ):
        return self.page(title, ns)


class WikipediaPageSection(object):
    def __init__(
            self,
            title: str,
            level=0,
            text=''
    ):
        self._title = title
        self._level = level
        self._text = text
        self._section = []

    @property
    def title(self) -> str:
        return self._title

    @property
    def level(self) -> int:
        return self._level

    @property
    def text(self) -> str:
        return self._text

    @property
    def sections(self) -> ['WikipediaPageSection']:
        return self._section

    def __repr__(self):
        return "Section: {} ({}):\n{}\nSubsections ({}):\n{}".format(
            self._title,
            self._level,
            self._text,
            len(self._section),
            "\n".join(map(repr, self._section))
        )


class WikipediaLangLink(object):
    def __init__(
            self,
            title: str,
            lang: str,
            url: str
    ):
        self._title = title
        self._lang = lang
        self._url = url

    @property
    def title(self) -> str:
        return self._title

    @property
    def lang(self) -> str:
        return self._lang

    @property
    def url(self) -> str:
        return self._url

    def __repr__(self):
        return "LangLink: {} ({}): {}".format(
            self._title,
            self._lang,
            self._url,
        )


class WikipediaPage(object):
    ATTRIBUTES_MAPPING = {
        "pageid": ["info", "structured", "langlinks"],
        "ns": ["info", "structured", "langlinks"],
        "title": ["info", "structured", "langlinks"],
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
        "displaytitle": ["info"]
    }

    def __init__(
            self,
            wiki: Wikipedia,
            title: str,
            ns: int = 0
    ):
        self.wiki = wiki
        self._summary = ''
        self._section = []
        self._section_mapping = {}
        self._langlinks = {}
        self._links = {}

        self._called = {
            'structured': False,
            'info': False,
            'langlinks': False,
            'links': False
        }
        self._attributes = {
            'title': title,
            'ns': ns
        }

    def __getattr__(self, name):
        if name not in self.ATTRIBUTES_MAPPING:
            return self.__getattribute__(name)

        if name in self._attributes:
            return self._attributes[name]

        for call in self.ATTRIBUTES_MAPPING[name]:
            if not self._called[call]:
                getattr(self, "_fetch_" + call)()
                return self._attributes[name]

    def exists(self) -> bool:
        return self.pageid != -1

    @property
    def summary(self) -> str:
        if not self._called['structured']:
            self._fetch_structured()
        return self._summary

    @property
    def sections(self) -> [WikipediaPageSection]:
        if not self._called['structured']:
            self._fetch_structured()
        return self._section

    def section_by_title(self, title) -> WikipediaPageSection:
        if not self._called['structured']:
            self._fetch_structured()
        return self._section_mapping[title]

    @property
    def langlinks(self):
        if not self._called['langlinks']:
            self._fetch_langlinks()
        return self._langlinks

    @property
    def links(self):
        if not self._called['links']:
            self._fetch_links()
        return self._links

    def _fetch_structured(self) -> 'WikipediaPage':
        self.wiki._structured(
            self
        )
        self._called['structured'] = True
        return self

    def _fetch_info(self) -> 'WikipediaPage':
        self.wiki._info(
            self
        )
        self._called['info'] = True
        return self

    def _fetch_langlinks(self) -> 'WikipediaPage':
        self.wiki._langlinks(
            self
        )
        self._called['langlinks'] = True
        return self

    def _fetch_links(self) -> 'WikipediaPage':
        self.wiki._links(
            self
        )
        self._called['links'] = True
        return self

    def __repr__(self):
        if any(self._called.values()):
            return "{} (id: {}, ns: {})".format(self.title, self.id, self.ns)
        else:
            return "{} (id: ??, ns: {})".format(self.title, self.ns)
