from enum import Enum
import logging
import re
import requests
log = logging.getLogger(__name__)

# https://www.mediawiki.org/wiki/API:Main_page


class ExtractFormat(Enum):
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
    ExtractFormat.WIKI.value: re.compile(r'\n\n *(===*) (.*?) (===*) *\n'),
    ExtractFormat.HTML.value: re.compile(r'\n? *<h(\d)[^>]*?>(<span[^>]*><\/span>)? *(<span[^>]*>)? *(<span[^>]*><\/span>)? *(.*?) *(<\/span>)?<\/h\d>\n?'),
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

    def article(
            self,
            title: str
    ):
        return WikipediaPage(self, title)

    def _structured(
        self,
        page: 'WikipediaPage'
    ):
        """
        https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bextracts
        """
        params = {
            'action': 'query',
            'prop': 'extracts',
            'titles': page._title
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
        for v in pages.values():
            return self._build_structured(v, page)

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
        page._title = extract['title']
        page._id = extract['pageid']

        section_stack = [page]
        section = None
        prev_pos = 0

        for match in re.finditer(
            RE_SECTION[self.extract_format.value],
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

    def title(self) -> str:
        return self._title

    def level(self) -> int:
        return self._level

    def text(self) -> str:
        return self._text

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
    def __init__(
            self,
            wiki: Wikipedia,
            title: str
    ):
        self.wiki = wiki
        self._title = title
        self._id = 0
        self._summary = ''
        self._section = []
        self._section_mapping = {}
        self._called = {
            'structured': False
        }

    def title(self) -> str:
        return self._title

    def id(self) -> int:
        if not self._called['structured']:
            self.structured()
        return self._id

    def summary(self) -> str:
        if not self._called['structured']:
            self.structured()
        return self._summary

    def sections(self) -> [WikipediaPageSection]:
        if not self._called['structured']:
            self.structured()
        return self._section

    def section_by_title(self, title) -> WikipediaPageSection:
        if not self._called['structured']:
            self.structured()
        return self._section_mapping[title]

    def structured(self) -> 'WikipediaPage':
        self.wiki._structured(
            self
        )
        self._called['structured'] = True
        return self

    def __repr__(self):
        return (
            "{}: ({})\n====\nSummary:\n{}\n======\nSections ({}):\n{}"
        ).format(
            self._title,
            self._id,
            self._summary,
            len(self._section),
            "\n".join(map(repr, self._section))
        )
