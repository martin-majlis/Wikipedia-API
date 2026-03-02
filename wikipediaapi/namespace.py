from enum import IntEnum
from typing import Union


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
