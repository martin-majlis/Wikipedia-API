Design
======

This document describes the internal architecture of ``Wikipedia-API``,
explains how the classes interact with each other, and provides a
step-by-step guide for adding support for a new MediaWiki API call.

.. contents:: Table of Contents
   :depth: 3
   :local:


Overview
--------

``Wikipedia-API`` is structured around two independent concerns:

1. **HTTP transport** — how to make HTTP requests (sync vs. async,
   retries, rate-limit handling).
2. **API logic** — how to build MediaWiki query parameters and parse
   the JSON responses into Python objects.

Each concern is implemented as an abstract mixin.  Concrete client
classes are assembled by combining one transport mixin with one API
mixin through Python's multiple inheritance.  This keeps the two layers
entirely decoupled: the API logic never imports ``httpxyz``, and the
transport layer knows nothing about MediaWiki.


File Layout
-----------

::

    wikipediaapi/
    ├── __init__.py              # Public exports
    ├── cli.py                   # Command line interface (main entry point)
    ├── commands/                # CLI command modules
    │   ├── __init__.py
    │   ├── base.py              # Shared utilities and common options
    │   ├── page_commands.py     # Page content commands
    │   ├── link_commands.py     # Link-related commands
    │   ├── category_commands.py # Category commands
    │   ├── geo_commands.py      # Geographic commands
    │   └── search_commands.py    # Search and discovery commands
    ├── _http_client/            # Transport layer package
    │   ├── __init__.py
    │   ├── base_http_client.py  # Shared retry & config logic
    │   ├── sync_http_client.py   # Blocking httpxyz.Client
    │   ├── async_http_client.py  # Non-blocking httpxyz.AsyncClient
    │   ├── retry_utils.py        # Retry utilities
    │   └── retry_after_wait.py   # Retry-After header handling
    ├── _resources/              # API layer package
    │   ├── __init__.py
    │   ├── base_wikipedia_resource.py  # Param builders, parsers, dispatchers
    │   ├── wikipedia_resource.py      # Sync public API methods
    │   └── async_wikipedia_resource.py # Async public API methods
    ├── _types/                  # Typed dataclasses package
    │   ├── __init__.py
    │   ├── coordinate.py         # Coordinate dataclass
    │   ├── geo_point.py          # GeoPoint dataclass
    │   ├── geo_box.py            # GeoBox dataclass
    │   ├── geo_search_meta.py    # GeoSearchMeta dataclass
    │   ├── search_meta.py        # SearchMeta dataclass
    │   └── search_results.py     # SearchResults dataclass
    ├── _params/                 # Query parameter dataclasses package
    │   ├── __init__.py
    │   ├── base_params.py       # Base parameter class
    │   ├── coordinates_params.py # CoordinatesParams
    │   ├── geo_search_params.py  # GeoSearchParams
    │   ├── images_params.py      # ImagesParams
    │   ├── random_params.py      # RandomParams
    │   ├── search_params.py      # SearchParams
    │   └── protocols.py          # Protocol constants
    ├── _pages_dict/             # PagesDict package
    │   ├── __init__.py
    │   ├── base_pages_dict.py   # Base PagesDict functionality
    │   ├── pages_dict.py         # PagesDict (sync)
    │   └── async_pages_dict.py   # AsyncPagesDict
    ├── _enums/                  # Enums package
    │   ├── __init__.py
    │   ├── coordinate_type.py    # CoordinateType enum
    │   ├── coordinates_prop.py  # CoordinatesProp enum
    │   ├── direction.py          # Direction enum
    │   ├── geosearch_sort.py     # GeoSearchSort enum
    │   ├── globe.py              # Globe enum
    │   ├── namespace.py          # Namespace enum
    │   ├── redirect_filter.py    # RedirectFilter enum
    │   ├── search_info.py        # SearchInfo enum
    │   ├── search_prop.py        # SearchProp enum
    │   ├── search_qi_profile.py  # SearchQiProfile enum
    │   ├── search_sort.py        # SearchSort enum
    │   └── search_what.py        # SearchWhat enum
    ├── exceptions/              # Exception classes package
    │   ├── __init__.py
    │   ├── wikipedia_exception.py      # Base exception
    │   ├── wiki_connection_error.py     # Connection errors
    │   ├── wiki_http_error.py            # HTTP errors
    │   ├── wiki_http_timeout_error.py   # Timeout errors
    │   ├── wiki_invalid_json_error.py   # JSON parsing errors
    │   └── wiki_rate_limit_error.py     # Rate limiting errors
    ├── wikipedia.py             # Wikipedia (sync concrete client)
    ├── async_wikipedia.py       # AsyncWikipedia (async concrete client)
    ├── _base_wikipedia_page.py  # BaseWikipediaPage (shared page state & methods)
    ├── wikipedia_page.py        # WikipediaPage (lazy sync page object)
    ├── async_wikipedia_page.py  # AsyncWikipediaPage (lazy async page object)
    ├── wikipedia_page_section.py  # WikipediaPageSection
    ├── extract_format.py        # ExtractFormat enum (WIKI / HTML)
    └── namespace.py             # Legacy namespace module (redirects to _enums.namespace)


