Development
===========

Makefile targets
----------------
* ``make release`` - based on version specified in ``wikipedia/__init__.py`` creates new release as well as git tag
* ``make run-tests`` - run unit tests
* ``make run-coverage`` - run code coverage
* ``make pypi-html`` - generates single HTML documentation into ``pypi-doc.html``
* ``make html`` - generates HTML documentation similar to RTFD into folder ``_build/html/``
* ``make requirements`` - install requirements
* ``make requirements-dev`` - install development requirements

Usage Statistics
----------------

* `PIP Downloads`_

.. _PIP Downloads: https://pypistats.org/packages/wikipedia-api


Underlying API
--------------

* `API - HP`_
* `Module - Parse`_
* `Module - Query`_

.. _API - HP: https://www.mediawiki.org/wiki/API:Main_page
.. _Module - Parse: https://en.wikipedia.org/w/api.php?action=help&modules=parse
.. _Module - Query: https://en.wikipedia.org/w/api.php?action=help&modules=query
