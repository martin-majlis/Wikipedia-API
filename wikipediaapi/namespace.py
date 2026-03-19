"""MediaWiki namespace enumeration and utilities.

This module defines the Namespace enum which represents the different
namespaces used by MediaWiki wikis. Each namespace has a specific integer
value and purpose, from main articles (0) to special pages like user pages,
categories, and templates.
"""

from enum import IntEnum
from typing import Union


class Namespace(IntEnum):
    """
    Integer enumeration of MediaWiki namespaces.

    Each Wikipedia page belongs to a namespace identified by an integer.
    Namespace 0 (``MAIN``) contains ordinary articles; other values
    represent talk pages, user pages, category pages, etc.

    Pass a member of this enum wherever a ``WikiNamespace`` is accepted
    (e.g. ``wiki.page("Python", ns=Namespace.MAIN)``).

    Full namespace reference:

    * https://en.wikipedia.org/wiki/Wikipedia:Namespace
    * https://en.wikipedia.org/wiki/Wikipedia:Namespace#Programming
    """

    MAIN = 0
    """Main article namespace (ns=0). Ordinary Wikipedia articles live here."""

    TALK = 1
    """Talk namespace (ns=1). Discussion pages for main-namespace articles."""

    USER = 2
    """User namespace (ns=2). Pages belonging to registered users."""

    USER_TALK = 3
    """User talk namespace (ns=3). Discussion pages for user pages."""

    WIKIPEDIA = 4
    """Wikipedia project namespace (ns=4). Policy and project pages."""

    WIKIPEDIA_TALK = 5
    """Wikipedia talk namespace (ns=5). Discussion of project pages."""

    FILE = 6
    """File namespace (ns=6). Images, audio files, and other media."""

    FILE_TALK = 7
    """File talk namespace (ns=7). Discussion of file pages."""

    MEDIAWIKI = 8
    """MediaWiki namespace (ns=8). Interface messages and system texts."""

    MEDIAWIKI_TALK = 9
    """MediaWiki talk namespace (ns=9). Discussion of interface messages."""

    TEMPLATE = 10
    """Template namespace (ns=10). Reusable wiki templates."""

    TEMPLATE_TALK = 11
    """Template talk namespace (ns=11). Discussion of templates."""

    HELP = 12
    """Help namespace (ns=12). Help and how-to pages."""

    HELP_TALK = 13
    """Help talk namespace (ns=13). Discussion of help pages."""

    CATEGORY = 14
    """Category namespace (ns=14). Category pages that group articles."""

    CATEGORY_TALK = 15
    """Category talk namespace (ns=15). Discussion of category pages."""

    PORTAL = 100
    """Portal namespace (ns=100). Topic-focused entry-point portals."""

    PORTAL_TALK = 101
    """Portal talk namespace (ns=101). Discussion of portals."""

    PROJECT = 102
    """Project namespace (ns=102). WikiProject coordination pages."""

    PROJECT_TALK = 103
    """Project talk namespace (ns=103). Discussion of WikiProject pages."""

    REFERENCE = 104
    """Reference namespace (ns=104). Reference desk pages."""

    REFERENCE_TALK = 105
    """Reference talk namespace (ns=105). Discussion of reference pages."""

    BOOK = 108
    """Book namespace (ns=108). Wikipedia book pages."""

    BOOK_TALK = 109
    """Book talk namespace (ns=109). Discussion of book pages."""

    DRAFT = 118
    """Draft namespace (ns=118). Unreviewed draft articles."""

    DRAFT_TALK = 119
    """Draft talk namespace (ns=119). Discussion of draft pages."""

    EDUCATION_PROGRAM = 446
    """Education Program namespace (ns=446). Educational course pages."""

    EDUCATION_PROGRAM_TALK = 447
    """Education Program talk namespace (ns=447)."""

    TIMED_TEXT = 710
    """TimedText namespace (ns=710). Subtitle/caption files for media."""

    TIMED_TEXT_TALK = 711
    """TimedText talk namespace (ns=711). Discussion of timed-text pages."""

    MODULE = 828
    """Module namespace (ns=828). Lua scripting modules."""

    MODULE_TALK = 829
    """Module talk namespace (ns=829). Discussion of Lua modules."""

    GADGET = 2300
    """Gadget namespace (ns=2300). JavaScript gadget pages."""

    GADGET_TALK = 2301
    """Gadget talk namespace (ns=2301). Discussion of gadget pages."""

    GADGET_DEFINITION = 2302
    """Gadget definition namespace (ns=2302). Gadget definition pages."""

    GADGET_DEFINITION_TALK = 2303
    """Gadget definition talk namespace (ns=2303)."""


#: Type alias for namespace arguments accepted throughout the library.
#: Accepts either a :class:`Namespace` enum member or a raw ``int``,
#: e.g. ``Namespace.CATEGORY`` or simply ``14``.
WikiNamespace = Union[Namespace, int]


def namespace2int(namespace: WikiNamespace) -> int:
    """
    Convert a :class:`WikiNamespace` value to a plain ``int``.

    If *namespace* is a :class:`Namespace` enum member its integer value
    is returned.  If it is already an ``int`` it is returned unchanged.

    :param namespace: namespace to convert
    :return: integer representation of the namespace
    """
    if isinstance(namespace, Namespace):
        return namespace.value

    return namespace
