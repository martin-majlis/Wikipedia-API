import logging
import re
import requests
log = logging.getLogger(__name__)

# https://www.mediawiki.org/wiki/API:Main_page

RE_SECTION = re.compile(r'\n\n(===*) (.*?) (===*)\n')


class Wikipedia(object):
    def __init__(
            self,
            language='en',
            user_agent='Wikipedia-API (https://github.com/martin-majlis/Wikipedia-API)',
    ):
        '''
        Language of the API being requested.
        Select language from `list of all Wikipedias <http://meta.wikimedia.org/wiki/List_of_Wikipedias>`_.
        '''
        self.language = language.strip().lower()
        self.user_agent = user_agent

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
            'explaintext': True,
            'titles': page.title
        }

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
        # print(text)
        page.title = extract['title']
        page.id = extract['pageid']

        section_stack = [page]
        section_stack_pos = 0
        section = None
        prev_pos = 0

        for match in re.finditer(RE_SECTION, extract['extract']):
            print(match.start(), match.end())
            if page.summary == '':
                page.summary = extract['extract'][0:match.start()]
            else:
                section.text = extract['extract'][prev_pos:match.start()]

            sec_title = match.group(2)
            sec_level = len(match.group(1)) - 1
            section = WikipediaPageSection(
                sec_title,
                sec_level
            )
            section_stack[sec_level - 1].section.append(section)
            if sec_level > section_stack_pos:
                section_stack.append(section)
            elif sec_level < section_stack_pos:
                section_stack.pop()
            section_stack_pos = sec_level

            prev_pos = match.end()
            page.section_mapping[section.title] = section

            match = RE_SECTION.search(extract['extract'])

        if prev_pos > 0:
            section.text = extract['extract'][prev_pos:]


class WikipediaPageSection(object):
    def __init__(
            self,
            title: str,
            level=0,
            text=''
    ):
        self.title = title
        self.level = level
        self.text = text
        self.section = []

    def __repr__(self):
        return "Section: {} ({}): {}".format(
            self.title,
            self.level,
            self.text
        )


class WikipediaPage(object):
    def __init__(
            self,
            wiki: Wikipedia,
            title: str
    ):
        self.wiki = wiki
        self.title = title
        self.id = 0
        self.summary = ''
        self.section = []
        self.section_mapping = {}
        self.called = {
            'structured': False
        }

    def summary(self):
        if not self.called['structured']:
            self.structured()
        return self.summary

    def sections(self):
        if not self.called['structured']:
            self.structured()
        return self.section

    def section_by_title(self, title):
        if not self.called['structured']:
            self.structured()
        return self.section_mapping[title]

    def structured(self):
        self.wiki._structured(
            self
        )
        self.called['structured'] = True

    def __repr__(self):
        return "{}: ({})\n====\nSummary:\n{}\n======\nSections:\n{}".format(
            self.title,
            self.id,
            self.summary,
            "\n".join(map(repr, self.section))
        )
