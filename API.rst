API
===

Wikipedia
---------
* ``__init__(user_agent: str, language='en', variant=None, extract_format=ExtractFormat.WIKI, headers=None, extra_api_params=None, max_retries=3, retry_wait=1.0, **kwargs)``
* ``page(title, ns=Namespace.MAIN)``
* ``pages(titles)`` — create a ``PagesDict`` of lazy pages (no network call)
* ``coordinates(page, *, limit=10, primary='primary', prop=('globe',), distance_from_point=None (GeoPoint), distance_from_page=None)`` → ``list[Coordinate]``
* ``images(page, *, limit=10, images=None, direction=Direction.ASCENDING)`` → ``ImagesDict``
* ``imageinfo(image, *, prop=('url', 'width', 'height', ...), limit=1)`` → ``list[ImageInfo]``
* ``batch_imageinfo(images, *, prop=('url', 'width', 'height', ...), limit=1)`` → ``dict[str, list[ImageInfo]]``
* ``geosearch(*, coord=None (GeoPoint), page=None, bbox=None (GeoBox), radius=500, max_dim=None, sort='distance', limit=10, ns=Namespace.MAIN, prop=None)`` → ``PagesDict``
* ``random(*, limit=1, ns=Namespace.MAIN, filter_redir='nonredirects')`` → ``PagesDict``
* ``search(query, *, ns=Namespace.MAIN, limit=10, prop=None, info=None, sort='relevance')`` → ``SearchResults``
* ``batch_coordinates(pages, *, limit=10, primary='primary', prop=('globe',), distance_from_point=None (GeoPoint), distance_from_page=None)`` → ``dict[WikipediaPage, list[Coordinate]]``
* ``batch_images(pages, *, limit=10, images=None, direction=Direction.ASCENDING)`` → ``dict[str, PagesDict]``

AsyncWikipedia
--------------
Same constructor parameters as ``Wikipedia``.  All methods are coroutines
(use ``await``).

* ``page(title, ns=Namespace.MAIN)`` — returns an ``AsyncWikipediaPage`` (no network call)
* ``pages(titles)`` — create an ``AsyncPagesDict`` of lazy pages (no network call)
* ``await coordinates(page, ...)`` → ``list[Coordinate]``
* ``await images(page, ...)`` → ``ImagesDict``
* ``await imageinfo(image, ...)`` → ``list[ImageInfo]``
* ``await batch_imageinfo(images, ...)`` → ``dict[str, list[ImageInfo]]``
* ``await geosearch(...)`` → ``PagesDict``
* ``await random(...)`` → ``PagesDict``
* ``await search(query, ...)`` → ``SearchResults``
* ``await batch_coordinates(pages, ...)`` → ``dict[AsyncWikipediaPage, list[Coordinate]]``
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
* ``images`` - images/files on this page (``ImagesDict``); triggers ``images`` API call with default params
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
* ``await page.images`` — awaitable property; ``ImagesDict``
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

WikipediaImage
---------------
Lazy representation of a Wikipedia/Commons file page.  No network call is
made at construction time; accessing ``imageinfo`` (or any convenience
property derived from it) triggers the minimum API call needed.

* ``title`` — file title including the ``File:`` prefix
* ``language`` — two-letter language code
* ``namespace`` — integer namespace number (6 for files)
* ``pageid`` — MediaWiki page ID
* ``imageinfo`` — list of ``ImageInfo`` objects (lazy-fetched; triggers API call)
* ``url`` — full URL of the file (from first ``ImageInfo``)
* ``width`` — image width in pixels (from first ``ImageInfo``)
* ``height`` — image height in pixels (from first ``ImageInfo``)
* ``size`` — file size in bytes (from first ``ImageInfo``)
* ``mime`` — MIME type (from first ``ImageInfo``)
* ``mediatype`` — MediaWiki media type (from first ``ImageInfo``)
* ``sha1`` — SHA-1 hash of the file (from first ``ImageInfo``)
* ``timestamp`` — ISO 8601 timestamp of this revision (from first ``ImageInfo``)
* ``user`` — username of the uploader (from first ``ImageInfo``)
* ``descriptionurl`` — URL of the file description page (from first ``ImageInfo``)
* ``descriptionshorturl`` — short URL of the description page (from first ``ImageInfo``)

AsyncWikipediaImage
--------------------
Async mirror of ``WikipediaImage``.  All properties that trigger network calls
are awaitable (use ``await``).

