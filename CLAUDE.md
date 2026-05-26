# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wikipedia-API is a Python wrapper for the MediaWiki API. It provides both synchronous (`Wikipedia`) and asynchronous (`AsyncWikipedia`) clients. Published on PyPI as `wikipedia-api`. Requires Python 3.10+.

## Commands

```bash
# Install all dependencies (uses uv package manager)
make requirements-all

# Run all tests (unit + CLI verification)
make run-tests

# Run only unit tests
make run-tests-unit

# Run a single test file / class / method
uv run pytest tests/wikipedia_test.py
uv run pytest tests/wikipedia_test.py::TestWikipedia
uv run pytest tests/wikipedia_test.py::TestWikipedia::test_method

# Run tests with coverage (must stay above 90%)
make run-coverage

# Run all pre-commit hooks
make run-pre-commit

# Type checking only
make run-type-check

# Linting and formatting check (ruff)
make run-ruff

# CLI snapshot tests
make run-test-cli-verify    # verify against recorded snapshots
make run-test-cli-record    # re-record snapshots after intentional CLI changes

# Validate ATTRIBUTES_MAPPING is in sync with page properties
make run-validate-attributes-mappping

# Full pre-release validation
make pre-release-check

# Build package
make build-package
```

## Architecture

The codebase separates two concerns via mixins and multiple inheritance:

1. **HTTP Transport** (`wikipediaapi/_http_client/`) - sync/async HTTP with retry logic via tenacity + httpx
2. **API Logic** (`wikipediaapi/_resources/`) - MediaWiki parameter building and response parsing

Concrete clients compose one of each:
```
Wikipedia(WikipediaResource, SyncHTTPClient)
AsyncWikipedia(AsyncWikipediaResource, AsyncHTTPClient)
```

### Key layers

- `_http_client/` - `BaseHTTPClient` (shared config/retry) -> `SyncHTTPClient` / `AsyncHTTPClient`
- `_resources/` - `BaseWikipediaResource` (param builders `_*_params`, response parsers `_build_*`, dispatch helpers) -> `WikipediaResource` / `AsyncWikipediaResource`
- `_wikipedia/` - `Wikipedia` (sync concrete client) / `AsyncWikipedia` (async concrete client)
- `_page/` - `BaseWikipediaPage` -> `WikipediaPage` (sync, lazy properties) / `AsyncWikipediaPage` (awaitable properties) / `WikipediaPageSection`
- `_image/` - `BaseWikipediaImage` -> `WikipediaImage` (sync) / `AsyncWikipediaImage` (async)
- `_types/` - Frozen dataclasses (Coordinate, GeoPoint, SearchResults, etc.)
- `_params/` - Query parameter dataclasses with `to_api()` and `cache_key()` methods
- `_enums/` - Strongly-typed enums for API parameters (Namespace, SearchSort, etc.)
- `exceptions/` - Exception hierarchy (WikiConnectionError, WikiHttpError, WikiRateLimitError, etc.)
- `cli.py` - Click-based CLI tool

### Dispatch helpers

Four patterns in `BaseWikipediaResource`, each with sync and async variants:
- `_dispatch_prop` - single-page prop query (extracts, info, langlinks, categories)
- `_dispatch_prop_paginated` - paginated prop query (links, coordinates, images)
- `_dispatch_list` - paginated list query requiring a page (backlinks, categorymembers)
- `_dispatch_standalone_list` - paginated list query without a page

**Warning**: `geosearch`, `random`, and `search` deliberately use a single `_get` call (not `_dispatch_standalone_list`) to avoid infinite loops.

### Page lazy loading

Pages created via `wiki.page(title)` make no network call at construction. Properties (summary, text, links, etc.) fetch on first access and cache the result. `ATTRIBUTES_MAPPING` in `_page/_base_wikipedia_page.py` maps property names to API calls.

`coordinates` and `images` use per-parameter caching via `page._param_cache[name][cache_key]` with a `NOT_CACHED` sentinel.

## Critical Invariants

### Sync/async symmetry is mandatory

Every public attribute/method on `WikipediaPage` must have a matching interface on `AsyncWikipediaPage`:
- Sync `@property` -> Async `@property` returning a coroutine (`await page.foo`)
- Sync method -> Async coroutine method
- Non-fetching `@property` -> Same in both

Both sync and async methods share the same `_*_params` and `_build_*` implementations.

### After every change checklist

1. Update `API.rst` and `DESIGN.rst` if architecture/API changed
2. Update `index.rst` and `README.rst` (must stay in sync) if user-facing behavior changed
3. Update `example_sync.py` and `example_async.py`
4. Update CLI (`cli.py`, `tests/cli/test_cli.sh`, `tests/cli_test.py`, `CLI.rst`)
5. Update `tests/test_sync_async_symmetry.py` property lists for new page attributes
6. Run `make run-validate-attributes-mappping` for page property changes
7. Run `make run-pre-commit` and `make run-coverage`
8. Add a bullet to the `Unreleased` section in `CHANGES.rst` describing the change and linking the PR

### Testing rules

- All HTTP tests must use `tests/mock_data.py` - never make real HTTP requests in unit tests
- Test files follow `*_test.py` naming pattern
- `asyncio_mode = "auto"` is configured for pytest-asyncio
- Code coverage must stay above 90% (core modules 95%+)

### Code style

- Max line length: 100 characters (enforced by ruff)
- Explicit type annotations preferred; minimize use of `Any`
- Use `uv run` to execute scripts (not `.venv/bin/python`)

## Adding a New API Call

Follow the step-by-step guide in `DESIGN.rst` ("Adding a New API Call" section). The process:

1. Choose the right dispatcher based on response structure
2. Add cache slot to `BaseWikipediaPage.__init__`
3. Add `_*_params` method to `BaseWikipediaResource`
4. Add `_build_*` response parser to `BaseWikipediaResource`
5. Add sync method to `WikipediaResource`
6. Add async method to `AsyncWikipediaResource`
7. Add lazy `@property` to `WikipediaPage`
8. Add awaitable `@property` to `AsyncWikipediaPage`
9. Add tests with mock data

## Adding a New Submodule

Follow the step-by-step guide in `ADDING_SUBMODULES.md`.
