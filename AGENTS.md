# AGENTS.md

Guide for AI agents (and developers) on how to install, build, and test the Wikipedia-API project.

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