Class Hierarchy
---------------

The inheritance chains are::

    BaseHTTPClient
    ├── SyncHTTPClient
    └── AsyncHTTPClient

    BaseWikipediaResource
    ├── WikipediaResource
    └── AsyncWikipediaResource

    BaseWikipediaPage
    ├── WikipediaPage
    └── AsyncWikipediaPage

Concrete clients compose one transport and one API mixin::

    Wikipedia(WikipediaResource, SyncHTTPClient)
    AsyncWikipedia(AsyncWikipediaResource, AsyncHTTPClient)

Page objects hold a back-reference to the client and call it lazily::

    WikipediaPage(BaseWikipediaPage)  ──back-ref──►  Wikipedia
    AsyncWikipediaPage(BaseWikipediaPage)  ────────►  AsyncWikipedia

``BaseWikipediaPage`` holds all state (``_attributes``, ``_called``,
``_section_mapping``, …) and all code whose behaviour is identical
regardless of sync vs. async: ``ATTRIBUTES_MAPPING``, ``__init__``,
the ``language``/``variant``/``title``/``ns`` properties,
``sections_by_title``, and ``section_by_title``.

The subclasses are responsible for the fundamentally different parts:

* ``_fetch`` — ``def`` in sync, ``async def`` in async.
* ``_info_attr(name)`` — sync helper returns cached info attr (fetching
  if needed); async version is ``async def``.
* ``sections`` property — sync auto-fetches; async requires an explicit
  ``await page.summary`` first.
* ``exists()`` — sync auto-fetches via ``self.pageid``; async is a
  coroutine method that lazily fetches ``pageid`` via ``info``.
* All data-fetching surface (``summary``, ``langlinks``, ``pageid``, …)
  — explicit ``@property`` in both; async properties return coroutines
  (``await page.summary``, ``await page.pageid``, etc.).
* ``WikipediaPage`` also overrides ``sections_by_title`` to trigger an
  automatic ``extracts`` fetch (the base version is read-only from cache).


Full Class Diagram
~~~~~~~~~~~~~~~~~~

