Wikipedia API
=============

This package provides python API for accessing `Wikipedia`_.

.. _Wikipedia: https://www.mediawiki.org/wiki/API:Main_page

|build-status| |docs| |cc-badge| |cc-issues|

.. PYPI-BEGIN
.. toctree::
   :maxdepth: 2

   CHANGES
.. PYPI-END

Installation
------------

.. code-block:: python

    pip3 install wikipedia-api


Usage
-----

.. code-block:: python

	import wikipedia

	wiki = wikipedia.Wikipedia('en')

	page = wiki.article('Python_(programming_language)')

	print("Page - Id: %s" % page.id())
	# Page - Id: 23862

	print("Page - Title: %s" % page.title())
	# Page - Title: Python (programming language)

	print("Page - Summary: %s" % page.summary())
	# Page - Summary: Python is a widely used high-level programming ...


	def print_sections(sections, level=0):
		for s in sections:
		    print("%s: %s - %s" % ("*" * (level + 1), s.title(), s.text()[0:40]))
		    print_sections(s.sections(), level + 1)


	print_sections(page.sections())
	# *: History - Python was conceived in the late 1980s, 
	# *: Features and philosophy - Python is a multi-paradigm programming l
	# *: Syntax and semantics - Python is meant to be an easily readable
	# **: Indentation - Python uses whitespace indentation, rath
	# **: Statements and control flow - Python's statements include (among other
	# **: Expressions - Some Python expressions are similar to l
	# ...

	libraries = page.section_by_title('Libraries')
	print("Section - Title: %s" % libraries.title())
	# Section - Title: Libraries

	print("Section - Text: %s" % libraries.text())
	# Section - Text: Python's large standard library, commonly cited as ...

External Links
--------------

* `GitHub`_
* `PyPi`_
* `Travis`_
* `ReadTheDocs`_

.. _GitHub: https://github.com/martin-majlis/Wikipedia-API/
.. _PyPi: https://pypi.python.org/pypi/Wikipedia-API/
.. _Travis: https://travis-ci.org/martin-majlis/Wikipedia-API/
.. _ReadTheDocs: http://wikipedia-api.readthedocs.io/


Usage Statistics
----------------

* `Downloads by version`_
* `Downloads by version and country`_
* `Downloads by date`_
* `Downloads comparison`_

.. _Downloads by version: https://bigquery.cloud.google.com/savedquery/35201106510:a6c4870ce9fb43e6aefef12faf56128b
.. _Downloads by version and country: https://bigquery.cloud.google.com/savedquery/35201106510:46e43ec892d64a10ae9e52a214ee4e04
.. _Downloads by date: https://bigquery.cloud.google.com/savedquery/35201106510:3848fc01939a4fd3aa265478bfcb6a11
.. _Downloads comparison: https://bigquery.cloud.google.com/savedquery/35201106510:40051d42809040a3937b8efce9ea7053




.. |build-status| image:: https://travis-ci.org/martin-majlis/Wikipedia-API.svg?branch=master
    :alt: build status
    :target: https://travis-ci.org/martin-majlis/Wikipedia-API

.. |docs| image:: https://readthedocs.org/projects/wikipedia-api/badge/?version=latest
    :target: http://wikipedia-api.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |cc-badge| image:: https://codeclimate.com/github/martin-majlis/Wikipedia-API/badges/gpa.svg
    :target: https://codeclimate.com/github/martin-majlis/Wikipedia-API
    :alt: Code Climate

.. |cc-issues| image:: https://codeclimate.com/github/martin-majlis/Wikipedia-API/badges/issue_count.svg
    :target: https://codeclimate.com/github/martin-majlis/Wikipedia-API
    :alt: Issue Count
