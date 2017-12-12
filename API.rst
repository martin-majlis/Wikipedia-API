API
===

Wikipedia
---------
* ``__init__(language='en', extract_format, user_agent)``
* ``article(title)``

WikipediaPage
-------------
* ``exists()``
* ``pageid``
* ``title`` - title
* ``summary`` - summary of the page
* ``sections`` - list of all sections (list of ``WikipediaPageSection``)
* ``langlinks`` - list of all language links to other languages (``WikipediaLangLink``)
* ``section_by_title(name)`` - finds section by title (``WikipediaPageSection``)
* ``displaytitle``
* ``canonicalurl``
* ``ns``
* ``contentmodel``
* ``pagelanguage``
* ``pagelanguagehtmlcode``
* ``pagelanguagedir``
* ``touched``
* ``lastrevid``
* ``length``
* ``protection``
* ``restrictiontypes``
* ``watchers``
* ``notificationtimestamp``
* ``talkid``
* ``fullurl``
* ``editurl``
* ``readable``
* ``preload``


WikipediaPageSection
--------------------
* ``title``
* ``level``
* ``text``
* ``sections``

WikipediaLangLink
-----------------
* ``lang``
* ``title``
* ``url``

ExtractFormat
-------------
* ``WIKI``
* ``HTML``
