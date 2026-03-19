"""Enumeration for Wikipedia extract format options.

This module defines the ExtractFormat enum which controls how page content
is extracted from the Wikipedia API. Different formats affect how section
headers are recognized, text structure, and markup characters in the
returned strings.
"""

from enum import IntEnum


class ExtractFormat(IntEnum):
    """
    Controls the markup format used when fetching page extracts.

    Pass a value of this enum as the ``extract_format`` argument to
    :class:`~wikipediaapi.Wikipedia` or
    :class:`~wikipediaapi.AsyncWikipedia`.  The chosen format affects
    how section headers are recognised, how text is structured, and what
    markup characters appear in the returned strings.

    Example usage::

        import wikipediaapi
        wiki = wikipediaapi.Wikipedia(
            user_agent='MyBot/1.0',
            language='en',
            extract_format=wikipediaapi.ExtractFormat.HTML,
        )
    """

    WIKI = 1
    """
    Plain-text wiki markup format.

    Section headings are represented as ``==Title==``, ``===Title===``,
    etc., allowing the library to recognise and split on them.  Best
    choice when you only need the textual content without any HTML.

    MediaWiki API reference: https://www.mediawiki.org/wiki/Extension:TextExtracts
    """

    HTML = 2
    """
    HTML format.

    Section headings are represented as ``<h2>``, ``<h3>``, etc.,
    and body text is wrapped in ``<p>`` tags.  Use this format when you
    need to render the content in a browser or HTML-aware renderer.

    MediaWiki API reference: https://www.mediawiki.org/wiki/Extension:TextExtracts
    """

    # Plain: https://goo.gl/MAv2qz
    # Doesn't allow to recognize subsections
    # PLAIN = 3
