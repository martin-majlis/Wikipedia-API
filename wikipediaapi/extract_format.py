from enum import IntEnum


class ExtractFormat(IntEnum):
    """Represents extraction format."""

    WIKI = 1
    """
    Allows recognizing subsections

    Example: https://goo.gl/PScNVV
    """

    HTML = 2
    """
    Alows retrieval of HTML tags

    Example: https://goo.gl/1Jwwpr
    """

    # Plain: https://goo.gl/MAv2qz
    # Doesn't allow to recognize subsections
    # PLAIN = 3