* ``title``, ``language``, ``namespace``, ``pageid`` — plain properties (no await)
* ``await imageinfo`` — awaitable property; list of ``ImageInfo`` objects
* ``await url`` — awaitable property; full URL of the file
* ``await width`` — awaitable property; image width in pixels
* ``await height`` — awaitable property; image height in pixels
* ``await size`` — awaitable property; file size in bytes
* ``await mime`` — awaitable property; MIME type
* ``await mediatype`` — awaitable property; MediaWiki media type
* ``await sha1`` — awaitable property; SHA-1 hash of the file
* ``await timestamp`` — awaitable property; ISO 8601 timestamp
* ``await user`` — awaitable property; username of uploader
* ``await descriptionurl`` — awaitable property; description page URL
* ``await descriptionshorturl`` — awaitable property; short description page URL

ImagesDict
----------
A ``dict[str, WikipediaImage]`` subclass with batch convenience methods.

* ``imageinfo(*, prop=_DEFAULT_PROP, limit=1)`` → ``dict[str, list[ImageInfo]]`` — batch-fetch ``imageinfo`` for all images via ``batch_imageinfo()``

AsyncImagesDict
---------------
Async mirror of ``ImagesDict``.

* ``await imageinfo(*, prop=_DEFAULT_PROP, limit=1)`` → ``dict[str, list[ImageInfo]]``

ExtractFormat
-------------
* ``WIKI`` - plain-text wiki markup (``==Heading==``)
* ``HTML`` - HTML markup (``<h2>Heading</h2>``)

Direction
---------
Sort direction enum used by image methods.

* ``ASCENDING`` - ascending order (default)
* ``DESCENDING`` - descending order

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

``ImageInfo``
~~~~~~~~~~~~~
Frozen dataclass representing one file revision from ``prop=imageinfo``.
All fields are optional and depend on the ``iiprop`` parameter and file
availability.

* ``url: str | None`` — full URL of the file
* ``descriptionurl: str | None`` — URL of the file description page
* ``descriptionshorturl: str | None`` — short URL of the description page
* ``width: int | None`` — image width in pixels
* ``height: int | None`` — image height in pixels
* ``size: int | None`` — file size in bytes
* ``mime: str | None`` — MIME type (e.g. ``"image/jpeg"``)
* ``mediatype: str | None`` — MediaWiki media type (e.g. ``"BITMAP"``)
* ``sha1: str | None`` — SHA-1 hash of the file content
* ``timestamp: str | None`` — ISO 8601 timestamp of this revision
* ``user: str | None`` — username of the uploader

``SearchResults``
~~~~~~~~~~~~~~~~~
Wrapper returned by ``search()``.

* ``pages: PagesDict`` — matched pages (each has ``search_meta`` set)
* ``totalhits: int`` — total number of matches server-side
* ``suggestion: str | None`` — search suggestion (if any)

``PagesDict``
~~~~~~~~~~~~~
A ``dict[str, WikipediaPage]`` subclass with batch convenience methods.

* ``coordinates(*, ...)`` → ``dict[WikipediaPage, list[Coordinate]]``
* ``images(*, ...)`` → ``dict[str, PagesDict]``

``AsyncPagesDict``
~~~~~~~~~~~~~~~~~~
Async mirror of ``PagesDict``.

* ``await coordinates(*, ...)`` → ``dict[AsyncWikipediaPage, list[Coordinate]]``
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

Enum Parameters
---------------

Many API methods accept strongly-typed enum parameters for better type safety
while maintaining full backward compatibility with string values.

Available Enums
~~~~~~~~~~~~~~~

**Direction**
  Sort direction for image methods.

  * ``ASCENDING`` - ascending order (default)
  * ``DESCENDING`` - descending order

**SearchSort**
  Sort options for search results.

  * ``RELEVANCE`` - sort by relevance (default)
  * ``NONE`` - no sorting
  * ``RANDOM`` - random order
  * ``CREATE_TIMESTAMP_ASC`` - sort by creation time (oldest first)
  * ``CREATE_TIMESTAMP_DESC`` - sort by creation time (newest first)
  * ``INCOMING_LINKS_ASC`` - sort by incoming links (fewest first)
  * ``INCOMING_LINKS_DESC`` - sort by incoming links (most first)
  * ``JUST_MATCH`` - sort by match quality
  * ``LAST_EDIT_ASC`` - sort by last edit time (oldest first)
  * ``LAST_EDIT_DESC`` - sort by last edit time (newest first)
  * ``TITLE_NATURAL_ASC`` - title natural sort ascending
  * ``TITLE_NATURAL_DESC`` - title natural sort descending
  * ``USER_RANDOM`` - user-specific random