::

    ┌─────────────────────────┐      ┌──────────────────────────────┐
    │     BaseHTTPClient      │      │    BaseWikipediaResource     │
    │  _get(lang, params)     │      │  _construct_params()         │
    │  __init__(...)          │      │  _make_page()                │
    │  _check_and_correct_    │      │  _common_attributes()        │
    │    params()             │      │  _create_section()           │
    └────────────┬────────────┘      │  _build_extracts()           │
                 │                   │  _build_info()               │
         ┌───────┴────────┐          │  _build_langlinks()          │
         │                │          │  _build_links()              │
    ┌────┴──────┐  ┌───────┴──────┐  │  _build_backlinks()          │
    │  Sync     │  │  Async       │  │  _build_categories()         │
    │  HTTP     │  │  HTTP        │  │  _build_categorymembers()    │
    │  Client   │  │  Client      │  │  _process_prop_response()    │
    │           │  │              │  │  _dispatch_prop()            │
    │  _get()   │  │  _get()      │  │  _async_dispatch_prop()      │
    │  (sync)   │  │  (async)     │  │  _dispatch_prop_paginated()  │
    └────┬──────┘  └───────┬──────┘  │  _async_dispatch_prop_pag..()│
         │                 │         │  _dispatch_list()            │
         │                 │         │  _async_dispatch_list()      │
         │                 │         │  _dispatch_standalone_list() │
         │                 │         │  _async_dispatch_standalone_ │
         │                 │         │    list()                    │
         │                 │         │  _build_normalization_map()  │
         │                 │         │  _extracts_params()          │
         │                 │         │  _info_params()              │
         │                 │         │  _langlinks_params()         │
         │                 │         │  _links_params()             │
         │                 │         │  _backlinks_params()         │
         │                 │         │  _categories_params()        │
         │                 │         │  _categorymembers_params()   │
         │                 │         │  _coordinates_params()       │
         │                 │         │  _images_params()            │
         │                 │         │  _geosearch_params()         │
         │                 │         │  _random_params()            │
         │                 │         │  _search_params()            │
         │                 │         └──────────────┬───────────────┘
         │                 │                        │
         │                 │               ┌────────┴──────────┐
         │                 │               │                   │
         │           ┌─────┴───────┐ ┌─────┴──────┐  ┌────────┴───────┐
         │           │  Wikipedia  │ │  Wikipedia │  │  AsyncWikipedia│
         │           │  Resource   │ │  (concrete)│  │  Resource      │
         │           │             │ │            │  │                │
         │           │  page()     │ │  __init__()│  │  _make_page()  │
         │           │  article()  │ └─────┬──────┘  │  page()        │
         │           │  extracts() │       │          │  article()     │
         │           │  info()     │       │(MRO)     │  extracts()    │
         │           │  langlinks()│       │          │  info()        │
         │           │  links()    │       │          │  langlinks()   │
         │           │  backlinks()│       │          │  links()       │
         │           │  categories()       │          │  backlinks()   │
         │           │  category   │       │          │  categories()  │
         │           │    members()│       │          │  category      │
         │           │  coordinates()      │          │    members()   │
         │           │  images()   │       │          │  coordinates() │
         │           │  geosearch()│       │          │  images()      │
         │           │  random()   │       │          │  geosearch()   │
         │           │  search()   │       │          │  random()      │
         │           │  batch_     │       │          │  search()      │
         │           │   coordinates()     │          │  batch_        │
         │           │  batch_     │       │          │   coordinates()│
         │           │   images()  │       │          │  batch_images()│
         │           └─────┬───────┘       │          │                │
         │                 │               │          └────────┬───────┘
         └─────────────────┘               │                   │
                           └───────────────┘     ┌─────────────┴──────┐
                                                  │  AsyncWikipedia    │
                                                  │  (concrete)        │
                                                  │  __init__()        │
                                                  └────────────────────┘

    Page objects (share a common base; hold back-reference to their wiki instance):

    ┌──────────────────────────────────────────────────────────────┐
    │                    BaseWikipediaPage                         │
    │                                                              │
    │  ATTRIBUTES_MAPPING (class var)                              │
    │  __init__(wiki, title, ns, language, variant, url)           │
    │  language, variant, title, ns  (properties, no fetch)        │
    │  sections_by_title(title) → list   (reads cache)             │
    │  section_by_title(title)  → opt    (delegates to above)      │
    └──────────────────┬───────────────────────────┬───────────────┘
                       │                           │
          ┌────────────┴────────────┐  ┌───────────┴──────────────┐
          │     WikipediaPage       │  │   AsyncWikipediaPage      │
          │                         │  │                           │
          │  _fetch (def)           │  │  _fetch (async def)       │
          │  _info_attr(name)       │  │  _info_attr(name) (async) │
          │  sections_by_title      │  │  sections (property,      │
          │    (override: auto-     │  │    no auto-fetch)         │
          │    fetches extracts)    │  │  exists() (coroutine)     │
          │  sections (auto-fetch)  │  │  summary (await. prop)    │
          │  exists() (auto-fetch)  │  │  text    (await. prop)    │
          │  summary (property)     │  │  langlinks (await. prop)  │
          │  text    (property)     │  │  links     (await. prop)  │
          │  langlinks (property)   │  │  backlinks (await. prop)  │
          │  links     (property)   │  │  categories (await. prop) │
          │  backlinks (property)   │  │  categorymembers          │
          │  categories (property)  │  │    (awaitable prop)       │
          │  categorymembers (prop) │  │  coordinates (await. prop)│
          │  coordinates (property) │  │  images     (await. prop) │
          │  images    (property)   │  │  geosearch_meta (property)│
          │  geosearch_meta (prop)  │  │  search_meta (property)   │
          │  search_meta (property) │  │  pageid    (await. prop)  │
          │  pageid   (property)    │  │  fullurl   (await. prop)  │
          │  fullurl  (property)    │  │  displaytitle (await.)    │
          │  displaytitle (property)│  │  + 18 more info props     │
          │  + 18 more info props   │  │                           │
          │                         │  │  _wiki ──────────────────►│
          │                         │  │  AsyncWikipedia instance  │
          │  _wiki ─────────────────┼► │                           │
          │  Wikipedia instance     │  └───────────────────────────┘
          └─────────────────────────┘


Transport Layer
---------------

``_http_client/`` package implements the HTTP transport layer with three classes.

BaseHTTPClient
~~~~~~~~~~~~~~

