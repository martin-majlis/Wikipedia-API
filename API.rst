API
===

Wikipedia
---------
* ``__init__(user_agent: str, language='en', extract_format=ExtractFormat.WIKI, headers: Optional[Dict[str, Any]] = None, **kwargs)``
* ``page(title)``

WikipediaPage
-------------
* ``exists()``
* ``pageid``
* ``title`` - title
* ``summary`` - summary of the page
* ``text`` - returns text of the page
* ``sections`` - list of all sections (list of ``WikipediaPageSection``)
* ``langlinks`` - language links to other languages ({lang: ``WikipediaLangLink``})
* ``section_by_title(name)`` - finds last section by title (``WikipediaPageSection``)
* ``sections_by_title(name)`` - finds all section by title (``WikipediaPageSection``)
* ``links`` - links to other pages ({title: ``WikipediaPage``})
* ``categories`` - all categories ({title: ``WikipediaPage``})
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
* ``section_by_title(title)``

ExtractFormat
-------------
* ``WIKI``
* ``HTML``