**SearchProp**
  Properties to return in search results (deprecated upstream but still supported).

  * ``SIZE`` - page size in bytes
  * ``WORDCOUNT`` - word count
  * ``TIMESTAMP`` - last edit timestamp
  * ``SNIPPET`` - search snippet with highlighting
  * ``TITLE_SNIPPET`` - title snippet with highlighting
  * ``REDIRECT_TITLE`` - redirect title
  * ``REDIRECT_SNIPPET`` - redirect snippet with highlighting
  * ``SECTION_TITLE`` - section title
  * ``SECTION_SNIPPET`` - section snippet with highlighting
  * ``IS_FILE_MATCH`` - whether file content matched
  * ``CATEGORY_SNIPPET`` - category snippet with highlighting
  * ``SCORE`` - relevance score (deprecated)
  * ``HAS_RELATED`` - has related suggestions (deprecated)
  * ``EXTENSION_DATA`` - extension-generated data

**SearchInfo**
  Metadata to return in search results.

  * ``TOTAL_HITS`` - total number of matches
  * ``SUGGESTION`` - spelling suggestion
  * ``REWRITTEN_QUERY`` - rewritten query

**SearchWhat**
  Type of search to perform.

  * ``TEXT`` - search page text (default)
  * ``TITLE`` - search page titles only
  * ``NEAR_MATCH`` - near match search

**SearchQiProfile**
  Query-independent ranking profile.

  * ``ENGINE_AUTO_SELECT`` - let engine choose (default)
  * ``CLASSIC`` - classic ranking
  * ``CLASSIC_NO_BOOST_LINKS`` - classic without link boost
  * ``EMPTY`` - empty profile (debug only)
  * ``GROWTH_UNDERLINKED`` - prioritize underlinked articles
  * ``MLR_1024RS`` - machine learning ranking
  * ``MLR_1024RS_NEXT`` - next generation ML ranking
  * ``POPULAR_INCLINKS`` - prioritize popular pages with links
  * ``POPULAR_INCLINKS_PV`` - prioritize popular pages with pageviews
  * ``WSUM_INCLINKS`` - weighted sum of incoming links
  * ``WSUM_INCLINKS_PV`` - weighted sum of links and pageviews

**GeoSearchSort**
  Sort options for geographic search.

  * ``DISTANCE`` - sort by distance (default)
  * ``RELEVANCE`` - sort by relevance

**Globe**
  Celestial body for coordinates.

  * ``EARTH`` - Earth (default)
  * ``MARS`` - Mars
  * ``MOON`` - Moon
  * ``VENUS`` - Venus

**CoordinateType**
  Coordinate filtering options.

  * ``ALL`` - all coordinates (default)
  * ``PRIMARY`` - primary coordinates only
  * ``SECONDARY`` - secondary coordinates only

**RedirectFilter**
  Redirect filtering for random pages.

  * ``ALL`` - all pages (redirects and non-redirects)
  * ``REDIRECTS`` - redirect pages only
  * ``NONREDIRECTS`` - non-redirect pages only (default)

**CoordinatesProp**
  Additional coordinate properties to fetch.

  * ``COUNTRY`` - ISO 3166-1 alpha-2 country code (e.g. US or RU)
  * ``DIM`` - Approximate size of the object in meters
  * ``GLOBE`` - Which terrestrial body the coordinates are relative to (e.g. moon or pluto)
  * ``NAME`` - Name of the object the coordinates point to
  * ``REGION`` - ISO 3166-2 region code (the part after the dash; e.g. FL or MOS)
  * ``TYPE`` - Type of the object the coordinates point to

Usage Examples
~~~~~~~~~~~~~~~~

**Basic Enum Usage**