Abstract base in ``base_http_client.py`` that holds shared configuration (language, variant,
user-agent, extract format, retry parameters, extra API params) and
the ``_check_and_correct_params()`` validator.  It does **not** make
HTTP requests directly.

SyncHTTPClient
~~~~~~~~~~~~~~

Provides a blocking ``_get(language, params) -> dict`` method in ``sync_http_client.py`` backed by
``httpxyz.Client``.  Retry logic uses ``tenacity`` with exponential
backoff; ``Retry-After`` headers are honoured for HTTP 429 responses.

AsyncHTTPClient
~~~~~~~~~~~~~~~

Provides an ``async def _get(language, params) -> dict`` coroutine in ``async_http_client.py``
backed by ``httpxyz.AsyncClient``.  Retry logic mirrors
``SyncHTTPClient`` but uses ``tenacity``'s ``AsyncRetrying``.

Both clients construct the endpoint URL as::

    https://{language}.wikipedia.org/w/api.php

Additional utilities:

- ``retry_utils.py`` - Common retry utilities and helpers
- ``retry_after_wait.py`` - Retry-After header handling logic


API Layer
---------

``_resources/`` package implements the API layer with three classes.

BaseWikipediaResource
~~~~~~~~~~~~~~~~~~~~~

Pure mixin in ``base_wikipedia_resource.py`` with no HTTP transport.  Contains:

* **Parameter builders** (``_*_params``) — each returns a ``dict``
  ready to pass to the dispatcher.
* **Response parsers** (``_build_*``) — each accepts a raw API
  response fragment and a ``WikipediaPage``, populates the page
  in-place, and returns the parsed value.
* **Dispatch helpers** — generic methods that call ``self._get``
  (provided by the transport mixin), handle pagination, and delegate
  to a ``_build_*`` method.  See `Dispatch Helpers`_ below.

WikipediaResource
~~~~~~~~~~~~~~~~~

Thin synchronous mixin in ``wikipedia_resource.py``.  Each public API method (``extracts``,
``info``, ``langlinks``, ``links``, ``backlinks``, ``categories``,
``categorymembers``) is a one-liner that delegates to the appropriate
sync dispatch helper::

    def extracts(self, page, **kwargs):
        return self._dispatch_prop(
            page, self._extracts_params(page, **kwargs),
            "", self._build_extracts,
        )

AsyncWikipediaResource
~~~~~~~~~~~~~~~~~~~~~~

Mirror of ``WikipediaResource`` using async dispatch helpers in ``async_wikipedia_resource.py``::

    async def extracts(self, page, **kwargs):
        return await self._async_dispatch_prop(
            page, self._extracts_params(page, **kwargs),
            "", self._build_extracts,
        )

``_make_page`` is overridden to return ``AsyncWikipediaPage`` instead
of ``WikipediaPage`` so that stub pages created during response parsing
are automatically async-capable.


Dispatch Helpers
----------------

Four dispatch patterns cover all current MediaWiki API query shapes.
Each has a sync and an async variant.

+------------------------------+-------------------------------------------+------------------+
| Helper                       | When to use                               | Pagination key   |
+==============================+===========================================+==================+
| ``_dispatch_prop``           | Prop query, result fits in one page.      | (none)           |
|                              | Response: ``raw["query"]["pages"]``       |                  |
+------------------------------+-------------------------------------------+------------------+
| ``_dispatch_prop_paginated`` | Prop query, result may span pages.        | ``raw["continue"]|
|                              | Accumulates ``raw["query"]["pages"]       | [continue_key]`` |
|                              | [page_id][list_key]`` across pages.       |                  |
+------------------------------+-------------------------------------------+------------------+
| ``_dispatch_list``           | List query, result may span pages.        | ``raw["continue"]|
|                              | Accumulates ``raw["query"][list_key]``    | [continue_key]`` |
|                              | across pages.  Requires a page object.    |                  |
+------------------------------+-------------------------------------------+------------------+
| ``_dispatch_standalone_list``| List query that does *not* require a page | ``raw["continue"]|
|                              | object.  Accumulates ``raw["query"]       | [continue_key]`` |
|                              | [list_key]`` and returns the raw response.|                  |
+------------------------------+-------------------------------------------+------------------+

Current mapping:

* ``extracts``, ``info``, ``langlinks``, ``categories``
  → ``_dispatch_prop``
* ``links`` → ``_dispatch_prop_paginated`` (cursor: ``plcontinue``,
  list key: ``links``)
* ``backlinks`` → ``_dispatch_list`` (cursor: ``blcontinue``,
  list key: ``backlinks``)
