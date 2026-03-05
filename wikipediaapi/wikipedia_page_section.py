from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .wikipedia import Wikipedia

from .extract_format import ExtractFormat


class WikipediaPageSection:
    """WikipediaPageSection represents section in the page."""

    def __init__(self, wiki: "Wikipedia", title: str, level: int = 0, text: str = "") -> None:
        """Constructs WikipediaPageSection."""
        self.wiki = wiki
        self._title = title
        self._level = level
        self._text = text
        self._section = []  # type: list['WikipediaPageSection']

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
    def sections(self) -> list["WikipediaPageSection"]:
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
