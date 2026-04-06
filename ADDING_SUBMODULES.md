# How to Add a New MediaWiki Query Submodule

A step-by-step guide for adding support for a new MediaWiki
`action=query` submodule to the Wikipedia-API library.

This guide uses two real examples that are already implemented:

- **`coordinates`** — a **`prop=`** submodule (per-page data, fetched with a page title)
- **`search`** — a **`list=`** submodule (standalone query, not tied to a specific page)

Read `DESIGN.rst` and `API.rst` before starting.

---

## Table of Contents

1. [Understand the Two Submodule Types](#1-understand-the-two-submodule-types)
2. [Step 1: Define Typed Data Classes](#step-1-define-typed-data-classes-_typespy)
3. [Step 2: Define Parameter Dataclass](#step-2-define-parameter-dataclass-_paramspy)
4. [Step 3: Add API Parameter Builder](#step-3-add-api-parameter-builder-_resourcespy--basewikipediaresource)
5. [Step 4: Add Response Parser](#step-4-add-response-parser-_resourcespy--basewikipediaresource)
6. [Step 5: Add Sync Public Method](#step-5-add-sync-public-method-_resourcespy--wikipediaresource)
7. [Step 6: Add Async Public Method](#step-6-add-async-public-method-_resourcespy--asyncwikipediaresource)
8. [Step 7: Add Page Properties](#step-7-add-page-properties)
9. [Step 8: Update Page Init](#step-8-update-page-init-_base_wikipedia_pagepy)
10. [Step 9: Export from \_\_init\_\_.py](#step-9-export-from-__init__py)
11. [Step 10: Add Mock Data](#step-10-add-mock-data-testsmock_datapy)
12. [Step 11: Add Tests](#step-11-add-tests)
13. [Step 12: Update Documentation](#step-12-update-documentation)
14. [Step 13: Run Quality Checks](#step-13-run-quality-checks)

---

## 1. Understand the Two Submodule Types

MediaWiki `action=query` has two families of submodules:

| Type        | API shape                                             | Example                         | Dispatch helper                                   |
| ----------- | ----------------------------------------------------- | ------------------------------- | ------------------------------------------------- |
| **`prop=`** | Requires `titles=`, result in `raw["query"]["pages"]` | `coordinates`, `images`         | `_dispatch_prop` or manual `_get` + iterate pages |
| **`list=`** | No `titles=`, result in `raw["query"][list_key]`      | `geosearch`, `random`, `search` | single `_get` call (see warning below)            |

Choose the right type first — it determines which dispatch helper to use and
whether your public method takes a `page` parameter.

---

## Step 1: Define Typed Data Classes (`_types.py`)

If your submodule returns structured data beyond just page titles, create a
frozen dataclass to hold it.

### Example A: `Coordinate` (for `prop=coordinates`)

```python
# wikipediaapi/_types.py

@dataclass(frozen=True)
class Coordinate:
    """A single geographic coordinate associated with a Wikipedia page."""
    lat: float
    lon: float
    primary: bool
    globe: str = "earth"
    type: str | None = None
    name: str | None = None
    dim: int | None = None
    country: str | None = None
    region: str | None = None
    dist: float | None = None
```

### Example B: `SearchMeta` + `SearchResults` (for `list=search`)

```python
# wikipediaapi/_types.py

@dataclass(frozen=True)
class SearchMeta:
    """Metadata attached to each page returned by search()."""
    snippet: str = ""
    size: int = 0
    wordcount: int = 0
    timestamp: str = ""


@dataclass
class SearchResults:
    """Wrapper returned by search() combining pages with aggregate info."""
    pages: PagesDict
    totalhits: int = 0
    suggestion: str | None = None
```

**Rules:**

- Use `frozen=True` for value objects (immutable).
- Use plain `@dataclass` for wrappers that hold mutable containers like `PagesDict`.
- Map field names from the JSON keys the MediaWiki API returns.
- Provide sensible defaults for optional fields.

---

## Step 2: Define Parameter Dataclass (`_params.py`)

Each submodule has its own set of API parameters with a module-specific prefix
(e.g. `co` for coordinates, `sr` for search). Create a frozen dataclass that
maps clean Python names to prefixed MediaWiki names.

### Example A: `CoordinatesParams` (prefix `co`)

```python
# wikipediaapi/_params.py

@dataclass(frozen=True)
class CoordinatesParams(_BaseParams):
    """Parameters for prop=coordinates (prefix co)."""
    limit: int = 10
    primary: str = "primary"
    prop: str = "globe"
    distance_from_point: str | None = None
    distance_from_page: str | None = None

    PREFIX: ClassVar[str] = "co"
    FIELD_MAP: ClassVar[dict[str, str]] = {
        "limit": "limit",             # → colimit
        "primary": "primary",         # → coprimary
        "prop": "prop",               # → coprop
        "distance_from_point": "distancefrompoint",  # → codistancefrompoint
        "distance_from_page": "distancefrompage",    # → codistancefrompage
    }
```

### Example B: `SearchParams` (prefix `sr`)

```python
@dataclass(frozen=True)
class SearchParams(_BaseParams):
    """Parameters for list=search (prefix sr)."""
    query: str = ""
    namespace: int = 0
    limit: int = 10
    sort: str = "relevance"
    # ... more fields as needed

    PREFIX: ClassVar[str] = "sr"
    FIELD_MAP: ClassVar[dict[str, str]] = {
        "query": "search",      # → srsearch (note: API param name differs!)
        "namespace": "namespace",  # → srnamespace
        "limit": "limit",         # → srlimit
        "sort": "sort",           # → srsort
    }
```

**How it works:**

- `_BaseParams` provides `to_api()` which iterates `FIELD_MAP` and produces
  `{PREFIX + suffix: str(value)}` for every non-None field.
- `_BaseParams` provides `cache_key()` which returns a hashable tuple of all
  field values, used by the per-parameter cache on page objects.

**How to find the prefix:** Check the MediaWiki API help page for your module.
The prefix is shown in the module header — e.g. `prop=coordinates (co)` means
prefix `co`. Every parameter starts with that prefix:
`colimit`, `coprimary`, `coprop`, etc.

---

## Step 3: Add API Parameter Builder (`_resources.py` → `BaseWikipediaResource`)

Add a method that builds the raw API params dict. This is shared by both sync
and async code paths.

### Example A: `prop=` submodule (coordinates)

```python
# In BaseWikipediaResource class

def _coordinates_api_params(
    self,
    page: "BaseWikipediaPage[Any]",
    params: CoordinatesParams,
) -> dict[str, Any]:
    """Build API params for prop=coordinates."""
    api_params: dict[str, Any] = {
        "action": "query",
        "prop": "coordinates",      # ← the submodule name
        "titles": page.title,       # ← prop= submodules need a page title
    }
    api_params.update(params.to_api())  # ← merge prefixed params
    return api_params
```

### Example B: `list=` submodule (search)

```python
def _search_api_params(self, params: SearchParams) -> dict[str, Any]:
    """Build API params for list=search."""
    api_params: dict[str, Any] = {
        "action": "query",
        "list": "search",          # ← standalone list, no page title
    }
    api_params.update(params.to_api())
    return api_params
```

**Key difference:** `prop=` builders take a `page` parameter and include
`"titles": page.title`. `list=` builders do not.

---

## Step 4: Add Response Parser (`_resources.py` → `BaseWikipediaResource`)

Parse the raw JSON response into your typed data classes. This is also shared
by sync and async.

### Example A: `prop=` parser (coordinates) — per-page

For `prop=` modules, the parser processes a single page entry from
`raw["query"]["pages"]`:

```python
def _build_coordinates_for_page(
    self,
    extract: dict[str, Any],       # single page entry
    page: "BaseWikipediaPage[Any]",
    params: CoordinatesParams,
) -> list[Coordinate]:
    """Parse coordinates from a single page API response entry."""
    self._common_attributes(extract, page)  # always call this first
    coords: list[Coordinate] = []
    for raw_coord in extract.get("coordinates", []):
        coords.append(
            Coordinate(
                lat=float(raw_coord["lat"]),
                lon=float(raw_coord["lon"]),
                primary=raw_coord.get("primary", "") == "",
                globe=raw_coord.get("globe", "earth"),
                # ... more fields
            )
        )
    # Store in per-parameter cache
    page._set_cached("coordinates", params.cache_key(), coords)
    return coords
```

### Example B: `list=` parser (search) — standalone

For `list=` modules, the parser processes the entire `raw` response:

```python
def _build_search_results(self, raw: dict[str, Any]) -> SearchResults:
    """Parse search list results into a SearchResults wrapper."""
    pages = PagesDict(wiki=self)
    raw_query = raw.get("query", {})

    for entry in raw_query.get("search", []):
        p = self._make_page(          # ← creates correct page type
            title=entry["title"],
            ns=int(entry.get("ns", 0)),
            language=self.language,
            variant=self.variant,
        )
        p._attributes["pageid"] = entry.get("pageid", -1)

        # Attach per-result metadata
        p._search_meta = SearchMeta(
            snippet=entry.get("snippet", ""),
            size=int(entry.get("size", 0)),
            wordcount=int(entry.get("wordcount", 0)),
            timestamp=entry.get("timestamp", ""),
        )
        pages[entry["title"]] = p

    # Extract aggregate info
    searchinfo = raw_query.get("searchinfo", {})
    return SearchResults(
        pages=pages,
        totalhits=int(searchinfo.get("totalhits", 0)),
        suggestion=searchinfo.get("suggestion"),
    )
```

**Important patterns:**

- Always use `self._make_page()` to create child pages — this ensures the
  correct type (`WikipediaPage` vs `AsyncWikipediaPage`) is created based on
  whether we're in sync or async context.
- Always call `self._common_attributes(extract, page)` for `prop=` parsers.
- For `list=` parsers, pre-set `_attributes["pageid"]` from the response.

---

## Step 5: Add Sync Public Method (`_resources.py` → `WikipediaResource`)

### Example A: `prop=` method (coordinates)

`prop=` methods take a page, construct params, check cache, call `_get`, and
iterate the response:

```python
def coordinates(
    self,
    page: WikipediaPage,
    *,                              # ← keyword-only after page
    limit: int = 10,
    primary: str = "primary",
    prop: str = "globe",
    distance_from_point: str | None = None,
    distance_from_page: str | None = None,
) -> list[Coordinate]:
    """Fetch geographic coordinates for a page."""
    # 1. Build params object
    params = CoordinatesParams(
        limit=limit, primary=primary, prop=prop,
        distance_from_point=distance_from_point,
        distance_from_page=distance_from_page,
    )

    # 2. Check per-parameter cache
    cached = page._get_cached("coordinates", params.cache_key())
    if not isinstance(cached, type(NOT_CACHED)):
        return cached

    # 3. Build API params and make request
    api_params = self._coordinates_api_params(page, params)
    raw = self._get(page.language, self._construct_params(page, api_params))

    # 4. Iterate response pages and parse
    self._common_attributes(raw.get("query", {}), page)
    for k, v in raw.get("query", {}).get("pages", {}).items():
        if k == "-1":
            page._attributes["pageid"] = -1
            page._set_cached("coordinates", params.cache_key(), [])
            return []
        return self._build_coordinates_for_page(v, page, params)

    page._set_cached("coordinates", params.cache_key(), [])
    return []
```

### Example B: `list=` method (search)

`list=` methods don't take a page — they make a **single `_get` call**:

```python
def search(
    self,
    query: str,
    *,
    namespace: int = 0,
    limit: int = 10,
    sort: str = "relevance",
) -> SearchResults:
    """Search Wikipedia for pages matching a query."""
    # 1. Build params object
    params = SearchParams(query=query, namespace=namespace, limit=limit, sort=sort)

    # 2. Build API params
    api_params = self._search_api_params(params)

    # 3. Single request — the caller's limit controls how many results
    raw = self._get(
        self.language,
        self._construct_params_standalone(api_params),
    )

    # 4. Parse the response
    return self._build_search_results(raw)
```

> **⚠️ WARNING — Do NOT use `_dispatch_standalone_list` for standalone list
> queries.**
>
> `_dispatch_standalone_list` paginates by looping while the API returns a
> `continue` token. This causes **infinite loops** or near-infinite loops
> for standalone list queries:
>
> - **`random`** — the API _always_ returns a `continue` token (there are
>   always more random pages), so the loop never terminates.
> - **`search`** — broad queries match thousands of pages; the loop would
>   make thousands of API calls before exhausting all results.
> - **`geosearch`** — densely populated areas can produce very long
>   continuation chains.
>
> The caller's `limit` parameter already tells the MediaWiki API how many
> results to return in a single response. **Always use a single `_get` /
> `await self._get` call** for these methods.
>
> `_dispatch_standalone_list` exists in the codebase but is currently
> unused. It should only be used if you genuinely need to exhaust _all_
> results from a list query (and even then, add a safeguard).

---

## Step 6: Add Async Public Method (`_resources.py` → `AsyncWikipediaResource`)

The async method mirrors the sync method exactly, but uses `await` and the
`_async_*` dispatch helpers.

### Example A: `prop=` async method (coordinates)

```python
async def coordinates(
    self,
    page: AsyncWikipediaPage,
    *,
    limit: int = 10,
    primary: str = "primary",
    prop: str = "globe",
    distance_from_point: str | None = None,
    distance_from_page: str | None = None,
) -> list[Coordinate]:
    """Async: Fetch geographic coordinates for a page."""
    params = CoordinatesParams(...)
    cached = page._get_cached("coordinates", params.cache_key())
    if not isinstance(cached, type(NOT_CACHED)):
        return cached
    api_params = self._coordinates_api_params(page, params)
    raw = await self._get(...)  # ← await
    # ... same iteration logic as sync
```

### Example B: `list=` async method (search)

```python
async def search(self, query: str, *, ...) -> SearchResults:
    """Async: Search Wikipedia."""
    params = SearchParams(...)
    api_params = self._search_api_params(params)
    # Single request — same as sync, just with await
    raw = await self._get(
        self.language,
        self._construct_params_standalone(api_params),
    )
    return self._build_search_results(raw)
```

**🚨 CRITICAL:** The sync and async methods MUST have identical signatures
(same parameter names, types, defaults, return type). Only the dispatch calls
differ (`self._get(...)` vs `await self._get(...)` ).

---

## Step 7: Add Page Properties

### When to add a page property

Only add page-level properties for `prop=` submodules where it makes sense to
access the data as `page.coordinates` or `page.images`. Standalone `list=`
modules like `search` and `random` don't need page properties — they return
results at the wiki client level.

For `list=` modules that attach metadata to result pages (like `geosearch_meta`
or `search_meta`), add a plain `@property` (no network call) on the page.

### 7a. Sync property (`wikipedia_page.py`)

For a fetching property (like `coordinates`):

```python
@property
def coordinates(self) -> list[Coordinate]:
    """Geographic coordinates for this page."""
    default_params = CoordinatesParams()
    cached = self._get_cached("coordinates", default_params.cache_key())
    if isinstance(cached, type(NOT_CACHED)):
        self.wiki.coordinates(self)     # ← triggers fetch
        cached = self._get_cached("coordinates", default_params.cache_key())
        if isinstance(cached, type(NOT_CACHED)):
            return []
    return cached
```

For a plain metadata property (like `search_meta`):

```python
@property
def search_meta(self) -> SearchMeta | None:
    """Search metadata, or None if page didn't come from search()."""
    return self._search_meta
```

### 7b. Async property (`async_wikipedia_page.py`)

For a fetching property — **returns a coroutine** so callers use
`await page.coordinates`:

```python
@property
def coordinates(self) -> Any:
    """Awaitable: geographic coordinates for this page."""

    async def _get() -> list[Coordinate]:
        default_params = CoordinatesParams()
        cached = self._get_cached("coordinates", default_params.cache_key())
        if isinstance(cached, type(NOT_CACHED)):
            await self.wiki.coordinates(self)   # ← await
            cached = self._get_cached("coordinates", default_params.cache_key())
            if isinstance(cached, type(NOT_CACHED)):
                return []
        return cached

    return _get()  # ← returns the coroutine, not the result
```

For a plain metadata property — **identical in both sync and async** (no await):

```python
@property
def search_meta(self) -> SearchMeta | None:
    """Search metadata, or None."""
    return self._search_meta
```

### Sync/Async Symmetry Rules

| Sync (`WikipediaPage`)                   | Async (`AsyncWikipediaPage`)                            |
| ---------------------------------------- | ------------------------------------------------------- |
| `@property` that fetches → returns value | `@property` that returns a coroutine → `await page.foo` |
| `@property` no fetch → returns value     | `@property` no fetch → returns value (identical)        |

---

## Step 8: Update Page Init (`_base_wikipedia_page.py`)

Add cache slots for your new data:

```python
# In BaseWikipediaPage.__init__():

# For per-parameter cached data (coordinates, images):
# Already handled by _param_cache dict — no new slot needed.

# For metadata attached by list= queries:
self._search_meta: Any = None
self._geosearch_meta: Any = None
```

The `_param_cache` dict (already initialized as `{}`) handles per-parameter
caching for `coordinates` and `images` automatically. You only need to add
explicit `_<name>` attributes for metadata properties like `geosearch_meta`
and `search_meta`.

---

## Step 9: Export from `__init__.py`

Add your new types to the public API:

```python
# wikipediaapi/__init__.py

from ._types import Coordinate
from ._types import SearchMeta
from ._types import SearchResults

__all__ = [
    # ... existing exports ...
    "Coordinate",
    "SearchMeta",
    "SearchResults",
]
```

---

## Step 10: Add Mock Data (`tests/mock_data.py`)

Add mock API responses that match the exact cache key format used by
the test infrastructure. The key format is:

```
{language}:{param1}={value1}&{param2}={value2}&...&
```

Parameters are sorted alphabetically. Trailing `&` is required.

### Example A: `prop=coordinates` mock

```python
# Successful response
"en:action=query&colimit=10&coprimary=primary&coprop=globe&format=json&prop=coordinates&redirects=1&titles=Test_1&": {
    "batchcomplete": "",
    "query": {
        "pages": {
            "4": {
                "pageid": 4,
                "ns": 0,
                "title": "Test 1",
                "coordinates": [
                    {
                        "lat": 51.5074,
                        "lon": -0.1278,
                        "primary": "",      # "" means primary in MW API
                        "globe": "earth",
                    }
                ],
            }
        }
    },
},

# Non-existent page
"en:action=query&colimit=10&coprimary=primary&coprop=globe&format=json&prop=coordinates&redirects=1&titles=NonExistent&": {
    "batchcomplete": "",
    "query": {
        "pages": {
            "-1": {
                "ns": 0,
                "title": "NonExistent",
                "missing": "",
            }
        }
    },
},
```

### Example B: `list=search` mock

```python
"en:action=query&format=json&list=search&redirects=1&srlimit=10&srnamespace=0&srsearch=Python&srsort=relevance&": {
    "batchcomplete": "",
    "query": {
        "searchinfo": {"totalhits": 5432, "suggestion": "python programming"},
        "search": [
            {
                "ns": 0,
                "title": "Python (programming language)",
                "pageid": 300,
                "size": 123456,
                "wordcount": 15000,
                "snippet": "<span>Python</span> is a programming language",
                "timestamp": "2024-01-01T00:00:00Z",
            },
        ],
    },
},
```

### How to find the exact cache key

1. Look at your params dataclass defaults and `to_api()` output.
2. Combine with the base params (`action=query`, `format=json`, `redirects=1`,
   `prop=X` or `list=X`, and `titles=Y` for prop modules).
3. Sort all params alphabetically, join with `&`, add trailing `&`.
4. Prepend `{language}:`.

**Tip:** If unsure, add a `print()` in `mock_data.py`'s `wikipedia_api_request`
to see what key is being looked up at test time.

---

## Step 11: Add Tests

Create a test file `tests/<module>_test.py` or add to
`tests/query_submodules_test.py`.

### Example A: `prop=coordinates` tests

```python
class TestCoordinates(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_coordinates_default(self):
        page = self.wiki.page("Test_1")
        coords = self.wiki.coordinates(page)
        self.assertEqual(len(coords), 1)
        self.assertAlmostEqual(coords[0].lat, 51.5074)
        self.assertTrue(coords[0].primary)

    def test_coordinates_nonexistent_page(self):
        page = self.wiki.page("NonExistent")
        coords = self.wiki.coordinates(page)
        self.assertEqual(coords, [])

    def test_coordinates_cached(self):
        page = self.wiki.page("Test_1")
        coords1 = self.wiki.coordinates(page)
        coords2 = self.wiki.coordinates(page)
        self.assertIs(coords1, coords2)  # same object = cache hit

    def test_page_coordinates_property(self):
        page = self.wiki.page("Test_1")
        coords = page.coordinates
        self.assertEqual(len(coords), 1)
```

### Example B: `list=search` tests

```python
class TestSearch(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._get = wikipedia_api_request(self.wiki)

    def test_search(self):
        results = self.wiki.search("Python")
        self.assertIsInstance(results, wikipediaapi.SearchResults)
        self.assertEqual(len(results.pages), 2)

    def test_search_totalhits(self):
        results = self.wiki.search("Python")
        self.assertEqual(results.totalhits, 5432)

    def test_search_meta(self):
        results = self.wiki.search("Python")
        p = results.pages["Python (programming language)"]
        self.assertIsNotNone(p.search_meta)
        self.assertEqual(p.search_meta.size, 123456)
```

### Always add async tests too

```python
class TestAsyncSearch(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.wiki = wikipediaapi.AsyncWikipedia(user_agent, "en")
        self.wiki._get = async_wikipedia_api_request(self.wiki)

    async def test_async_search(self):
        results = await self.wiki.search("Python")
        self.assertIsInstance(results, wikipediaapi.SearchResults)
        self.assertEqual(len(results.pages), 2)
```

### What to test

- ✅ Default parameters return expected data
- ✅ Custom parameters (e.g. `primary="all"`) return different data
- ✅ Non-existent page returns empty result
- ✅ Cache hit returns same object (`assertIs`)
- ✅ Per-parameter cache separates different param sets
- ✅ Page property triggers fetch and returns correct data
- ✅ Typed data classes have correct fields
- ✅ Frozen dataclasses reject mutation
- ✅ Async versions of all the above

---

## Step 12: Update Documentation

After implementing, update these files:

1. **`API.rst`** — Add method signatures to `Wikipedia` and `AsyncWikipedia`
   sections, add properties to `WikipediaPage` and `AsyncWikipediaPage`
   sections, add new data classes to "Typed Data Classes" section.

2. **`DESIGN.rst`** — Update class diagram, dispatch helpers mapping,
   invariants section.

3. **`examples/example_sync.py`** — Add a usage example section (numbered, with
   comments).

4. **`examples/example_async.py`** — Mirror the sync example with `await`.

5. **`index.rst`** — Add a "How To" section with sync and async code blocks.

6. **`README.rst`** — Should mirror `index.rst`.

---

## Step 13: Run Quality Checks

```bash
# All pre-commit hooks (isort, black, flake8, mypy, pyupgrade)
make run-pre-commit

# Unit tests (414+ tests)
make run-tests

# Coverage (must stay ≥ 90%, target 96%)
make run-coverage
```

Fix any issues and re-run until everything passes.

---

## Quick Reference: Files to Touch

| File                                   | What to add                                                |
| -------------------------------------- | ---------------------------------------------------------- |
| `wikipediaapi/_types.py`               | Frozen dataclass for response data                         |
| `wikipediaapi/_params.py`              | Frozen dataclass for API parameters                        |
| `wikipediaapi/_resources.py`           | `_*_api_params()`, `_build_*()`, sync method, async method |
| `wikipediaapi/_base_wikipedia_page.py` | Cache slots (if needed) in `__init__`                      |
| `wikipediaapi/wikipedia_page.py`       | Sync `@property`                                           |
| `wikipediaapi/async_wikipedia_page.py` | Async `@property` (returns coroutine)                      |
| `wikipediaapi/__init__.py`             | Export new types                                           |
| `tests/mock_data.py`                   | Mock API responses                                         |
| `tests/query_submodules_test.py`       | Sync + async tests                                         |
| `API.rst`                              | Public API reference                                       |
| `DESIGN.rst`                           | Architecture docs                                          |
| `examples/example_sync.py`             | Sync usage example                                         |
| `examples/example_async.py`            | Async usage example                                        |
| `index.rst`                            | User-facing docs                                           |

---

## Common Pitfalls

1. **Wrong cache key in mock data** — The key must exactly match the sorted,
   prefixed params. Add a print statement to debug.

2. **Forgetting async symmetry** — Every sync method needs an identical async
   counterpart. Every sync page property needs an async page property.

3. **Using `_get` instead of `await self._get`** in async methods — Will
   silently return a coroutine object instead of the result.

4. **Not using `_make_page()`** — If you manually construct `WikipediaPage()`
   in a `_build_*` method, async callers will get sync page objects. Always use
   `self._make_page()`.

5. **Title normalization in batch methods** — MediaWiki normalizes titles
   (e.g. `Test_1` → `Test 1`). Use `_build_normalization_map(raw)` and look up
   original titles in the norm map.

6. **Not exporting from `__init__.py`** — Users import from `wikipediaapi`
   directly. If you forget to export, they can't access your types.

7. **Standalone list params missing `redirects=1`** — The
   `_construct_params_standalone()` method adds this automatically, but your
   mock data keys need to include it.