* ``categorymembers`` → ``_dispatch_list`` (cursor: ``cmcontinue``,
  list key: ``categorymembers``)
* ``coordinates`` → custom per-page dispatch with per-parameter caching
  (cursor: ``cocontinue``, uses ``_dispatch_prop_paginated`` internally)
* ``images`` → custom per-page dispatch with per-parameter caching
  (cursor: ``imcontinue``)
* ``geosearch`` → single ``_get`` call (no pagination)
* ``random`` → single ``_get`` call (no pagination)
* ``search`` → single ``_get`` call (no pagination)

.. warning::

   ``geosearch``, ``random``, and ``search`` deliberately bypass
   ``_dispatch_standalone_list`` and make a **single API request**.
   The caller's ``limit`` parameter already tells the MediaWiki API
   how many results to return.  Using the paginating dispatcher would
   cause an infinite loop for ``random`` (the API always offers more
   random pages) and near-infinite loops for ``search`` and
   ``geosearch`` (broad queries can match thousands of pages).
   Only use ``_dispatch_standalone_list`` for list queries where
   exhaustive fetching is the desired behaviour.


Request Lifecycle
-----------------

Synchronous (property access path)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    user code: page.summary
        │
        ▼
    WikipediaPage.summary  (property, checks _summary cache)
        │
        ▼
    WikipediaPage._fetch_page()
        │
        ▼
    Wikipedia.extracts(page)             ◄─ WikipediaResource
        │
        ▼
    BaseWikipediaResource._dispatch_prop(
        page, params, empty="", builder=_build_extracts)
        │
        ├─► _construct_params(page, params)   → merged dict
        │
        ├─► SyncHTTPClient._get(language, merged_params)
        │       │
        │       ├─► httpxyz.Client.get(url, params=…)
        │       └─► tenacity retry loop (429 / 5xx / timeout)
        │             → raw JSON dict
        │
        └─► _process_prop_response(raw, page, empty, builder)
                │
                └─► _build_extracts(extract, page)
                        │
                        ├─► populate page._summary
                        ├─► populate page._section_mapping
                        └─► return page._summary

Asynchronous (property access path)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    user code: await page.summary
        │
        ▼
    AsyncWikipediaPage.summary  (explicit @property, returns coroutine)
        │
        ▼
    AsyncWikipediaPage._fetch  (async, called inside the coroutine)
        │
        ▼
    AsyncWikipedia.extracts(page)        ◄─ AsyncWikipediaResource
        │
        ▼
    BaseWikipediaResource._async_dispatch_prop(
        page, params, empty="", builder=_build_extracts)
        │
        ├─► _construct_params(page, params)   → merged dict
        │
        ├─► await AsyncHTTPClient._get(language, merged_params)
        │       │
        │       ├─► await httpxyz.AsyncClient.get(url, params=…)
        │       └─► tenacity AsyncRetrying loop
        │             → raw JSON dict
        │
        └─► _process_prop_response(raw, page, empty, builder)
                │
                └─► _build_extracts(extract, page)
                        └─► return page._summary


Adding a New API Call
---------------------

This section walks through a complete example: adding support for the
``templates`` prop, which returns a list of templates used on a page.

MediaWiki reference:
https://www.mediawiki.org/w/api.php?action=help&modules=query%2Btemplates

Step 1 — Choose the Right Dispatcher
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inspect the API response structure:

* **Single-fetch prop** (result in ``raw["query"]["pages"]``, no
  ``continue`` key expected in practice) → ``_dispatch_prop``.
* **Paginated prop** (``continue`` key uses a ``*continue`` cursor,
  data nested under ``raw["query"]["pages"][id][list_key]``) →
  ``_dispatch_prop_paginated``.
* **List query** (``action=query&list=…``, data under
  ``raw["query"][list_key]``) → ``_dispatch_list``.

``templates`` uses ``prop=templates``, may paginate with ``tlcontinue``,
and stores results under ``raw["query"]["pages"][id]["templates"]``.
→ Use ``_dispatch_prop_paginated``.

Step 2 — Add a Return-Type Attribute to BaseWikipediaPage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In ``_base_wikipedia_page.py``, add a cache slot in
``BaseWikipediaPage.__init__``::

    self._templates: dict[str, Any] = {}

Step 3 — Add the Parameter Builder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In ``BaseWikipediaResource`` (``_resources/base_wikipedia_resource.py``), add::

    def _templates_params(self, page: WikipediaPage) -> dict[str, Any]:
        """
        Build params for the ``templates`` prop query.

        Requests up to 500 templates per API response page.  Pagination
        is handled automatically by :meth:`_dispatch_prop_paginated`
        using the ``tlcontinue`` cursor.

        :param page: source page (provides ``title``)
        :return: base params dict; merge kwargs at the call site
        """
        return {
            "action": "query",
            "prop": "templates",
            "titles": page.title,
            "tllimit": 500,
        }

