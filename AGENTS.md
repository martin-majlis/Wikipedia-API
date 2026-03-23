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

## Docstring Standards

**📝 Write descriptive docstrings with consistent structure.**

All functions, methods, classes, and modules must have descriptive docstrings that follow this structure:

### Required Docstring Format

```python
def example_function(param1: str, param2: int) -> bool:
    """One-line summary of the function's purpose.

    Detailed description of the function's behavior, including important
    implementation details, usage patterns, or context.

    Args:
        param1: Description of the first parameter, including expected format
            and constraints.
        param2: Description of the second parameter, including valid ranges
            or special values.

    Returns:
        Description of the return value, including its type and meaning.
        Include possible return values and their significance.

    Raises:
        ExceptionType: Description of when this exception is raised,
            including the conditions that trigger it.
        AnotherException: Description of when this exception occurs.

    Invariants:
        - Any conditions that remain true before and after execution
        - State guarantees that the function maintains
        - Thread safety considerations if applicable
    """
```

### Docstring Requirements

1. **One-line summary**: Must be a complete sentence ending with a period
   that concisely describes what the function does.

2. **Detailed description**: Expand on the summary with implementation details,
   usage examples, or important context.

3. **Parameters section (`Args`)**: Document all parameters with:
   - Parameter name (matching the function signature)
   - Description including expected format, constraints, and valid values
   - Use proper indentation and formatting

4. **Return values section (`Returns`)**: Document the return value with:
   - Type information (if not obvious from type hints)
   - Meaning and significance of different return values
   - Special cases or conditions

5. **Exceptions section (`Raises`)**: Document all exceptions that can be raised:
   - Exception type name
   - Conditions that trigger the exception
   - Any recovery strategies or expected handling

6. **Invariants section (`Invariants`)**: Document any guarantees:
   - Pre/post-conditions that remain true
   - State guarantees and thread safety
   - Side effects and their implications

### Special Cases

- **Properties**: Use the same format but replace `Args` with appropriate sections
- **Methods**: Include `self` parameter documentation if relevant
- **Classes**: Include overall purpose, usage examples, and important attributes
- **Modules**: Describe the module's purpose and main exports

### Examples

```python
def page_exists(self) -> bool:
    """Check if the Wikipedia page exists on the server.

    Performs a lightweight check to determine if the page exists without
    fetching the full page content. This is useful for validation before
    attempting expensive operations.

    Returns:
        True if the page exists and is accessible, False if the page
        does not exist or cannot be accessed.

    Raises:
        requests.exceptions.ConnectionError: If the network connection fails.
        requests.exceptions.Timeout: If the request times out.

    Invariants:
        - Does not modify the page's internal state
        - Safe to call multiple times without side effects
        - Thread-safe for concurrent access
    """
```

All docstrings must be checked during code review and should pass the
pre-commit hooks without warnings.

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
5. **Check project configuration**: Verify line length limits and linter settings in `pyproject.toml` match project requirements

The pre-commit hooks include:

- **isort**: Import sorting
- **black**: Code formatting (max 100 characters per line)
- **flake8**: Linting (max 100 characters per line)
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

**Project Configuration**: Check `pyproject.toml` for:

- `tool.black.line-length = 100` (should match flake8 max)
- `tool.flake8.max-line-length = 100` (should match black limit)
- Linter configurations in `[tool.*]` sections

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

### 3. Update the CLI tool

Whenever the public API of `Wikipedia` or `AsyncWikipedia` changes
(new methods, renamed parameters, changed return types), the
command-line interface and its tests **must** be updated in lockstep:

- **`wikipediaapi/cli.py`** — add or update CLI commands and their
  helper functions to expose the new or changed API functionality.
- **`tests/cli/test_cli.sh`** — add new test entries to the `TESTS`
  array for every new command, then run `make run-test-cli-record` to
  generate the expected output fixtures.
- **`tests/cli_test.py`** — add or update unit tests for the CLI
  helper functions (e.g. `get_*`, `format_*`).
- **`CLI.rst`** — document new commands, options, and examples.

### 4. Update tests

- Add or update unit tests in `tests/` for every new or modified code
  path.
- For synchronous code: `tests/wikipedia_page_test.py` and related
  files.
- For asynchronous code: `tests/async_wikipedia_page_test.py` and
  related files.
- **Keep `tests/test_sync_async_symmetry.py` up to date**: When adding new
  properties or methods to either `WikipediaPage` or `AsyncWikipediaPage`,
  update the `TestSyncAsyncPropertySymmetry` class to include the new
  attributes in the appropriate property lists (`construction_props`,
  `awaitable_props`, `collection_props`, etc.). The test automatically
  discovers all public attributes using `dir()` and will alert you to
  any missing properties that need to be added to the test lists. This ensures sync/async
  symmetry is maintained for all API features.
- Run the full suite and coverage check (see [Test](#test) below)
  before committing.

## Pre-release Check

Run the full validation suite (pre-commit, type check, flake8, coverage, pypi-html, tox, example):

```bash
make pre-release-check
```

## Script Execution and Debugging

**📝 CRITICAL: Always store script output to log files for analysis**

When running scripts, especially for debugging or validation purposes:

1. **Always use `uv run`**: Use `uv run python script.py` instead of `.venv/bin/python script.py`
2. **Always redirect output to a timestamped log file**: Use `2>&1 | tee script_$(date +%Y%m%d_%H%M%S).log` to capture both stdout and stderr
3. **Read and analyze the log file**: Use `read_file` tool to examine the complete output instead of multiple command executions
4. **Avoid repeated command executions**: Don't use multiple `grep`, `head`, `tail` commands on the same script run - read the log once and analyze it
5. **Include timestamps for debugging**: Add timestamps to script output when investigating timing issues
6. **Use structured logging**: Format output in a consistent way for easy parsing

Example:

```bash
# Good practice - single execution, complete capture with timestamp
uv run python script.py 2>&1 | tee script_$(date +%Y%m%d_%H%M%S).log

# Then analyze the complete output
# (use read_file tool to examine the timestamped log file)

# Bad practice - multiple executions
.venv/bin/python script.py | grep "error"
.venv/bin/python script.py | tail -10
.venv/bin/python script.py | head -20
```

This approach ensures consistent analysis and avoids wasting time with repeated command executions.

## Project Structure

- `wikipediaapi/` — Main package (single `__init__.py` module)
- `tests/` — Unit tests (`*test.py` files, `mock_data.py` for test fixtures)
- `pyproject.toml` — Package metadata, dependencies, and build configuration
- `Makefile` — All build, test, and release commands
- `tox.ini` — Multi-Python test configuration
- `.pre-commit-config.yaml` — Pre-commit hook definitions
