API
===

Wikipedia
---------
* ``__init__(language='en', extract_format=ExtractFormat.WIKI, user_agent, timeout=10.0)``
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
* ``section_by_title(name)`` - finds section by title (``WikipediaPageSection``)
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

ExtractFormat
-------------
* ``WIKI``
* ``HTML``