Step 4 — Add the Response Parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In ``BaseWikipediaResource`` (``_resources/base_wikipedia_resource.py``), add::

    def _build_templates(
        self, extract: Any, page: WikipediaPage
    ) -> PagesDict:
        """
        Build the templates map from a ``templates`` API response.

        :param extract: single page entry from ``raw["query"]["pages"]``
        :param page: page object whose ``_templates`` dict is replaced
        :return: ``{title: WikipediaPage}`` mapping
        """
        page._templates = {}
        self._common_attributes(extract, page)
        for tpl in extract.get("templates", []):
            page._templates[tpl["title"]] = self._make_page(
                title=tpl["title"],
                ns=int(tpl["ns"]),
                language=page.language,
                variant=page.variant,
            )
        return page._templates

Step 5 — Add the Sync Method to WikipediaResource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    def templates(
        self, page: WikipediaPage, **kwargs: Any
    ) -> PagesDict:
        """
        Fetch all templates used on a page, keyed by title.

        Follows API pagination automatically (``tlcontinue`` cursor).

        :param page: source page
        :param kwargs: extra API parameters forwarded verbatim
        :return: ``{title: WikipediaPage}``; ``{}`` if page missing
        :raises WikiHttpTimeoutError: if the request times out
        :raises WikiConnectionError: if a connection cannot be established
        :raises WikiRateLimitError: if the API returns HTTP 429
        :raises WikiHttpError: if the API returns a non-success HTTP status
        :raises WikiInvalidJsonError: if the response is not valid JSON
        """
        return self._dispatch_prop_paginated(
            page,
            {**self._templates_params(page), **kwargs},
            "tlcontinue",
            "templates",
            self._build_templates,
        )

Step 6 — Add the Async Method to AsyncWikipediaResource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    async def templates(
        self, page: WikipediaPage, **kwargs: Any
    ) -> PagesDict:
        """
        Async version of :meth:`WikipediaResource.templates`.
        """
        return await self._async_dispatch_prop_paginated(
            page,
            {**self._templates_params(page), **kwargs},
            "tlcontinue",
            "templates",
            self._build_templates,
        )

Step 7 — Add a Lazy Property to WikipediaPage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In ``wikipedia_page.py``::

    @property
    def templates(self) -> PagesDict:
        """Returns templates used on this page."""
        if not self._called["templates"]:
            self._fetch("templates")
        return self._templates

Step 8 — Add a Lazy Coroutine Property to AsyncWikipediaPage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In ``async_wikipedia_page.py``, the ``@property`` returns a coroutine
created by a nested ``async def``; callers do ``await page.templates``::

    @property
    def templates(self) -> Any:
        """Awaitable: returns templates used on this page."""

        async def _get() -> PagesDict:
            if not self._called["templates"]:
                await self._fetch("templates")
            return self._templates

        return _get()

Step 9 — Add Tests
~~~~~~~~~~~~~~~~~~~

Add mock data to ``tests/mock_data.py``::

    "Template:A": {
        "query": {
            "pages": {
                "1": {
                    "pageid": 1,
                    "ns": 0,
                    "title": "Template:A",
                    "templates": [
                        {"ns": 10, "title": "Template:A"},
                    ],
                }
            }
        }
    },

Add a test file ``tests/templates_test.py``::

    import unittest
    from unittest.mock import patch

    import wikipediaapi

    from tests.mock_data import mock_data


    class TestTemplates(unittest.TestCase):
        def setUp(self):
            self.wiki = wikipediaapi.Wikipedia(
                user_agent="test", language="en"
            )

        def _mock_get(self, language, params):
            return mock_data[params["titles"]]

        def test_templates(self):
            with patch.object(self.wiki, "_get", side_effect=self._mock_get):
                page = self.wiki.page("Template:A")
                templates = self.wiki.templates(page)
                self.assertIn("Template:A", templates)


Invariants and Conventions
--------------------------

The following invariants hold throughout the codebase and must be
preserved when adding new functionality.

**Parameter builders (``_*_params``)**

* Always return a plain ``dict[str, Any]``.
* Never call ``_construct_params`` — dispatchers do that.
* Never mutate the page object.
* For props: include ``"action": "query"`` and ``"prop": "<name>"``.
* For lists: include ``"action": "query"`` and ``"list": "<name>"``.