Type-safe enum usage (recommended)::

    import wikipediaapi
    from wikipediaapi import (
        SearchProp, SearchInfo, SearchWhat, SearchQiProfile, SearchSort,
        GeoSearchSort, Globe, CoordinateType, RedirectFilter, Direction
    )
    from wikipediaapi import GeoPoint

    wiki = wikipediaapi.Wikipedia('MyApp/1.0', 'en')

    # Search with comprehensive enum parameters
    results = wiki.search(
        "python",
        prop=[SearchProp.SIZE, SearchProp.WORDCOUNT, SearchProp.TIMESTAMP],
        info=[SearchInfo.TOTAL_HITS, SearchInfo.SUGGESTION],
        what=SearchWhat.TEXT,
        qi_profile=SearchQiProfile.ENGINE_AUTO_SELECT,
        sort=SearchSort.RELEVANCE
    )

    # Geosearch with enum parameters
    point = GeoPoint(lat=51.5074, lon=-0.1278)
    geo_results = wiki.geosearch(
        coord=point,
        sort=GeoSearchSort.DISTANCE,
        globe=Globe.EARTH
    )

    # Coordinates with enum parameters
    page = wiki.page("Mount Everest")
    coords = wiki.coordinates(
        page,
        prop=[CoordinatesProp.GLOBE, CoordinatesProp.TYPE, CoordinatesProp.COUNTRY],
        primary=CoordinateType.ALL
    )

    # Random pages with enum filter
    random_pages = wiki.random(filter_redirect=RedirectFilter.NONREDIRECTS, limit=5)

    # Images with enum direction
    page = wiki.page("London")
    images = wiki.images(page, direction=Direction.ASCENDING)

**Advanced Enum Examples**

Different search strategies::

    # Search by last edited time (newest first)
    results = wiki.search("python", sort=SearchSort.LAST_EDIT_DESC)

    # Search by incoming links (most linked first)
    results = wiki.search("python", sort=SearchSort.INCOMING_LINKS_DESC)

    # Search by title (alphabetical)
    results = wiki.search("python", sort=SearchSort.TITLE_NATURAL_ASC)

    # Random search order
    results = wiki.search("python", sort=SearchSort.RANDOM)

Geographic search on different celestial bodies::

    # Search on Mars
    mars_point = GeoPoint(lat=14.5, lon=175.5)
    mars_results = wiki.geosearch(
        coord=mars_point,
        globe=Globe.MARS,
        sort=GeoSearchSort.DISTANCE,
        radius=1000
    )

    # Search on the Moon
    moon_point = GeoPoint(lat=0.7, lon=23.4)
    moon_results = wiki.geosearch(
        coord=moon_point,
        globe=Globe.MOON,
        sort=GeoSearchSort.DISTANCE,
        radius=500
    )

Coordinate filtering::

    # Get only primary coordinates
    primary_coords = wiki.coordinates(page, primary=CoordinateType.PRIMARY)

    # Get only secondary coordinates
    secondary_coords = wiki.coordinates(page, primary=CoordinateType.SECONDARY)

    # Get all coordinates (primary + secondary)
    all_coords = wiki.coordinates(page, primary=CoordinateType.ALL)

    # Get coordinates with specific properties
    coords_with_props = wiki.coordinates(
        page,
        prop=[CoordinatesProp.GLOBE, CoordinatesProp.TYPE, CoordinatesProp.COUNTRY]
    )

Redirect filtering::

    # Get only redirect pages
    redirects = wiki.random(filter_redirect=RedirectFilter.REDIRECTS, limit=10)

    # Get only non-redirect pages
    articles = wiki.random(filter_redirect=RedirectFilter.NONREDIRECTS, limit=10)

    # Get all pages
    all_pages = wiki.random(filter_redirect=RedirectFilter.ALL, limit=10)

**Async Enum Usage**

All enum parameters work identically in the async API::

    import asyncio
    from wikipediaapi._enums import SearchSort, GeoSearchSort, Globe

    async def search_examples():
        wiki = wikipediaapi.AsyncWikipedia('MyApp/1.0', 'en')

        # Async search with enum
        results = await wiki.search("python", sort=SearchSort.RELEVANCE)

        # Async geosearch with enum
        point = GeoPoint(lat=51.5074, lon=-0.1278)
        geo_results = await wiki.geosearch(
            coord=point,
            sort=GeoSearchSort.DISTANCE,
            globe=Globe.EARTH
        )

        return results, geo_results

    results, geo_results = asyncio.run(search_examples())

Backward-compatible string usage::

    # All of these still work exactly the same
    results = wiki.search("python", sort="relevance")
    geo_results = wiki.geosearch(coord=point, sort="distance", globe="earth")
    coords = wiki.coordinates(page, prop=["globe", "type", "country"], primary="all")
    random_pages = wiki.random(filter_redirect="nonredirects", limit=5)
    images = wiki.images(page, direction="ascending")

**Mixed Enum and String Usage**

You can mix enums and strings in the same call::

    # Mix enum and string parameters
    results = wiki.search("python", sort=SearchSort.RELEVANCE, ns=0)  # ns as int
    geo_results = wiki.geosearch(
        coord=point,
        sort=GeoSearchSort.DISTANCE,  # enum
        globe="earth",               # string
        radius=1000
    )

    # This flexibility makes migration easy

