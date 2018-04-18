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


class Namespace(object):
    """
    https://en.wikipedia.org/wiki/Wikipedia:Namespace
    https://en.wikipedia.org/wiki/Wikipedia:Namespace#Programming
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


RE_SECTION = {
    ExtractFormat.WIKI: re.compile(r'\n\n *(===*) (.*?) (===*) *\n'),
    ExtractFormat.HTML: re.compile(
        r'\n? *<h(\d)[^>]*?>(<span[^>]*><\/span>)? *' +
        '(<span[^>]*>)? *(<span[^>]*><\/span>)? *(.*?) *' +
        '(<\/span>)?(<span>Edit<\/span>)?<\/h\d>\n?'
        #                  ^^^^
        # Example page with 'Edit' erroneous links: https://bit.ly/2ui4FWs
    ),
    # ExtractFormat.PLAIN.value: re.compile(r'\n\n *(===*) (.*?) (===*) *\n'),
}


class Wikipedia(object):
    def __init__(
            self,
            language='en',
            extract_format=ExtractFormat.WIKI,
            user_agent=(
            'Wikipedia-API (https://github.com/martin-majlis/Wikipedia-API)'
            ),
            timeout=10.0
    ):
        '''
        Language of the API being requested.
        Select language from `list of all Wikipedias:
            <http://meta.wikimedia.org/wiki/List_of_Wikipedias>`.
        '''
        self.language = language.strip().lower()
        self.user_agent = user_agent
        self.extract_format = extract_format
        self.timeout = timeout

    def page(
            self,
            title: str,
            ns: int = 0
    ):
        return WikipediaPage(
            self,
            title=title,
            ns=ns,
            language=self.language
        )

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
            page,
            params
        )
        self._common_attributes(raw['query'], page)
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
            page,
            params
        )
        self._common_attributes(raw['query'], page)
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
            page,
            params
        )
        self._common_attributes(raw['query'], page)
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
            page,
            params
        )
        self._common_attributes(raw['query'], page)
        pages = raw['query']['pages']
        for k, v in pages.items():
            if k == '-1':
                page._attributes['pageid'] = -1
                return page
            else:
                while 'continue' in raw:
                    params['plcontinue'] = raw['continue']['plcontinue']
                    raw = self._query(
                        page,
                        params
                    )
                    v['links'] += raw['query']['pages'][k]['links']

                return self._build_links(v, page)

    def _backlinks(
        self,
        page: 'WikipediaPage'
    ) -> 'WikipediaPage':
        """
        https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bbacklinks
        https://www.mediawiki.org/wiki/API:Backlinks
        """

        params = {
            'action': 'query',
            'list': 'backlinks',
            'bltitle': page.title,
            'bllimit': 500,
        }
        raw = self._query(
            page,
            params
        )
        self._common_attributes(raw['query'], page)
        v = raw['query']
        while 'continue' in raw:
            params['blcontinue'] = raw['continue']['blcontinue']
            raw = self._query(
                page,
                params
            )
            v['backlinks'] += raw['query']['backlinks']
        return self._build_backlinks(v, page)
    
    
    def _categories(
        self,
        page: 'WikipediaPage'
    ) -> 'WikipediaPage':
        """
        https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategories
        https://www.mediawiki.org/wiki/API:Categories
        """

        params = {
            'action': 'query',
            'prop': 'categories',
            'titles': page.title,
            'cllimit': 500,
        }
        raw = self._query(
            page,
            params
        )
        self._common_attributes(raw['query'], page)
        pages = raw['query']['pages']
        for k, v in pages.items():
            if k == '-1':
                page._attributes['pageid'] = -1
                return page
            else:
                return self._build_categories(v, page)

    def _categorymembers(
        self,
        page: 'WikipediaPage'
    ) -> 'WikipediaPage':
        """
        https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategorymembers
        https://www.mediawiki.org/wiki/API:Categorymembers
        """

        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': page.title,
            'cmlimit': 500,
        }
        raw = self._query(
            page,
            params
        )
        self._common_attributes(raw['query'], page)
        v = raw['query']
        while 'continue' in raw:
            params['cmcontinue'] = raw['continue']['cmcontinue']
            raw = self._query(
                page,
                params
            )
            v['categorymembers'] += raw['query']['categorymembers']

        return self._build_categorymembers(v, page)

    def _query(
        self,
        page: 'WikipediaPage',
        params: {}
    ):
        base_url = 'http://' + page.language + '.wikipedia.org/w/api.php'
        headers = {
            'User-Agent': self.user_agent,
            'Accept-Encoding': 'gzip',
        }
        logging.info(
            "Request URL: %s",
            base_url + "?" + "&".join(
                [k + "=" + str(v) for k, v in params.items()]
            )
        )
        params['format'] = 'json'
        params['redirects'] = 1
        r = requests.get(
            base_url,
            params=params,
            headers=headers,
            timeout=self.timeout,
        )
        return r.json()

    def _build_structured(
        self,
        extract,
        page
    ):
        self._common_attributes(extract, page)
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

            # section_stack_pos = sec_level

            prev_pos = match.end()
            page._section_mapping[section._title] = section

        if prev_pos > 0:
            section._text = extract['extract'][prev_pos:]

        return page

    def _create_section(self, match):
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
        return section

    def _build_info(
        self,
        extract,
        page
    ):
        self._common_attributes(extract, page)
        for k, v in extract.items():
            page._attributes[k] = v

        return page

    def _build_langlinks(
        self,
        extract,
        page
    ):
        self._common_attributes(extract, page)
        for langlink in extract['langlinks']:
            p = WikipediaPage(
                wiki=self,
                title=langlink['*'],
                ns=0,
                language=langlink['lang'],
                url=langlink['url']
            )
            page._langlinks[p.language] = p

        return page

    def _build_links(
        self,
        extract,
        page
    ):
        self._common_attributes(extract, page)
        for link in extract['links']:
            page._links[link['title']] = WikipediaPage(
                wiki=self,
                title=link['title'],
                ns=link['ns'],
                language=page.language
            )

        return page

    def _build_backlinks(
        self,
        extract,
        page
    ):
        self._common_attributes(extract, page)
        for backlink in extract['backlinks']:
            page._backlinks[backlink['title']] = WikipediaPage(
                wiki=self,
                title=backlink['title'],
                ns=backlink['ns'],
                language=page.language
            )

        return page


    def _build_categories(
        self,
        extract,
        page
    ):
        self._common_attributes(extract, page)
        for category in extract['categories']:
            page._categories[category['title']] = WikipediaPage(
                wiki=self,
                title=category['title'],
                ns=category['ns'],
                language=page.language
            )

        return page

    def _build_categorymembers(
        self,
        extract,
        page
    ):
        self._common_attributes(extract, page)
        for member in extract['categorymembers']:
            p = WikipediaPage(
                wiki=self,
                title=member['title'],
                ns=member['ns'],
                language=page.language
            )
            p.pageid = member['pageid']

            page._categorymembers[member['title']] = p

        return page

    def _common_attributes(
        self,
        extract,
        page
    ):
        common_attributes = [
            'title',
            'pageid',
            'ns',
            'redirects'
        ]

        for attr in common_attributes:
            if attr in extract:
                page._attributes[attr] = extract[attr]

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


class WikipediaPage(object):
    ATTRIBUTES_MAPPING = {
        "language": [],
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
            ns: int = 0,
            language: str = 'en',
            url: str = None
    ):
        self.wiki = wiki
        self._summary = ''
        self._section = []
        self._section_mapping = {}
        self._langlinks = {}
        self._links = {}
        self._backlinks = {}
        self._categories = {}
        self._categorymembers = {}

        self._called = {
            'structured': False,
            'info': False,
            'langlinks': False,
            'links': False,
            'backlinks': False,
            'categories': False,
            'categorymembers': False,
        }

        self._attributes = {
            'title': title,
            'ns': ns,
            'language': language
        }

        if url is not None:
            self._attributes['fullurl'] = url

    def __getattr__(self, name):
        if name not in self.ATTRIBUTES_MAPPING:
            return self.__getattribute__(name)

        if name in self._attributes:
            return self._attributes[name]

        for call in self.ATTRIBUTES_MAPPING[name]:
            if not self._called[call]:
                getattr(self, "_fetch")(call)
                return self._attributes[name]

    def exists(self) -> bool:
        return self.pageid != -1

    @property
    def summary(self) -> str:
        if not self._called['structured']:
            self._fetch('structured')
        return self._summary

    @property
    def sections(self) -> [WikipediaPageSection]:
        if not self._called['structured']:
            self._fetch('structured')
        return self._section

    def section_by_title(self, title) -> WikipediaPageSection:
        if not self._called['structured']:
            self._fetch('structured')
        return self._section_mapping[title]

    @property
    def text(self):
        txt = self.summary
        if len(txt) > 0:
            txt += "\n\n"

        def combine(sections, level):
            res = ""
            for sec in sections:
                if self.wiki.extract_format == ExtractFormat.WIKI:
                    res += sec.title
                elif self.wiki.extract_format == ExtractFormat.HTML:
                    res += "<h{}>{}</h{}>".format(level, sec.title, level)
                else:
                    raise NotImplementedError("Unknown ExtractFormat type")

                res += "\n"
                res += sec.text
                if len(sec.text) > 0:
                    res += "\n\n"

                res += combine(sec.sections, level + 1)

            return res

        txt += combine(self.sections, 2)

        return txt.strip()

    @property
    def langlinks(self):
        if not self._called['langlinks']:
            self._fetch('langlinks')
        return self._langlinks

    @property
    def links(self):
        if not self._called['links']:
            self._fetch('links')
        return self._links

    @property
    def backlinks(self):
        if not self._called['backlinks']:
            self._fetch('backlinks')
        return self._backlinks

    @property
    def categories(self):
        if not self._called['categories']:
            self._fetch('categories')
        return self._categories

    @property
    def categorymembers(self):
        if not self._called['categorymembers']:
            self._fetch('categorymembers')
        return self._categorymembers

    def _fetch(self, call) -> 'WikipediaPage':
        getattr(self.wiki, '_' + call)(self)
        self._called[call] = True
        return self

    def __repr__(self):
        if any(self._called.values()):
            return "{} (id: {}, ns: {})".format(
                self.title,
                self.pageid,
                self.ns
            )
        else:
            return "{} (id: ??, ns: {})".format(
                self.title,
                self.ns
            )