**Response parsers (``_build_*``)**

* Accept ``(extract: Any, page: WikipediaPage)`` as the first two
  positional arguments.
* Reset the relevant cache attribute (``page._links = {}``, etc.)
  before populating it.
* Call ``_common_attributes(extract, page)`` to copy standard fields.
* Always return the populated cache attribute.
* Use ``_make_page()`` to create stub child pages so that the correct
  page type (``WikipediaPage`` vs. ``AsyncWikipediaPage``) is
  produced automatically.

**Dispatch helpers**

* ``_dispatch_prop`` / ``_async_dispatch_prop`` — for props where
  the full result fits in one API response.
* ``_dispatch_prop_paginated`` / ``_async_dispatch_prop_paginated`` —
  for props that may paginate.  The *params* dict is mutated in-place
  to add the continuation key on each subsequent request.
* ``_dispatch_list`` / ``_async_dispatch_list`` — for ``list=``
  queries that may paginate.  Requires a page object for language context.
* ``_dispatch_standalone_list`` / ``_async_dispatch_standalone_list`` —
  for ``list=`` queries that are **not** tied to a specific page (e.g.
  ``geosearch``, ``random``, ``search``).  These accept a ``language``
  string instead of a page object and return the raw merged response.

**Public API methods**

* Sync methods in ``WikipediaResource`` must never use ``await``.
* Async methods in ``AsyncWikipediaResource`` must always be defined
  with ``async def`` and use ``await``.
* Both sync and async methods must share the same ``_*_params`` and
  ``_build_*`` implementations without duplication.
* All raises must be documented in the docstring.

**Typed data (``_types/`` package)**

* ``coordinate.py`` — ``Coordinate`` frozen ``@dataclass`` value objects
* ``geo_point.py`` — ``GeoPoint`` frozen ``@dataclass`` value objects
* ``geo_box.py`` — ``GeoBox`` frozen ``@dataclass`` value objects
* ``geo_search_meta.py`` — ``GeoSearchMeta`` frozen ``@dataclass`` value objects
* ``search_meta.py`` — ``SearchMeta`` frozen ``@dataclass`` value objects
* ``search_results.py`` — ``SearchResults`` wrapper around ``PagesDict``

**Parameter dataclasses (``_params/`` package)**

Each query submodule has a frozen ``@dataclass`` (e.g.
``CoordinatesParams``, ``ImagesParams``) that maps clean Python
names to MediaWiki API parameter names with a configurable prefix.
* Pipe-separated MediaWiki parameters (for example ``prop``, ``info``,
  and ``images``) are exposed as iterable-only inputs in the Python API.
  They are normalized to ``"|"``-joined strings in ``__post_init__``
  before API serialization.
* The ``to_api()`` method returns the ``dict[str, str]`` ready for the
  API call; ``cache_key()`` returns a hashable tuple for per-parameter
  caching.

**Enums (``_enums/`` package)**

Strongly-typed enums for API parameters:
* ``coordinate_type.py`` — ``CoordinateType`` enum for coordinate filtering
* ``coordinates_prop.py`` — ``CoordinatesProp`` enum for coordinate properties
* ``direction.py`` — ``Direction`` enum for sort direction
* ``geosearch_sort.py`` — ``GeoSearchSort`` enum for geographic search sorting
* ``globe.py`` — ``Globe`` enum for celestial bodies
* ``namespace.py`` — ``Namespace`` enum for MediaWiki namespaces
* ``redirect_filter.py`` — ``RedirectFilter`` enum for redirect filtering
* ``search_info.py`` — ``SearchInfo`` enum for search metadata
* ``search_prop.py`` — ``SearchProp`` enum for search properties
* ``search_qi_profile.py`` — ``SearchQiProfile`` enum for query-independent ranking
* ``search_sort.py`` — ``SearchSort`` enum for search sorting
* ``search_what.py`` — ``SearchWhat`` enum for search type

**Exceptions (``exceptions/`` package)**

* ``wikipedia_exception.py`` — ``WikipediaException`` base exception
* ``wiki_connection_error.py`` — ``WikiConnectionError`` for connection failures
* ``wiki_http_error.py`` — ``WikiHttpError`` for HTTP errors
* ``wiki_http_timeout_error.py`` — ``WikiHttpTimeoutError`` for timeouts
* ``wiki_invalid_json_error.py`` — ``WikiInvalidJsonError`` for JSON parsing errors
* ``wiki_rate_limit_error.py`` — ``WikiRateLimitError`` for rate limiting

**Per-parameter caching**

