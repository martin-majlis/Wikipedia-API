# AGENTS.md

Guide for AI agents (and developers) on how to install, build, and test the Wikipedia-API project.

## Prerequisites

- **Python 3.10+** (supported: 3.10, 3.11, 3.12, 3.13, 3.14)
- **Virtual environment** already set up in `.venv/`

## Virtual Environment

**Always activate the virtual environment before running any command:**

```bash
source .venv/bin/activate
```

## Install

Install all dependencies (runtime, dev, docs, build):

```bash
make requirements-all
```

Or install individual dependency groups:

- **Runtime dependencies:** `make requirements` (installs `requirements.txt` — `requests`)
- **Dev dependencies:** `make requirements-dev` (installs `requirements-dev.txt` — black, coverage, flake8, isort, mypy, pre-commit, tox, etc.)
- **Doc dependencies:** `make requirements-doc` (installs `requirements-doc.txt` — sphinx)
- **Build dependencies:** `make requirements-build` (installs `requirements-build.txt` — rst2html, setuptools, wheel)

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

### Run Unit Tests

```bash
make run-tests
```

This runs `python3 -m unittest discover tests/ '*test.py'`. All test files are in the `tests/` directory and follow the `*test.py` naming pattern.

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
- `setup.py` — Package metadata and build configuration
- `Makefile` — All build, test, and release commands
- `requirements.txt` — Runtime dependencies
- `requirements-dev.txt` — Development dependencies
- `requirements-doc.txt` — Documentation dependencies
- `requirements-build.txt` — Build/packaging dependencies
- `tox.ini` — Multi-Python test configuration
- `.pre-commit-config.yaml` — Pre-commit hook definitions
