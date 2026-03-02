API
===

Wikipedia
---------
* ``__init__(user_agent: str, language='en', variant=Optional[str] = None, extract_format=ExtractFormat.WIKI, headers: Optional[Dict[str, Any]] = None, extra_api_params: Optional[dict[str, Any]] = None, max_retries: int = 3, retry_wait: float = 1.0, **request_kwargs)``
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
* ``varianttitles``
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

Exceptions
----------

All exceptions raised by the library inherit from ``WikipediaException``.
No ``requests`` or ``json`` exceptions are exposed.

* ``WikipediaException`` - base exception for all Wikipedia-API errors
* ``HttpError(status_code, url)`` - non-success HTTP status from Wikipedia API
* ``RateLimitError(url, retry_after=None)`` - HTTP 429 Too Many Requests; subclass of ``HttpError``
* ``HttpTimeoutError(url)`` - request to Wikipedia API timed out
* ``InvalidJsonError(url)`` - response body was not valid JSON
* ``ConnectionError(url)`` - could not connect to Wikipedia API

Exception hierarchy::

    WikipediaException
    ├── HttpError
    │   └── RateLimitError
    ├── HttpTimeoutError
    ├── InvalidJsonError
    └── ConnectionError

Retry Behavior
--------------

Transient errors (HTTP 429, 5xx, timeouts, connection errors) are retried
automatically with exponential backoff. The behavior is controlled by two
constructor parameters:

* ``max_retries`` (default: ``3``) - maximum number of retry attempts; set to ``0`` to disable
* ``retry_wait`` (default: ``1.0``) - base wait time in seconds; actual wait is ``retry_wait * 2^attempt``

For HTTP 429, the ``Retry-After`` header is honored when present.

Non-retryable errors (HTTP 4xx other than 429, invalid JSON) raise immediately.
