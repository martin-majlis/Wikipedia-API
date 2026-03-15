# AGENTS.md

Guide for AI agents (and developers) on how to install, build, and test the Wikipedia-API project.

## Before You Start

**📖 CRITICAL: Always read the design and API documentation first**

Before making any changes, read these two documents to understand the
architecture, class hierarchy, and public API:

- **`DESIGN.rst`** — internal architecture, class hierarchy, request
  lifecycle, dispatch helpers, and a step-by-step guide for adding new
  API calls.
- **`API.rst`** — public API reference: every method, property, and
  attribute available on `Wikipedia`, `AsyncWikipedia`, `WikipediaPage`,
  `AsyncWikipediaPage`, `WikipediaPageSection`, and the CLI.

Skipping this step risks duplicating existing logic, violating
established conventions, or breaking the sync/async symmetry.

## Sync / Async Symmetry

**🚨 CRITICAL: The sync and async APIs MUST stay in perfect symmetry.**

`WikipediaPage` and `AsyncWikipediaPage` are parallel classes.
Every public attribute or method on one **must** have the same kind of
interface on the other:

| If `WikipediaPage` has …     | then `AsyncWikipediaPage` MUST have …                                            |
| ---------------------------- | -------------------------------------------------------------------------------- |
| `@property foo`              | awaitable property `await page.foo` (explicit `@property` returning a coroutine) |
| plain method `foo()`         | coroutine method `await page.foo()`                                              |
| plain `@property` (no fetch) | plain `@property` (no fetch)                                                     |

**Never** convert a property to a method (or vice versa) in one class
without making the matching change in the other. Violations break
the documented API contract and confuse callers who switch between
the two clients.

Examples of correct symmetry currently in place:

- `page.summary`, `page.text`, `page.langlinks`, `page.links`,
  `page.backlinks`, `page.categories`, `page.categorymembers` —
  `@property` in sync; explicit `@property` returning a coroutine in async.
- `page.pageid`, `page.fullurl`, `page.displaytitle`, and all other
  info attributes — same pattern: `@property` in sync, awaitable
  `@property` in async.
- `page.exists()` — plain method in sync; coroutine method
  `await page.exists()` in async (both use call syntax `()`).
- `page.sections`, `page.title`, `page.ns`, `page.language`,
  `page.variant` — plain `@property` in both (no awaiting needed).

## Typing Standards

**🧠 Prefer explicit type annotations and minimize `Any`.**

When writing or updating Python code in this repository:

- Use inline type annotations directly on variables, attributes, parameters,
  and return values (e.g. `value: dict[str, int] = {}`), instead of legacy
  `# type:` comments.
- Avoid `Any` whenever a more specific type can be expressed.
- Use `Any` only when it is absolutely necessary (for example, dynamic external
  payloads or framework boundaries where precise typing is not practical).
- If `Any` is required, keep its scope as small as possible and prefer typed
  wrappers/conversions at the boundary.
- Validate typing-related changes by running `make run-pre-commit` before
  submitting.

## Prerequisites

- **Python 3.10+** (supported: 3.10, 3.11, 3.12, 3.13, 3.14)
- **uv** (Python package manager and installer)
- **Make**

## Install

Install all dependencies (runtime, dev, docs, build):

```bash
make requirements-all
```

Or install individual dependency groups:

- **Runtime dependencies:** `make requirements` (installs core dependencies)
- **Dev dependencies:** `make requirements-dev` (installs black, coverage, flake8, isort, mypy, pre-commit, tox, etc.)
- **Doc dependencies:** `make requirements-doc` (installs sphinx)
- **Build dependencies:** `make requirements-build` (installs rst2html, setuptools, wheel)

Note: uv automatically creates and manages a virtual environment in `.venv/`.

## Build

Build the source distribution package:

```bash
make build-package
```

Generate PyPI HTML documentation preview:

```bash
make pypi-html
```

Generate Sphinx HTML documentation:

```bash
make html
```

## Test

### Run Tests

```bash
make run-tests
```

This command runs both the unit tests and the CLI verification tests.

- The unit tests are executed via `python3 -m unittest discover tests/ '*test.py'`. All test files are in the `tests/` directory and follow the `*test.py` naming pattern.
- The CLI verification tests are run using `./tests/cli/test_cli.sh verify`.

### CLI Tests

You can run the CLI tests independently.

- **Verify CLI:** `make run-test-cli-verify`
  - This runs the CLI tests to verify that the output matches the recorded snapshots. It uses `./tests/cli/test_cli.sh verify`.

- **Record CLI Snapshots:** `make run-test-cli-record`
  - This command updates the CLI test snapshots with the current output. Use this when you have intentionally changed the CLI's output. It runs `./tests/cli/test_cli.sh record`.

