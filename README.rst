Wikipedia API
=============

This package provides python API for accessing `Wikipedia`_.

.. _Wikipedia: https://www.mediawiki.org/wiki/API:Main_page

|build-status| |docs| |cc-badge| |cc-issues|

.. PYPI-BEGIN
.. toctree::
	:maxdepth: 2

	API
	CHANGES
	DEVELOPMENT
.. PYPI-END

Installation
------------

.. code-block:: python

    pip3 install wikipedia-api


Usage
-----

.. code-block:: python

	import wikipedia

	# Extract data in Wiki format
	wiki_wiki = wikipedia.Wikipedia('en')

	page_py = wiki_wiki.article('Python_(programming_language)')

	print("Page - Exists: %s" % page_py.exists())
	# Page - Exists: True

	print("Page - Id: %s" % page_py.pageid)
	# Page - Id: 23862

	print("Page - Title: %s" % page_py.title)
	# Page - Title: Python (programming language)

	print("Page - Summary: %s" % page_py.summary[0:60])
	# Page - Summary: Python is a widely used high-level programming language for


	def print_sections(sections, level=0):
		for s in sections:
			print("%s: %s - %s" % ("*" * (level + 1), s.title, s.text[0:40]))
			print_sections(s.sections, level + 1)


	print_sections(page_py.sections)
	# *: History - Python was conceived in the late 1980s, 
	# *: Features and philosophy - Python is a multi-paradigm programming l
	# *: Syntax and semantics - Python is meant to be an easily readable
	# **: Indentation - Python uses whitespace indentation, rath
	# **: Statements and control flow - Python's statements include (among other
	# **: Expressions - Some Python expressions are similar to l
	# ...

	section_py = page_py.section_by_title('Features and philosophy')
	print("Section - Title: %s" % section_py.title)
	# Section - Title: Features and philosophy

	print("Section - Text: %s" % section_py.text[0:60])
	# Section - Text: Python is a multi-paradigm programming language. Object-orie

	# Now lets extract texts with HTML tags
	wiki_html = wikipedia.Wikipedia(
		language='cs',
		extract_format=wikipedia.ExtractFormat.HTML
	)

	page_ostrava = wiki_html.article('Ostrava')

	print("Page - Exists: %s" % page_ostrava.exists())
	# Page - Exists: True

	print("Page - Id: %s" % page_ostrava.pageid)
	# Page - Id: 7667

	print("Page - Title: %s" % page_ostrava.title)
	# Page - Title: Ostrava

	print("Page - Summary: %s" % page_ostrava.summary[0:60])
	# Page - Summary: <p><b>Ostrava</b> (polsky <span lang="pl" title="polština" x

	print_sections(page_ostrava.sections)
	# *: Znak a logo - 
	# **: Heraldický znak - <p>Městský znak je blasonován: <i>V modr
	# **: Marketingové logo - <p>V roce 2008 bylo představeno nové log
	# *: Historie - <dl><dd><i>Související informace nalezne
	# **: Zemské hranice - <p>Zemské hranice zde tvoří řeky Odra a 
	# *: Obyvatelstvo - <ul class="gallery mw-gallery-traditiona

	section_ostrava = page_ostrava.section_by_title('Heraldický znak')
	print("Section - Title: %s" % section_ostrava.title)
	# Section - Title: Heraldický znak

	print("Section - Text: %s" % section_ostrava.text[0:60])
	# Section - Text: <p>Městský znak je blasonován: <i>V modrém štítě na zeleném

	page_nonexisting = wiki_wiki.article('Wikipedia-API-FooBar')
	print("Page - Exists: %s" % page_nonexisting.exists())
	# Page - Exists: False

	print("Page - Id: %s" % page_nonexisting.pageid)
	# Page - Id: -1

	print("Page - Title: %s" % page_nonexisting.title)
	# Page - Title: Wikipedia-API-FooBar
	
	print("Page - Summary: %s" % page_nonexisting.summary[0:60])
	# Page - Summary:

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