* ``coordinates`` and ``images`` support different parameter sets per
  page.  Results are cached in ``page._param_cache[name][cache_key]``
  via ``_get_cached`` / ``_set_cached`` on ``BaseWikipediaPage``.
* The ``NOT_CACHED`` sentinel (a singleton ``_Sentinel`` instance)
  distinguishes "never fetched" from "fetched, result is ``None``".
* Page-level properties (``page.coordinates``, ``page.images``) use
  default parameters; calling ``wiki.coordinates(page, primary="all")``
  caches under a separate key.

**Batch methods**

* ``batch_coordinates(pages)`` and ``batch_images(pages)`` send
  multi-title API requests (up to 50 titles per request) and
  distribute results to each page's per-parameter cache.
* ``PagesDict.coordinates()`` and ``PagesDict.images()`` are
  convenience methods that delegate to the batch methods on the wiki
  client.
* Batch methods use ``_build_normalization_map(raw)`` to handle
  MediaWiki title normalization (e.g. ``Test_1`` → ``Test 1``).

**Page objects**

* A page is created lazily via ``wiki.page(title)`` — no network call
  at construction time.
* Properties cache their result in a ``_<name>`` attribute; the first
  access triggers the API call, subsequent accesses return the cached
  value.
* ``WikipediaPage._fetch(call)`` calls ``getattr(self.wiki, call)(self)``
  and marks ``_called[call] = True``; the matching async version
  ``AsyncWikipediaPage._fetch(call)`` does the same with ``await``.
* ``geosearch_meta`` and ``search_meta`` are plain ``@property`` in both
  sync and async — they are set by ``geosearch()`` / ``search()`` on
  the wiki client and require no network call on the page itself.


Command Line Interface
---------------------

The CLI provides a command-line tool for querying Wikipedia using Wikipedia-API.
It is organized into a modular structure for better maintainability.

**Architecture**

The CLI is split into a main entry point and functional command modules::

    wikipediaapi/
    ├── cli.py                     # Main CLI entry point (54 lines)
    └── commands/                  # CLI command modules
        ├── __init__.py
        ├── base.py               # Shared utilities and common options
        ├── page_commands.py      # Page content commands
        ├── link_commands.py      # Link-related commands
        ├── category_commands.py  # Category commands
        ├── geo_commands.py       # Geographic commands
        └── search_commands.py    # Search and discovery commands

**Main Entry Point (``cli.py``)**

* Sets up the Click command group with version and help options
* Imports and registers all command modules
* Provides the ``main()`` function for the console script entry point
* Reduced from 1481 lines to 54 lines for better maintainability

**Base Module (``commands/base.py``)**

* Contains shared utilities: TypedDict classes, enum validators, formatters
* Defines common Click options used across all commands
* Provides helper functions for Wikipedia instance creation and page fetching
* Centralizes formatting functions for consistent output

**Command Modules**

Each command module groups related functionality:

* ``page_commands.py`` — ``summary``, ``text``, ``sections``, ``section``, ``page``
* ``link_commands.py`` — ``links``, ``backlinks``, ``langlinks``
* ``category_commands.py`` — ``categories``, ``categorymembers``
* ``geo_commands.py`` — ``coordinates``, ``images``, ``geosearch``
* ``search_commands.py`` — ``search``, ``random``

**Command Pattern**

Each command module follows this pattern:

1. **Business logic functions** — Pure functions that handle Wikipedia API calls
2. **Formatting functions** — Convert results to text/JSON output
3. **Click command decorators** — Define CLI interface with options and arguments
4. **Register function** — Registers commands with the main CLI group

**Benefits of Modular Structure**

* **Maintainable file sizes** — Each module 150-430 lines vs one 1481-line file
* **Logical organization** — Related commands grouped together
* **Easier development** — Changes to specific functionality isolated to relevant module
* **Better testing** — Command modules can be tested independently
* **Perfect backward compatibility** — All CLI commands work identically to before

**Usage Examples**

The CLI supports all original commands with identical interfaces::

    wikipedia-api summary "Python (programming language)"
    wikipedia-api links "Python (programming language)" --language cs
    wikipedia-api categories "Python (programming language)" --json
    wikipedia-api coordinates "Mount Everest"
    wikipedia-api geosearch --coord "51.5074|-0.1278"
    wikipedia-api search "Python programming"

**Adding New Commands**

To add a new CLI command:

1. Choose the appropriate command module based on functionality
2. Add business logic function (following existing patterns)
3. Add formatting function for output
4. Add Click command with proper options and documentation
5. Register the command in the module's ``register_commands()`` function

The modular structure makes it easy to extend the CLI while maintaining clean organization.