### Run Tests with Coverage

```bash
make run-coverage
```

Produces a coverage report and `coverage.xml` for the `wikipediaapi` package.

### Code Coverage Requirements

**🎯 CRITICAL: Always maintain code coverage above 90%**

Before submitting any changes, ensure that:

1. **Run coverage check**: `make run-coverage`
2. **Verify coverage**: All modules must have ≥90% coverage
3. **CLI module special attention**: The `wikipediaapi/cli.py` module must maintain ≥90% coverage
4. **If coverage drops**: Add appropriate tests to bring coverage back above 90%
5. **Coverage report**: Check the output for any modules below 90% and address them

Current coverage targets:

- **Overall project**: ≥90%
- **CLI module**: ≥90% (currently 96%)
- **Core modules**: ≥95%

The coverage report will show:

```
Name                                     Stmts   Miss  Cover   Missing
wikipediaapi/cli.py                        289     11    96%   28, 38, 60-61, 367-376, 730
```

If any module shows coverage below 90%, you must:

1. Identify the missing lines in the `Missing` column
2. Write tests to cover the uncovered code paths
3. Re-run coverage until all modules meet the 90% threshold

### Code Quality Requirements

**🔧 CRITICAL: All pre-commit hooks must pass**

Before submitting any changes, ensure that:

1. **Run pre-commit checks**: `make run-pre-commit`
2. **All hooks must pass**: No failures allowed
3. **Fix any issues**: Address linting, formatting, type checking, and other violations
4. **Re-run until clean**: Continue fixing and re-running until all checks pass

The pre-commit hooks include:

- **isort**: Import sorting
- **black**: Code formatting
- **flake8**: Linting (max line length: 100)
- **mypy**: Type checking
- **pyupgrade**: Python syntax upgrades
- **trailing whitespace**: Whitespace cleanup
- **YAML validation**: YAML file checks

Common issues to fix:

- Remove unused imports (F401)
- Fix line length violations (E501: max 100 characters)
- Resolve type checking errors
- Fix undefined variables (F821)
- Avoid lambda assignments (E731)
- Fix redefinition errors (F811)

### Run Tests Across Python Versions (tox)

```bash
make run-tox
```

Runs the test suite against Python 3.10–3.14 via tox.

## Lint & Type Checking

### Run All Pre-commit Hooks

```bash
make run-pre-commit
```

This runs isort, black, flake8, mypy, pyupgrade, and other checks (trailing whitespace, YAML validation, etc.).

### Run Individual Checks

- **Type checking:** `make run-type-check` (runs `mypy ./wikipediaapi`)
- **Linting:** `make run-flake8` (runs `flake8 --max-line-length=100 wikipediaapi tests`)

## After Every Change

**✅ CRITICAL: Keep all documentation, examples, and tests in sync**

After completing any change, go through this checklist before committing:

### 1. Update documentation files

Ensure each of the following files accurately reflects the change:

- **`API.rst`** — add or update entries for any new or modified
  methods, properties, or attributes.
- **`DESIGN.rst`** — update the class hierarchy, file layout, diagrams,
  or step-by-step guide if the architecture changed.
- **`index.rst`** — update usage examples or feature descriptions if
  user-facing behaviour changed (note: `README.rst` is identical in
  content and must be kept in sync with `index.rst`).
- **`README.rst`** — mirror any changes made to `index.rst`.

### 2. Update example files

- **`example_sync.py`** — add or update usage of any new or changed
  synchronous API (`Wikipedia`, `WikipediaPage`).
- **`example_async.py`** — add or update usage of any new or changed
  asynchronous API (`AsyncWikipedia`, `AsyncWikipediaPage`).

Both files serve as living documentation and must exercise every
publicly available method and attribute.

### 3. Update tests

- Add or update unit tests in `tests/` for every new or modified code
  path.
- For synchronous code: `tests/wikipedia_page_test.py` and related
  files.
- For asynchronous code: `tests/async_wikipedia_page_test.py` and
  related files.
- Run the full suite and coverage check (see [Test](#test) below)
  before committing.

## Pre-release Check

Run the full validation suite (pre-commit, type check, flake8, coverage, pypi-html, tox, example):

```bash
make pre-release-check
```

## Project Structure

- `wikipediaapi/` — Main package (single `__init__.py` module)
- `tests/` — Unit tests (`*test.py` files, `mock_data.py` for test fixtures)
- `pyproject.toml` — Package metadata, dependencies, and build configuration
- `Makefile` — All build, test, and release commands
- `tox.ini` — Multi-Python test configuration
- `.pre-commit-config.yaml` — Pre-commit hook definitions
