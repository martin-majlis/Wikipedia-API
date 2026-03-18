API
===

Wikipedia
---------
* ``__init__(user_agent: str, language='en', variant=None, extract_format=ExtractFormat.WIKI, headers=None, extra_api_params=None, max_retries=3, retry_wait=1.0, **kwargs)``
* ``page(title, ns=Namespace.MAIN)``

AsyncWikipedia
--------------
Same constructor parameters as ``Wikipedia``.

* ``page(title, ns=Namespace.MAIN)`` — returns an ``AsyncWikipediaPage`` (no network call)

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

Retry Behavior
--------------

Transient errors (HTTP 429, 5xx, timeouts, connection errors) are retried
automatically with exponential backoff. The behavior is controlled by two
constructor parameters:

* ``max_retries`` (default: ``3``) - maximum number of retry attempts; set to ``0`` to disable
* ``retry_wait`` (default: ``1.0``) - base wait time in seconds; actual wait is ``retry_wait * 2^attempt``

For HTTP 429, the ``Retry-After`` header is honored when present.

Non-retryable errors (HTTP 4xx other than 429, invalid JSON) raise immediately.
