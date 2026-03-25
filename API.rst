API
===

Wikipedia
---------
* ``__init__(user_agent: str, language='en', variant=None, extract_format=ExtractFormat.WIKI, headers=None, extra_api_params=None, max_retries=3, retry_wait=1.0, **kwargs)``
* ``page(title, ns=Namespace.MAIN)``
* ``pages(titles)`` — create a ``PagesDict`` of lazy pages (no network call)
* ``coordinates(page, *, limit=10, primary='primary', prop=('globe',), distance_from_point=None (GeoPoint), distance_from_page=None)`` → ``list[Coordinate]``
* ``images(page, *, limit=10, images=None, direction='ascending')`` → ``PagesDict``
* ``geosearch(*, coord=None (GeoPoint), page=None, bbox=None (GeoBox), radius=500, max_dim=None, sort='distance', limit=10, ns=Namespace.MAIN, prop=None)`` → ``PagesDict``
* ``random(*, limit=1, ns=Namespace.MAIN, filter_redir='nonredirects')`` → ``PagesDict``
* ``search(query, *, ns=Namespace.MAIN, limit=10, prop=None, info=None, sort='relevance')`` → ``SearchResults``
* ``batch_coordinates(pages, *, limit=10, primary='primary', prop=('globe',), distance_from_point=None (GeoPoint), distance_from_page=None)`` → ``dict[str, list[Coordinate]]``
* ``batch_images(pages, *, limit=10, images=None, direction='ascending')`` → ``dict[str, PagesDict]``

AsyncWikipedia
--------------
Same constructor parameters as ``Wikipedia``.  All methods are coroutines
(use ``await``).

* ``page(title, ns=Namespace.MAIN)`` — returns an ``AsyncWikipediaPage`` (no network call)
* ``pages(titles)`` — create an ``AsyncPagesDict`` of lazy pages (no network call)
* ``await coordinates(page, ...)`` → ``list[Coordinate]``
* ``await images(page, ...)`` → ``PagesDict``
* ``await geosearch(...)`` → ``PagesDict``
* ``await random(...)`` → ``PagesDict``
* ``await search(query, ...)`` → ``SearchResults``
* ``await batch_coordinates(pages, ...)`` → ``dict[str, list[Coordinate]]``
* ``await batch_images(pages, ...)`` → ``dict[str, PagesDict]``

WikipediaPage
-------------
* ``exists()``
* ``pageid``
* ``title``
* ``namespace``
* ``summary`` - introductory text of the page
* ``text`` - full page text (summary + all sections)
* ``sections`` - top-level sections (list of ``WikipediaPageSection``)
* ``section_by_title(title)`` - last section matching *title* (``WikipediaPageSection``)
* ``sections_by_title(title)`` - all sections matching *title* (list of ``WikipediaPageSection``)
* ``langlinks`` - pages in other languages ({lang: ``WikipediaPage``})
* ``links`` - outbound links ({title: ``WikipediaPage``})
* ``backlinks`` - pages linking to this page ({title: ``WikipediaPage``})
* ``categories`` - categories this page belongs to ({title: ``WikipediaPage``})
* ``categorymembers`` - pages in this category, when ``ns=Namespace.CATEGORY`` ({title: ``WikipediaPage``})
* ``coordinates`` - geographic coordinates (list of ``Coordinate``); triggers ``coordinates`` API call with default params
* ``images`` - images/files on this page (``PagesDict``); triggers ``images`` API call with default params
* ``geosearch_meta`` - ``GeoSearchMeta`` or ``None``; set when page came from ``geosearch()`` (plain property, no fetch)
* ``search_meta`` - ``SearchMeta`` or ``None``; set when page came from ``search()`` (plain property, no fetch)
* ``displaytitle``
* ``varianttitles``
* ``canonicalurl``
* ``fullurl``
* ``editurl``
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
* ``visitingwatchers``
* ``notificationtimestamp``
* ``talkid``
* ``readable``
* ``preload``

AsyncWikipediaPage
------------------
Mirrors ``WikipediaPage`` with the same attributes and interface.  All
data-fetching attributes are explicit ``@property`` definitions that
return coroutines (awaitable with ``await``).

* ``page.title``, ``page.ns``, ``page.namespace``, ``page.language``, ``page.variant`` — plain properties (no await)
* ``await page.summary`` — awaitable property; introductory text
* ``await page.text`` — awaitable property; full page text (summary + all sections)
* ``await page.sections`` — awaitable property; top-level sections (list of ``WikipediaPageSection``)
* ``await page.langlinks`` — awaitable property; ``{lang: AsyncWikipediaPage}`` dict
* ``await page.links`` — awaitable property; ``{title: AsyncWikipediaPage}`` dict
* ``await page.backlinks`` — awaitable property; ``{title: AsyncWikipediaPage}`` dict
* ``await page.categories`` — awaitable property; ``{title: AsyncWikipediaPage}`` dict
* ``await page.categorymembers`` — awaitable property; ``{title: AsyncWikipediaPage}`` dict
* ``await page.coordinates`` — awaitable property; ``list[Coordinate]``
* ``await page.images`` — awaitable property; ``PagesDict``
* ``page.geosearch_meta`` — plain property; ``GeoSearchMeta | None`` (no await)
* ``page.search_meta`` — plain property; ``SearchMeta | None`` (no await)
* ``await page.exists()`` — coroutine method; lazily fetches ``pageid`` via ``info`` if not yet cached
* ``page.section_by_title(title)`` — synchronous; returns last matching section or ``None``
* ``page.sections_by_title(title)`` — synchronous; returns all matching sections (list)

