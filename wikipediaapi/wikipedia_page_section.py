"""Wikipedia page section representation.

This module defines the WikipediaPageSection class which represents individual
sections of a Wikipedia page. Sections are organized in a tree structure
with the page summary as the root and headings as child sections.
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .wikipedia import Wikipedia

from .extract_format import ExtractFormat


class WikipediaPageSection:
    """
    Represents a single section (or the root summary) of a Wikipedia page.

    Sections are arranged in a tree: each section may have zero or more
    child sections accessible via :attr:`sections`.  The root of the tree
    is the page summary (level 0); its children are top-level headings
    (level 2 for ``==Heading==`` / ``<h2>``); their children are
    sub-headings, and so on.

    Instances are created by
    :meth:`~wikipediaapi._resources.BaseWikipediaResource._build_extracts`
    and should not normally be constructed directly.

    :attr wiki: the :class:`~wikipediaapi.Wikipedia` instance used to
        determine the extract format when rendering
    """

    def __init__(self, wiki: "Wikipedia", title: str, level: int = 0, text: str = "") -> None:
        """
        Initialise a page section.

        :param wiki: the Wikipedia client; used only for
            :attr:`~wikipediaapi.Wikipedia.extract_format` when rendering
            :meth:`full_text`
        :param title: heading text of this section (empty string for the
            root / summary pseudo-section)
        :param level: heading depth — 0 for the summary, 2 for ``<h2>``
            / ``==...==``, 3 for ``<h3>`` / ``===...===``, etc.
        :param text: plain body text of this section (excluding headings
            and text of sub-sections)
        """
        self.wiki = wiki
        self._title = title
        self._level = level
        self._text = text
        self._section: list["WikipediaPageSection"] = []

    @property
    def title(self) -> str:
        """
        Heading text of this section.

        For the root / summary pseudo-section this is an empty string.

        :return: section heading as a plain string
        """
        return self._title

    @property
    def level(self) -> int:
        """
        Heading depth of this section.

        The summary pseudo-section has level ``0``.  Heading levels follow
        the HTML convention: ``2`` for the outermost heading
        (``==...==`` / ``<h2>``), ``3`` for the next level, and so on.

        :return: integer heading level (0 = summary, 2 = top-level, …)
        """
        return self._level

    @property
    def text(self) -> str:
        """
        Body text of this section, excluding heading and sub-sections.

        The format (plain wiki markup or HTML) matches the
        ``extract_format`` of the :class:`~wikipediaapi.Wikipedia`
        instance that fetched the page.

        :return: section body text as a string
        """
        return self._text

    @property
    def sections(self) -> list["WikipediaPageSection"]:
        """
        Direct child sections of this section.

        Each element is itself a :class:`WikipediaPageSection` that may
        have further children.  Use recursion to traverse the full tree.

        :return: list of immediate sub-sections (may be empty)
        """
        return self._section

    def section_by_title(self, title: str) -> Optional["WikipediaPageSection"]:
        """
        Return the last direct child section whose heading matches *title*.

        When multiple sub-sections share the same heading (rare but
        valid in Wikipedia) the last one is returned.  Returns ``None``
        if no matching child section exists.

        :param title: exact heading text to search for
        :return: the matching :class:`WikipediaPageSection`, or ``None``
        """
        sections = [s for s in self._section if s.title == title]
        if sections:
            return sections[-1]
        return None

    def full_text(self, level: int = 1) -> str:
        """
        Return the rendered text of this section and all its descendants.

        The heading is prepended in the format appropriate for
        ``wiki.extract_format``:

        * :attr:`ExtractFormat.WIKI` — heading as ``==Title==`` (number
          of ``=`` chars = *level*)
        * :attr:`ExtractFormat.HTML` — heading as ``<h{level}>Title</h{level}>``

        Sub-sections are appended recursively with *level* incremented by
        one for each nesting depth.

        :param level: heading depth to use for *this* section's heading;
            child sections use ``level + 1``, etc.  Callers typically
            pass ``2`` for a top-level section.
        :return: full rendered string including heading, body, and all
            descendant sections
        :raises NotImplementedError: if ``wiki.extract_format`` is not
            :attr:`ExtractFormat.WIKI` or :attr:`ExtractFormat.HTML`
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

    def __repr__(self) -> str:
        """Return a string representation of the section.

        Returns:
            A formatted string showing the section title, level, text length,
            and number of subsections.
        """
        return "Section: {} ({}):\n{}\nSubsections ({}):\n{}".format(
            self._title,
            self._level,
            self._text,
            len(self._section),
            "\n".join(map(repr, self._section)),
        )
