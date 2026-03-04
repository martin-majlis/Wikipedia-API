Contributing
============

Thank you for your interest in contributing to Wikipedia-API! This guide will help you get started with setting up the development environment and making contributions.

Prerequisites
-------------

* **Python 3.10+** (supported: 3.10, 3.11, 3.12, 3.13, 3.14)
* **Make**
* **Pip**
* **Virtual environment** already set up in ``.venv/``

Getting Started
---------------

1. Clone the repository::

    git clone https://github.com/martin-majlis/Wikipedia-API.git
    cd Wikipedia-API

2. Activate the virtual environment (always required before running any command)::

    source .venv/bin/activate

3. Install all dependencies::

    make requirements-all

   Or install individual dependency groups:

   * **Runtime dependencies:** ``make requirements`` (installs ``requirements.txt`` — ``requests``)
   * **Dev dependencies:** ``make requirements-dev`` (installs ``requirements-dev.txt`` — black, coverage, flake8, isort, mypy, pre-commit, tox, etc.)
   * **Doc dependencies:** ``make requirements-doc`` (installs ``requirements-doc.txt`` — sphinx)
   * **Build dependencies:** ``make requirements-build`` (installs ``requirements-build.txt`` — rst2html, setuptools, wheel)

Development Workflow
--------------------

1. Create a new branch for your feature or bugfix::

    git checkout -b feature-name

2. Make your changes following the coding standards (see Linting & Type Checking section)

3. Run tests to ensure your changes don't break existing functionality::

    make run-tests

4. Run linting and type checking::

    make run-pre-commit

5. Commit your changes with a descriptive commit message

6. Push your branch and create a pull request

Testing
-------

Run Tests
~~~~~~~~~

The main test command runs both unit tests and CLI verification tests::

    make run-tests

* The unit tests are executed via ``python3 -m unittest discover tests/ '*test.py'``. All test files are in the ``tests/`` directory and follow the ``*test.py`` naming pattern.
* The CLI verification tests are run using ``./tests/cli/test_cli.sh verify``.

CLI Tests
~~~~~~~~~

You can run the CLI tests independently:

* **Verify CLI:** ``make run-test-cli-verify``
  - This runs the CLI tests to verify that the output matches the recorded snapshots. It uses ``./tests/cli/test_cli.sh verify``.

* **Record CLI Snapshots:** ``make run-test-cli-record``
  - This command updates the CLI test snapshots with the current output. Use this when you have intentionally changed the CLI's output. It runs ``./tests/cli/test_cli.sh record``.

Test Coverage
~~~~~~~~~~~~~

Run tests with coverage to generate a coverage report and ``coverage.xml`` for the ``wikipediaapi`` package::

    make run-coverage

Multi-Python Testing
~~~~~~~~~~~~~~~~~~~~~

Run the test suite against Python 3.10–3.14 via tox::

    make run-tox

Linting & Type Checking
------------------------

Run All Pre-commit Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~

This runs isort, black, flake8, mypy, pyupgrade, and other checks (trailing whitespace, YAML validation, etc.)::

    make run-pre-commit

Individual Checks
~~~~~~~~~~~~~~~~~

* **Type checking:** ``make run-type-check`` (runs ``mypy ./wikipediaapi``)
* **Linting:** ``make run-flake8`` (runs ``flake8 --max-line-length=100 wikipediaapi tests``)

Building
--------

Build the source distribution package::

    make build-package

Generate PyPI HTML documentation preview::

    make pypi-html

Generate Sphinx HTML documentation::

    make html

Pre-release Check
-----------------

Run the full validation suite (pre-commit, type check, flake8, coverage, pypi-html, tox, example)::

    make pre-release-check

Project Structure
-----------------

* ``wikipediaapi/`` — Main package (single ``__init__.py`` module)
* ``tests/`` — Unit tests (``*test.py`` files, ``mock_data.py`` for test fixtures)
* ``setup.py`` — Package metadata and build configuration
* ``Makefile`` — All build, test, and release commands
* ``requirements.txt`` — Runtime dependencies
* ``requirements-dev.txt`` — Development dependencies
* ``requirements-doc.txt`` — Documentation dependencies
* ``requirements-build.txt`` — Build/packaging dependencies
* ``tox.ini`` — Multi-Python test configuration
* ``.pre-commit-config.yaml`` — Pre-commit hook definitions

Coding Standards
----------------

* Follow PEP 8 style guidelines
* Use type hints where appropriate
* Write tests for new functionality
* Keep code coverage high
* Use descriptive commit messages
* Update documentation for API changes

Submitting Pull Requests
------------------------

1. Ensure all tests pass
2. Run the full pre-commit check suite
3. Update documentation if necessary
4. Provide a clear description of your changes
5. Link to any relevant issues

Release Process
---------------

The project maintainer handles releases using::

    make release

This creates a new release as well as a git tag.

Getting Help
------------

If you need help with development:

* Check existing issues on GitHub
* Read the project documentation
* Review the test files for examples
* Study the existing codebase structure

Thank you for contributing to Wikipedia-API!
