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
entirely decoupled: the API logic never imports ``httpx``, and the
transport layer knows nothing about MediaWiki.


File Layout
-----------

::

    wikipediaapi/
    ├── __init__.py              # Public exports
    ├── _http_client.py          # Transport layer
    │   ├── BaseHTTPClient       # Shared retry & config logic
    │   ├── SyncHTTPClient       # Blocking httpx.Client
    │   └── AsyncHTTPClient      # Non-blocking httpx.AsyncClient
    ├── _resources.py            # API layer
    │   ├── BaseWikipediaResource  # Param builders, parsers, dispatchers
    │   ├── WikipediaResource      # Sync public API methods
    │   └── AsyncWikipediaResource # Async public API methods
    ├── wikipedia.py             # Wikipedia (sync concrete client)
    ├── async_wikipedia.py       # AsyncWikipedia (async concrete client)
    ├── _base_wikipedia_page.py  # BaseWikipediaPage (shared page state & methods)
    ├── wikipedia_page.py        # WikipediaPage (lazy sync page object)
    ├── async_wikipedia_page.py  # AsyncWikipediaPage (lazy async page object)
    ├── wikipedia_page_section.py  # WikipediaPageSection
    ├── extract_format.py        # ExtractFormat enum (WIKI / HTML)
    └── namespace.py             # Namespace / WikiNamespace


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

* ``__getattr__`` — sync returns values directly; async returns coroutines.
* ``_fetch`` — ``def`` in sync, ``async def`` in async.
* ``sections`` property — sync auto-fetches; async requires an explicit
  ``await page.summary()`` first.
* ``exists()`` — sync auto-fetches via ``self.pageid``; async is a
  coroutine method that lazily fetches ``pageid`` via ``info``.
* All data-fetching surface (``summary``, ``langlinks``, …) — sync uses
  ``@property``; async uses awaitable property via ``__getattr__``
  (``COROUTINE_PROPERTIES`` dispatch).
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
         │                 │         │  _extracts_params()          │
         │                 │         │  _info_params()              │
         │                 │         │  _langlinks_params()         │
         │                 │         │  _links_params()             │
         │                 │         │  _backlinks_params()         │
         │                 │         │  _categories_params()        │
         │                 │         │  _categorymembers_params()   │
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
         │           └─────┬───────┘       │          │    members()   │
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
          │  categorymembers (prop) │  │  pageid    (await. prop)  │
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

``_http_client.py`` implements three classes.

BaseHTTPClient
~~~~~~~~~~~~~~

Abstract base that holds shared configuration (language, variant,
user-agent, extract format, retry parameters, extra API params) and
the ``_check_and_correct_params()`` validator.  It does **not** make
HTTP requests directly.

SyncHTTPClient
~~~~~~~~~~~~~~

Provides a blocking ``_get(language, params) -> dict`` method backed by
``httpx.Client``.  Retry logic uses ``tenacity`` with exponential
backoff; ``Retry-After`` headers are honoured for HTTP 429 responses.

AsyncHTTPClient
~~~~~~~~~~~~~~~

Provides an ``async def _get(language, params) -> dict`` coroutine
backed by ``httpx.AsyncClient``.  Retry logic mirrors
``SyncHTTPClient`` but uses ``tenacity``'s ``AsyncRetrying``.

Both clients construct the endpoint URL as::

    https://{language}.wikipedia.org/w/api.php


API Layer
---------

``_resources.py`` implements three classes.

BaseWikipediaResource
~~~~~~~~~~~~~~~~~~~~~

Pure mixin with no HTTP transport.  Contains:

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

Thin synchronous mixin.  Each public API method (``extracts``,
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

Mirror of ``WikipediaResource`` using async dispatch helpers::

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

Three dispatch patterns cover all current MediaWiki API query shapes.
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
|                              | across pages.                             |                  |
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
        │       ├─► httpx.Client.get(url, params=…)
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
    AsyncWikipediaPage.__getattr__("summary")  (COROUTINE_PROPERTIES dispatch)
        │
        ▼
    AsyncWikipediaPage._fetch_page()
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
        │       ├─► await httpx.AsyncClient.get(url, params=…)
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

In ``BaseWikipediaResource`` (``_resources.py``), add::

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

In ``BaseWikipediaResource``, add::

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
        if self._templates is None:
            self._wiki.templates(self)
        return self._templates  # type: ignore[return-value]

Step 8 — Add a Lazy Coroutine Property to AsyncWikipediaPage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In ``async_wikipedia_page.py``::

    @property
    async def templates(self) -> PagesDict:
        """Returns templates used on this page."""
        if self._templates is None:
            await self._wiki.templates(self)
        return self._templates  # type: ignore[return-value]

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
  queries that may paginate.

**Public API methods**

* Sync methods in ``WikipediaResource`` must never use ``await``.
* Async methods in ``AsyncWikipediaResource`` must always be defined
  with ``async def`` and use ``await``.
* Both sync and async methods must share the same ``_*_params`` and
  ``_build_*`` implementations without duplication.
* All raises must be documented in the docstring.

**Page objects**

* A page is created lazily via ``wiki.page(title)`` — no network call
  at construction time.
* Properties cache their result in a ``_<name>`` attribute; the first
  access triggers the API call, subsequent accesses return the cached
  value.
* ``WikipediaPage._fetch_page()`` calls ``self._wiki.info(self)`` and
  ``self._wiki.extracts(self)`` to initialise standard attributes.