Type Aliases
~~~~~~~~~~~~

For function signatures, the library uses ``Wiki*`` type aliases that accept
both enum members and strings:

* ``WikiDirection`` = ``Union[Direction, str]``
* ``WikiCoordinateType`` = ``Union[CoordinateType, str]``
* ``WikiGlobe`` = ``Union[Globe, str]``
* ``WikiSearchSort`` = ``Union[SearchSort, str]``
* ``WikiSearchProp`` = ``Union[SearchProp, str]``
* ``WikiSearchInfo`` = ``Union[SearchInfo, str]``
* ``WikiSearchWhat`` = ``Union[SearchWhat, str]``
* ``WikiSearchQiProfile`` = ``Union[SearchQiProfile, str]``
* ``WikiGeoSearchSort`` = ``Union[GeoSearchSort, str]``
* ``WikiRedirectFilter`` = ``Union[RedirectFilter, str]``
* ``WikiCoordinatesProp`` = ``Union[CoordinatesProp, str]``

This means you can write type-annotated code that accepts either form::

    def search_wiki(query: str, sort: WikiSearchSort) -> SearchResults:
        wiki = wikipediaapi.Wikipedia('MyApp/1.0')
        return wiki.search(query, sort=sort)

    def geo_search_wiki(
        coord: GeoPoint,
        sort: WikiGeoSearchSort,
        globe: WikiGlobe
    ) -> PagesDict:
        wiki = wikipediaapi.Wikipedia('MyApp/1.0')
        return wiki.geosearch(coord=coord, sort=sort, globe=globe)

    # Both calls work
    search_wiki("python", SearchSort.RELEVANCE)  # Type-safe
    search_wiki("python", "relevance")          # Backward compatible

    geo_search_wiki(point, GeoSearchSort.DISTANCE, Globe.EARTH)  # Type-safe
    geo_search_wiki(point, "distance", "earth")                   # Backward compatible

Converter Functions
~~~~~~~~~~~~~~~~~~

If you need to convert enum values to strings manually (e.g., for debugging
or custom API calls), use the converter functions:

* ``direction2str(value: WikiDirection) -> str``
* ``coordinate_type2str(value: WikiCoordinateType) -> str``
* ``globe2str(value: WikiGlobe) -> str``
* ``search_sort2str(value: WikiSearchSort) -> str``
* ``search_prop2str(value: WikiSearchProp) -> str``
* ``search_info2str(value: WikiSearchInfo) -> str``
* ``search_what2str(value: WikiSearchWhat) -> str``
* ``search_qi_profile2str(value: WikiSearchQiProfile) -> str``
* ``geosearch_sort2str(value: WikiGeoSearchSort) -> str``
* ``redirect_filter2str(value: WikiRedirectFilter) -> str``
* ``coordinates_prop2str(value: WikiCoordinatesProp) -> str``

All converters handle both enum members and strings gracefully::

    from wikipediaapi._enums import (
        search_sort2str, SearchSort,
        geosearch_sort2str, GeoSearchSort,
        globe2str, Globe
    )

    # Enum to string conversion
    assert search_sort2str(SearchSort.RELEVANCE) == "relevance"
    assert geosearch_sort2str(GeoSearchSort.DISTANCE) == "distance"
    assert globe2str(Globe.EARTH) == "earth"

    # String pass-through (unchanged)
    assert search_sort2str("relevance") == "relevance"
    assert geosearch_sort2str("distance") == "distance"
    assert globe2str("earth") == "earth"

    # Custom values pass through unchanged
    assert search_sort2str("custom_sort") == "custom_sort"
    assert globe2str("custom_globe") == "custom_globe"

**Use Cases for Converter Functions**

::

    # Debugging API parameters
    def debug_search_params(sort: WikiSearchSort):
        sort_str = search_sort2str(sort)
        print(f"Searching with sort: {sort_str}")
        return wiki.search("python", sort=sort)

    # Building custom API URLs
    def build_custom_search_url(sort: WikiSearchSort):
        sort_str = search_sort2str(sort)
        return f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=python&srsort={sort_str}"

    # Logging and monitoring
    import logging
    logger = logging.getLogger(__name__)

    def log_geosearch_params(sort: WikiGeoSearchSort, globe: WikiGlobe):
        logger.info(f"Geosearch: sort={geosearch_sort2str(sort)}, globe={globe2str(globe)}")
        return wiki.geosearch(coord=point, sort=sort, globe=globe)
