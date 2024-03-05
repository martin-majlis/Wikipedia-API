Changelog
=========

0.6.8
-----

* Update dependencies
* Add tests for more platforms

0.6.0
-----

* Make user agent mandatory - `Issue 63`_
* This breaks the API since `user_agent` is now the first parameter.

.. _Issue 63: https://github.com/martin-majlis/Wikipedia-API/issues/63


0.5.8
-----

* Adds support for retrieving all sections with given name - `Issue 39`_

.. _Issue 39: https://github.com/martin-majlis/Wikipedia-API/issues/39

0.5.4
-----

* Namespace could be arbitrary integer - `Issue 29`_

.. _Issue 29: https://github.com/martin-majlis/Wikipedia-API/issues/29


0.5.3
-----

* Adds persistent HTTP connection - `Issue 26`_
    * Downloading 50 pages reduced from 13s to 8s => 40% speed up

.. _Issue 26: https://github.com/martin-majlis/Wikipedia-API/issues/26


0.5.2
-----

* Adds namespaces 102 - 105 - `Issue 24`_

.. _Issue 24: https://github.com/martin-majlis/Wikipedia-API/issues/24

0.5.1
-----

* Adds tox for testing different Python versions

0.5.0
-----

* Allows modifying API call parameters
* Fixes `Issue 16`_ - hidden categories
* Fixes `Issue 21`_ - summary extraction

.. _Issue 16: https://github.com/martin-majlis/Wikipedia-API/issues/16
.. _Issue 21: https://github.com/martin-majlis/Wikipedia-API/issues/21


0.4.5
-----

* Handles missing sections correctly
* Fixes `Issue 20`_

.. _Issue 20: https://github.com/martin-majlis/Wikipedia-API/issues/20


0.4.4
-----
* Uses HTTPS directly instead of HTTP to avoid redirect

0.4.3
-----
* Correctly extracts text from pages without sections
* Adds support for quoted page titles

.. code:: python

    api = wikipediaapi.Wikipedia(
        language='hi',
    )
    python = api.article(
        title='%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8',
        unquote=True,
    )
    print(python.summary)

0.4.2
-----
* Adds support for Python 3.4 by not using f-strings

0.4.1
-----
* Uses code style enforced by flake8
* Increased code coverage

0.4.0
-----
* Uses type annotations => minimal requirement is now Python 3.5
* Adds possibility to use more parameters for `request`_. For example:

.. code:: python

    api = wikipediaapi.Wikipedia(
        language='en',
        proxies={'http': 'http://localhost:1234'}
    )

* Extends documentation

.. _request: http://docs.python-requests.org/en/master/api/#requests.request

0.3.4
-----
* Adds support for `property Categorymembers`_
* Adds property ``text`` for retrieving complete text of the page

.. _property Categorymembers: https://www.mediawiki.org/wiki/API:Categorymembers

0.3.3
-----
* Added support for `request timeout`_
* Add header: Accept-Encoding: gzip

.. _request timeout: https://github.com/martin-majlis/Wikipedia-API/issues/1

0.3.2
-----
* Added support for `property Categories`_

.. _property Categories: https://www.mediawiki.org/wiki/API:Categories

0.3.1
-----
* Removing ``WikipediaLangLink``
* Page keeps track of its own language, so it's easier to jump between different translations of the same page

0.3.0
-----
* Rename directory from ``wikipedia`` to ``wikipediaapi`` to avoid collisions

0.2.4
-----
* Handle redirects properly

0.2.3
-----
* Usage method ``page`` instead of ``article`` in ``Wikipedia``

0.2.2
-----
* Added support for `property Links`_

.. _property Links: https://www.mediawiki.org/wiki/API:Links

0.2.1
-----
* Added support for `property Langlinks`_

.. _property Langlinks: https://www.mediawiki.org/wiki/API:Langlinks

0.2.0
-----
* Use properties instead of functions
* Added support for `property Info`_

.. _property Info: https://www.mediawiki.org/wiki/API:Info

0.1.6
-----
* Support for extracting texts with HTML markdown
* Added initial version of unit tests

0.1.4
-----
* It's possible to extract summary and sections of the page
* Added support for `property Extracts`_

.. _property Extracts: https://www.mediawiki.org/wiki/Extension:TextExtracts#API
