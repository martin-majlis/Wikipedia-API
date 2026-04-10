Development
===========

Prerequisites
--------------

* Make
* Python 3.10+
* Pip

Makefile targets
-----------------
* ``make run-type-check`` - type checks source code (runs ``uv run ty check wikipediaapi/``)
* ``make run-ruff`` - lints and checks formatting (runs ``ruff check`` and ``ruff format --check``)
* ``make requirements-all`` - install all requirements
  * ``make requirements`` - install package requirements
  * ``make requirements-dev`` - install development requirements
* ``make run-tests`` - run unit tests (pytest)
* ``make run-tests-integration`` - run VCR integration tests (pytest)
* ``make run-coverage`` - run code coverage (pytest-cov)
* ``make pypi-html`` - generates single HTML documentation into ``pypi-doc.html``
* ``make html`` - generates HTML documentation similar to RTFD into folder ``_build/html/``
* ``make prepare-release VERSION='1.2.3'`` - bumps version files, runs full pre-release checks, and opens a PR from a ``release/1.2.3`` branch
* ``make create-github-release VERSION='1.2.3'`` - after the PR is merged, creates a GitHub Release with auto-generated notes, triggering PyPI publish

Releasing a New Version
-----------------------

1. Add an entry for the new version to ``CHANGES.rst`` (a line with exactly ``X.Y.Z`` as a heading).

2. From a clean ``master`` branch, run::

    make prepare-release VERSION='1.2.3'

   This will validate the version, bump ``pyproject.toml``, ``conf.py``, and
   ``wikipediaapi/_version.py``, run the full pre-release check suite, commit to
   a ``release/1.2.3`` branch, push it, and open a pull request.

3. Review and merge the pull request.

4. After the PR is merged, create the GitHub Release::

    make create-github-release VERSION='1.2.3'

   This creates a ``v1.2.3`` tag and GitHub Release with auto-generated release
   notes (based on merged PRs since the last release), which triggers the
   ``release.yml`` workflow to publish the package to PyPI.

Usage Statistics
----------------

* `PIP Downloads`_
* `Clickpy`_
* `Libraries.io`_
* `Deps.dev`_

.. _PIP Downloads: https://pypistats.org/packages/wikipedia-api
.. _Libraries.io: https://libraries.io/pypi/Wikipedia-API
.. _Deps.dev: https://deps.dev/pypi/wikipedia-api
.. _Clickpy: https://clickpy.clickhouse.com/dashboard/wikipedia-api

Underlying API
--------------

* `API - HP`_
* `Module - Parse`_
* `Module - Query`_

.. _API - HP: https://www.mediawiki.org/wiki/API:Main_page
.. _Module - Parse: https://en.wikipedia.org/w/api.php?action=help&modules=parse
.. _Module - Query: https://en.wikipedia.org/w/api.php?action=help&modules=query
