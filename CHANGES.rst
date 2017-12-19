Changelog
=========

0.3.4
-----
* Added support for `property Categorymembers`_
* Added property ``text`` for retrieving complete text of the page

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
