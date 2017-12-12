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
* ``title``
* ``summary``
* ``sections``
* ``section_by_title(name)``
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
