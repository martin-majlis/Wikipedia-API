Development
===========

Prerequisities
--------------
* Make
* Python3.10+
* Pip

Makefile targets
----------------
* ``make run-pre-commit`` - lints source code
* ``make requirements-all`` - install all requirements
  * ``make requirements`` - install package requirements
  * ``make requirements-dev`` - install development requirements
* ``make run-tests`` - run unit tests
* ``make run-coverage`` - run code coverage
* ``make pypi-html`` - generates single HTML documentation into ``pypi-doc.html``
* ``make html`` - generates HTML documentation similar to RTFD into folder ``_build/html/``
* ``make release`` - creates new release as well as git tag

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