WikipediaPageSection
--------------------
* ``title``
* ``level``
* ``text``
* ``sections``
* ``section_by_title(title)``
* ``full_text(level=1)`` - rendered text of this section and all descendants

ExtractFormat
-------------
* ``WIKI`` - plain-text wiki markup (``==Heading==``)
* ``HTML`` - HTML markup (``<h2>Heading</h2>``)

Namespace
---------
Integer enumeration of MediaWiki namespaces.  Common values:

* ``MAIN`` (0) - ordinary articles
* ``TALK`` (1)
* ``USER`` (2)
* ``FILE`` (6)
* ``TEMPLATE`` (10)
* ``CATEGORY`` (14)

Pass a ``Namespace`` member or a plain ``int`` wherever a namespace is accepted.

Exceptions
----------

All exceptions raised by the library inherit from ``WikipediaException``.
No ``httpx`` or ``json`` exceptions are exposed.

* ``WikipediaException`` - base exception for all Wikipedia-API errors
* ``WikiHttpError(status_code, url)`` - non-success HTTP status from Wikipedia API
* ``WikiRateLimitError(url, retry_after=None)`` - HTTP 429 Too Many Requests; subclass of ``WikiHttpError``
* ``WikiHttpTimeoutError(url)`` - request to Wikipedia API timed out
* ``WikiInvalidJsonError(url)`` - response body was not valid JSON
* ``WikiConnectionError(url)`` - could not connect to Wikipedia API

Exception hierarchy::

    WikipediaException
    ├── WikiHttpError
    │   └── WikiRateLimitError
    ├── WikiHttpTimeoutError
    ├── WikiInvalidJsonError
    └── WikiConnectionError

Typed Data Classes
------------------

``Coordinate``
~~~~~~~~~~~~~~
Frozen dataclass returned by ``coordinates()``.

* ``lat: float`` — latitude
* ``lon: float`` — longitude
* ``primary: bool`` — whether this is the primary coordinate
* ``globe: str`` — celestial body (default ``"earth"``)

``GeoPoint``
~~~~~~~~~~~~
Frozen dataclass used as input for point-based coordinate parameters.

* ``lat: float`` — latitude in range ``[-90.0, 90.0]``
* ``lon: float`` — longitude in range ``[-180.0, 180.0]``

``GeoBox``
~~~~~~~~~~
Frozen dataclass used as input for geosearch bounding boxes.

* ``top_left: GeoPoint`` — north-west corner
* ``bottom_right: GeoPoint`` — south-east corner

``GeoSearchMeta``
~~~~~~~~~~~~~~~~~
Frozen dataclass attached to pages returned by ``geosearch()``.

* ``dist: float`` — distance from search point (metres)
* ``lat: float`` — latitude
* ``lon: float`` — longitude
* ``primary: bool`` — whether the coordinate is primary

``SearchMeta``
~~~~~~~~~~~~~~
Frozen dataclass attached to pages returned by ``search()``.

* ``snippet: str`` — HTML search snippet
* ``size: int`` — page size in bytes
* ``wordcount: int`` — word count
* ``timestamp: str`` — last edit timestamp (ISO 8601)

``SearchResults``
~~~~~~~~~~~~~~~~~
Wrapper returned by ``search()``.

* ``pages: PagesDict`` — matched pages (each has ``search_meta`` set)
* ``totalhits: int`` — total number of matches server-side
* ``suggestion: str | None`` — search suggestion (if any)

``PagesDict``
~~~~~~~~~~~~~
A ``dict[str, WikipediaPage]`` subclass with batch convenience methods.

* ``coordinates(*, ...)`` → ``dict[str, list[Coordinate]]``
* ``images(*, ...)`` → ``dict[str, PagesDict]``

``AsyncPagesDict``
~~~~~~~~~~~~~~~~~~
Async mirror of ``PagesDict``.

* ``await coordinates(*, ...)`` → ``dict[str, list[Coordinate]]``
* ``await images(*, ...)`` → ``dict[str, AsyncPagesDict]``

Retry Behavior
--------------

Transient errors (HTTP 429, 5xx, timeouts, connection errors) are retried
automatically with exponential backoff. The behavior is controlled by two
constructor parameters:

* ``max_retries`` (default: ``3``) - maximum number of retry attempts; set to ``0`` to disable
* ``retry_wait`` (default: ``1.0``) - base wait time in seconds; actual wait is ``retry_wait * 2^attempt``

For HTTP 429, the ``Retry-After`` header is honored when present.

Non-retryable errors (HTTP 4xx other than 429, invalid JSON) raise immediately.
