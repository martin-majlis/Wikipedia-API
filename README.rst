Wikipedia API
=============

``Wikipedia-API`` is easy to use Python wrapper for `Wikipedias'`_ API. It supports extracting texts, sections, links, categories, translations, etc from Wikipedia. Documentation provides code snippets for the most common use cases.

.. _Wikipedias': https://www.mediawiki.org/wiki/API:Main_page

|github-stars-flat| |codecov-coverage| |docs| |version| |pyversions| |openssf-best-practices|

Installation
------------

This package requires at least Python 3.9 to install because it's using IntEnum.

.. code-block:: python

    pip3 install wikipedia-api


Usage
-----

Goal of ``Wikipedia-API`` is to provide simple and easy to use API for retrieving informations from Wikipedia. The library provides both a **synchronous** (``Wikipedia``) and an **asynchronous** (``AsyncWikipedia``) client. Bellow are examples of common use cases.

Key differences between the sync and async API:

* Info attributes (``fullurl``, ``displaytitle``, ``pageid``, …) are **awaitables**
  in the async API.
* ``title``, ``ns``, ``language``, ``variant`` are plain ``@property`` values in both APIs.
* In the async API, data-fetching properties (``summary``, ``langlinks``, ``links``,
  ``backlinks``, ``categories``, ``categorymembers``) are **awaitable properties**
  (no parentheses): ``await page.summary``, ``await page.langlinks``, etc.
* ``exists()`` is a plain method in the sync API; a **coroutine method** in the async API:
  ``await page.exists()``.
* ``section_by_title()`` and ``sections_by_title()`` are plain synchronous methods
  in both APIs.
* In the async API, ``sections`` is a plain ``@property`` populated after
  ``await page.summary``.

Importing
~~~~~~~~~

.. code-block:: python

    import wikipediaapi

    # Synchronous client
    wiki = wikipediaapi.Wikipedia(user_agent='MyProjectName (merlin@example.com)', language='en')

    # Asynchronous client
    wiki = wikipediaapi.AsyncWikipedia(user_agent='MyProjectName (merlin@example.com)', language='en')

How To Get Single Page
~~~~~~~~~~~~~~~~~~~~~~

Getting single page is straightforward. You have to initialize ``Wikipedia`` (or ``AsyncWikipedia``)
object and ask for page by its name.
To initialize it, you have to provide:

* `user_agent` to identify your project. Please follow the recommended `format`_.
* `language` to specify language mutation. It has to be one of `supported languages`_.

.. _format: https://meta.wikimedia.org/wiki/User-Agent_policy
.. _supported languages: http://meta.wikimedia.org/wiki/List_of_Wikipedias

**Synchronous**

.. code-block:: python

    import wikipediaapi
    wiki_wiki = wikipediaapi.Wikipedia(user_agent='MyProjectName (merlin@example.com)', language='en')

    page_py = wiki_wiki.page('Python_(programming_language)')

**Asynchronous**

.. code-block:: python

    import asyncio
    import wikipediaapi

    async def main():
        wiki_wiki = wikipediaapi.AsyncWikipedia(user_agent='MyProjectName (merlin@example.com)', language='en')
        page_py = wiki_wiki.page('Python_(programming_language)')
        # Data is fetched lazily — await any attribute or property to trigger it

    asyncio.run(main())

How To Check If Wiki Page Exists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For checking, whether page exists, you can use function ``exists``.

**Synchronous**

.. code-block:: python

    page_py = wiki_wiki.page('Python_(programming_language)')
    print("Page - Exists: %s" % page_py.exists())
    # Page - Exists: True

    page_missing = wiki_wiki.page('NonExistingPageWithStrangeName')
    print("Page - Exists: %s" % page_missing.exists())
    # Page - Exists: False

**Asynchronous**

In the async API, ``exists()`` is a coroutine — it lazily fetches ``pageid``
via the ``info`` API call if not yet cached (same approach as ``await page.fullurl``).

.. code-block:: python

    async def main():
        page_py = wiki_wiki.page('Python_(programming_language)')
        print("Page - Exists: %s" % await page_py.exists())
        # Page - Exists: True

        page_missing = wiki_wiki.page('NonExistingPageWithStrangeName')
        print("Page - Exists: %s" % await page_missing.exists())
        # Page - Exists: False

How To Get Page Summary
~~~~~~~~~~~~~~~~~~~~~~~

Class ``WikipediaPage`` has property ``summary``, which returns description of Wiki page.
In the async API, ``summary`` is a coroutine.

**Synchronous**

.. code-block:: python

    import wikipediaapi
    wiki_wiki = wikipediaapi.Wikipedia('MyProjectName (merlin@example.com)', 'en')

    print("Page - Title: %s" % page_py.title)
    # Page - Title: Python (programming language)

    print("Page - Summary: %s" % page_py.summary[0:60])
    # Page - Summary: Python is a widely used high-level programming language for

**Asynchronous**

.. code-block:: python

    async def main():
        print("Page - Title: %s" % page_py.title)
        # Page - Title: Python (programming language)

        summary = await page_py.summary
        print("Page - Summary: %s" % summary[0:60])
        # Page - Summary: Python is a widely used high-level programming language for

How To Get Page URL
~~~~~~~~~~~~~~~~~~~

``WikipediaPage`` has two properties with URL of the page. It is ``fullurl`` and ``canonicalurl``.
In the async API, these attributes are awaitables.

**Synchronous**

.. code-block:: python

    print(page_py.fullurl)
    # https://en.wikipedia.org/wiki/Python_(programming_language)

    print(page_py.canonicalurl)
    # https://en.wikipedia.org/wiki/Python_(programming_language)

**Asynchronous**

.. code-block:: python

    async def main():
        print(await page_py.fullurl)
        # https://en.wikipedia.org/wiki/Python_(programming_language)

        print(await page_py.canonicalurl)
        # https://en.wikipedia.org/wiki/Python_(programming_language)

How To Get Full Text
~~~~~~~~~~~~~~~~~~~~

To get full text of Wikipedia page you should use property ``text`` which constructs text of the page
as concatanation of summary and sections with their titles and texts.

**Synchronous**

.. code-block:: python

    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent='MyProjectName (merlin@example.com)',
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI
    )

    p_wiki = wiki_wiki.page("Test 1")
    print(p_wiki.text)
    # Summary
    # Section 1
    # Text of section 1
    # Section 1.1
    # Text of section 1.1
    # ...


    wiki_html = wikipediaapi.Wikipedia(
        user_agent='MyProjectName (merlin@example.com)',
        language='en',
        extract_format=wikipediaapi.ExtractFormat.HTML
    )
    p_html = wiki_html.page("Test 1")
    print(p_html.text)
    # <p>Summary</p>
    # <h2>Section 1</h2>
    # <p>Text of section 1</p>
    # <h3>Section 1.1</h3>
    # <p>Text of section 1.1</p>
    # ...

**Asynchronous**

The async API does not have a ``text`` property. Compose the full text from
``summary()`` and ``sections`` instead.

.. code-block:: python

    async def main():
        wiki_wiki = wikipediaapi.AsyncWikipedia(
            user_agent='MyProjectName (merlin@example.com)',
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )
        page = wiki_wiki.page("Test 1")
        summary = await page.summary  # also populates page.sections
        print(summary)
        for section in page.sections:
            print(section.title)
            print(section.text)

How To Get Page Sections
~~~~~~~~~~~~~~~~~~~~~~~~

To get all top level sections of page, you have to use property ``sections``. It returns list of
``WikipediaPageSection``, so you have to use recursion to get all subsections.

**Synchronous**

.. code-block:: python

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

**Asynchronous**

In the async API, ``sections`` is a plain ``@property`` populated after ``await page.summary``.

.. code-block:: python

    def print_sections(sections, level=0):
        for s in sections:
            print("%s: %s - %s" % ("*" * (level + 1), s.title, s.text[0:40]))
            print_sections(s.sections, level + 1)

    async def main():
        await page_py.summary  # populates page_py.sections
        print_sections(page_py.sections)
        # *: History - Python was conceived in the late 1980s,
        # *: Features and philosophy - Python is a multi-paradigm programming l

How To Get Page Section By Title
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get last section of page with given title, you have to use function ``section_by_title``.
It returns the last ``WikipediaPageSection`` with this title.
``section_by_title`` works the same in both the sync and async API.

.. code-block:: python

    section_history = page_py.section_by_title('History')
    print("%s - %s" % (section_history.title, section_history.text[0:40]))

    # History - Python was conceived in the late 1980s b

How To Get All Page Sections By Title
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get all sections of page with given title, you have to use function ``sections_by_title``.
It returns the all ``WikipediaPageSection`` with this title.
``sections_by_title`` works the same in both the sync and async API.

.. code-block:: python

    page_1920 = wiki_wiki.page('1920')
    sections_january = page_1920.sections_by_title('January')
    for s in sections_january:
        print("* %s - %s" % (s.title, s.text[0:40]))

    # * January - January 1
    # Polish–Soviet War in 1920: The
    # * January - January 2
    # Isaac Asimov, American author
    # * January - January 1 – Zygmunt Gorazdowski, Polish

How To Get Page In Other Languages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to get other translations of given page, you should use property ``langlinks``. It is map,
where key is language code and value is ``WikipediaPage`` (or ``AsyncWikipediaPage``).

**Synchronous**

.. code-block:: python

    def print_langlinks(page):
        langlinks = page.langlinks
        for k in sorted(langlinks.keys()):
            v = langlinks[k]
            print("%s: %s - %s: %s" % (k, v.language, v.title, v.fullurl))

    print_langlinks(page_py)
    # af: af - Python (programmeertaal): https://af.wikipedia.org/wiki/Python_(programmeertaal)
    # als: als - Python (Programmiersprache): https://als.wikipedia.org/wiki/Python_(Programmiersprache)
    # an: an - Python: https://an.wikipedia.org/wiki/Python
    # ar: ar - بايثون: https://ar.wikipedia.org/wiki/%D8%A8%D8%A7%D9%8A%D8%AB%D9%88%D9%86
    # as: as - পাইথন: https://as.wikipedia.org/wiki/%E0%A6%AA%E0%A6%BE%E0%A6%87%E0%A6%A5%E0%A6%A8

    page_py_cs = page_py.langlinks['cs']
    print("Page - Summary: %s" % page_py_cs.summary[0:60])
    # Page - Summary: Python (anglická výslovnost [ˈpaiθtən]) je vysokoúrovňový sk

**Asynchronous**

In the async API, ``langlinks`` is an awaitable property. Attributes on the returned
page stubs (e.g. ``fullurl``) are also awaitables.

.. code-block:: python

    async def main():
        langlinks = await page_py.langlinks
        for k in sorted(langlinks.keys()):
            v = langlinks[k]
            print("%s: %s - %s: %s" % (k, v.language, v.title, await v.fullurl))

        page_py_cs = langlinks['cs']
        print("Page - Summary: %s" % (await page_py_cs.summary)[0:60])
        # Page - Summary: Python (anglická výslovnost [ˈpaiθtən]) je vysokoúrovňový sk

How To Get Links To Other Pages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to get all links to other wiki pages from given page, you need to use property ``links``.
It's map, where key is page title and value is ``WikipediaPage`` (or ``AsyncWikipediaPage``).

**Synchronous**

.. code-block:: python

    def print_links(page):
        links = page.links
        for title in sorted(links.keys()):
            print("%s: %s" % (title, links[title]))

    print_links(page_py)
    # 3ds Max: 3ds Max (id: ??, ns: 0)
    # ?:: ?: (id: ??, ns: 0)
    # ABC (programming language): ABC (programming language) (id: ??, ns: 0)
    # ALGOL 68: ALGOL 68 (id: ??, ns: 0)
    # Abaqus: Abaqus (id: ??, ns: 0)
    # ...

**Asynchronous**

.. code-block:: python

    async def main():
        links = await page_py.links
        for title in sorted(links.keys()):
            print("%s: %s" % (title, links[title]))

How To Get Page Categories
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to get all categories under which page belongs, you should use property ``categories``.
It's map, where key is category title and value is ``WikipediaPage`` (or ``AsyncWikipediaPage``).

**Synchronous**

.. code-block:: python

    def print_categories(page):
        categories = page.categories
        for title in sorted(categories.keys()):
            print("%s: %s" % (title, categories[title]))


    print("Categories")
    print_categories(page_py)
    # Category:All articles containing potentially dated statements: ...
    # Category:All articles with unsourced statements: ...
    # Category:Articles containing potentially dated statements from August 2016: ...
    # Category:Articles containing potentially dated statements from March 2017: ...
    # Category:Articles containing potentially dated statements from September 2017: ...

**Asynchronous**

.. code-block:: python

    async def main():
        categories = await page_py.categories
        for title in sorted(categories.keys()):
            print("%s: %s" % (title, categories[title]))

How To Get All Pages From Category
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get all pages from given category, you should use property ``categorymembers`` (sync) or
awaitable property ``categorymembers`` (async). It returns all members of given category.
You have to implement recursion and deduplication by yourself.

**Synchronous**

.. code-block:: python

    def print_categorymembers(categorymembers, level=0, max_level=1):
        for c in categorymembers.values():
            print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
            if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
                print_categorymembers(c.categorymembers, level=level + 1, max_level=max_level)


    cat = wiki_wiki.page("Category:Physics")
    print("Category members: Category:Physics")
    print_categorymembers(cat.categorymembers)

    # Category members: Category:Physics
    # * Statistical mechanics (ns: 0)
    # * Category:Physical quantities (ns: 14)
    # ** Refractive index (ns: 0)
    # ** Vapor quality (ns: 0)
    # ** Electric susceptibility (ns: 0)
    # ** Specific weight (ns: 0)
    # ** Category:Viscosity (ns: 14)
    # *** Brookfield Engineering (ns: 0)

**Asynchronous**

.. code-block:: python

    async def print_categorymembers(categorymembers, level=0, max_level=1):
        for c in categorymembers.values():
            print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
            if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
                await print_categorymembers(
                    await c.categorymembers, level=level + 1, max_level=max_level
                )

    async def main():
        cat = wiki_wiki.page("Category:Physics")
        print("Category members: Category:Physics")
        await print_categorymembers(await cat.categorymembers)

Use Extra API Parameters
~~~~~~~~~~~~~~~~~~~~~~~~

Official API supports many different parameters. You can see them in the `sandbox`_. Not all these
parameters are supported directly as parameters of the functions. If you want to specify them,
you can pass them as additional parameters in the constructor. For the `info API call`_ you can
specify parameter `converttitles`. If you want to specify it, you can use:

**Synchronous**

.. code-block:: python

    import wikipediaapi
    wiki_wiki = wikipediaapi.Wikipedia('MyProjectName (merlin@example.com)', 'zh', 'zh-tw', extra_api_params={'converttitles': 1})
    page = wiki_wiki.page("孟卯")
    print(repr(page.varianttitles))

**Asynchronous**

.. code-block:: python

    async def main():
        wiki_wiki = wikipediaapi.AsyncWikipedia('MyProjectName (merlin@example.com)', 'zh', 'zh-tw', extra_api_params={'converttitles': 1})
        page = wiki_wiki.page("孟卯")
        print(repr(await page.varianttitles))


.. _sandbox: https://en.wikipedia.org/wiki/Special:ApiSandbox
.. _info API call: https://zh.wikipedia.org/wiki/Special:API%E6%B2%99%E7%9B%B2#action=query&format=json&variant=zh-tw&prop=info&titles=%E5%AD%9F%E5%8D%AF&converttitles=1&formatversion=2&inprop=varianttitles%7Cdisplaytitle

Error Handling
~~~~~~~~~~~~~~

All exceptions raised by the library inherit from ``WikipediaException``. You can catch specific
exceptions or the base ``WikipediaException``. The same exception types are raised by both the
sync and async clients.

**Synchronous**

.. code-block:: python

    import wikipediaapi

    wiki_wiki = wikipediaapi.Wikipedia(user_agent='MyProjectName (merlin@example.com)', language='en')

    # Catch any Wikipedia-API error
    try:
        page = wiki_wiki.page('Python_(programming_language)')
        print(page.summary[0:60])
    except wikipediaapi.WikipediaException as e:
        print("Error: %s" % e)

.. code-block:: python

    # Handle specific error types
    try:
        page = wiki_wiki.page('Python_(programming_language)')
        print(page.summary[0:60])
    except wikipediaapi.WikiRateLimitError as e:
        print("Rate limited! Retry after: %s seconds" % e.retry_after)
    except wikipediaapi.WikiHttpError as e:
        print("HTTP error %d: %s" % (e.status_code, e))
    except wikipediaapi.WikiHttpTimeoutError:
        print("Request timed out")
    except wikipediaapi.WikiConnectionError:
        print("Could not connect to Wikipedia")
    except wikipediaapi.WikiInvalidJsonError:
        print("Received invalid response from Wikipedia")

**Asynchronous**

.. code-block:: python

    async def main():
        wiki_wiki = wikipediaapi.AsyncWikipedia(user_agent='MyProjectName (merlin@example.com)', language='en')

        try:
            page = wiki_wiki.page('Python_(programming_language)')
            print((await page.summary)[0:60])
        except wikipediaapi.WikiRateLimitError as e:
            print("Rate limited! Retry after: %s seconds" % e.retry_after)
        except wikipediaapi.WikiHttpError as e:
            print("HTTP error %d: %s" % (e.status_code, e))
        except wikipediaapi.WikiHttpTimeoutError:
            print("Request timed out")
        except wikipediaapi.WikiConnectionError:
            print("Could not connect to Wikipedia")
        except wikipediaapi.WikiInvalidJsonError:
            print("Received invalid response from Wikipedia")

Retry Configuration
~~~~~~~~~~~~~~~~~~~

By default, transient errors (HTTP 429, 5xx, timeouts, connection errors) are retried up to 3 times
with exponential backoff. You can configure this behavior in the constructor.
The same options apply to both ``Wikipedia`` and ``AsyncWikipedia``.

.. code-block:: python

    import wikipediaapi

    # Custom retry: 5 retries with 2-second base wait
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent='MyProjectName (merlin@example.com)',
        language='en',
        max_retries=5,
        retry_wait=2.0,
    )

.. code-block:: python

    # Disable retries entirely
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent='MyProjectName (merlin@example.com)',
        language='en',
        max_retries=0,
    )

How To See Underlying API Call
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have problems with retrieving data you can get URL of undrerlying API call.
This will help you determine if the problem is in the library or somewhere else.
Logging works the same for both ``Wikipedia`` and ``AsyncWikipedia``.

.. code-block:: python

    import sys

    import wikipediaapi
    wikipediaapi.log.setLevel(level=wikipediaapi.logging.DEBUG)

    # Set handler if you use Python in interactive mode
    out_hdlr = wikipediaapi.logging.StreamHandler(sys.stderr)
    out_hdlr.setFormatter(wikipediaapi.logging.Formatter('%(asctime)s %(message)s'))
    out_hdlr.setLevel(wikipediaapi.logging.DEBUG)
    wikipediaapi.log.addHandler(out_hdlr)

    wiki = wikipediaapi.Wikipedia(user_agent='MyProjectName (merlin@example.com)', language='en')

    page_ostrava = wiki.page('Ostrava')
    print(page_ostrava.summary)
    # logger prints out: Request URL: http://en.wikipedia.org/w/api.php?action=query&prop=extracts&titles=Ostrava&explaintext=1&exsectionformat=wiki

External Links
--------------

* `GitHub`_
* `PyPi`_
* `ReadTheDocs`_

.. _GitHub: https://github.com/martin-majlis/Wikipedia-API/
.. _PyPi: https://pypi.python.org/pypi/Wikipedia-API/
.. _ReadTheDocs: http://wikipedia-api.readthedocs.io/

Other Badges
------------

|version| |pyversions| |implementations|
|github-downloads| |github-tag| |github-release|
|github-commits-since-latest| |github-forks| |github-stars| |github-watches|
|github-commit-activity| |github-last-commit| |github-code-size| |github-repo-size|
|pypi-license| |pypi-wheel| |pypi-format| |pypi-pyversions| |pypi-implementations|
|pypi-status| |pypi-downloads-dd| |pypi-downloads-dw| |pypi-downloads-dm|
|libraries-io-sourcerank| |libraries-io-dependent-repos| |coveralls|


Other Pages
-----------

.. PYPI-BEGIN
.. toctree::
    :maxdepth: 2

    API
    CHANGES
    CLI
    DESIGN
    DEVELOPMENT
    wikipediaapi/api

.. PYPI-END


.. |docs| image:: https://readthedocs.org/projects/wikipedia-api/badge/?version=latest
    :target: http://wikipedia-api.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |codecov-coverage| image:: https://codecov.io/gh/martin-majlis/Wikipedia-API/graph/badge.svg?token=C4MgwR5nrm
    :target: https://app.codecov.io/gh/martin-majlis/Wikipedia-API
    :alt: Test Coverage

.. |coveralls| image:: https://coveralls.io/repos/github/martin-majlis/Wikipedia-API/badge.svg?branch=master
    :target: https://coveralls.io/github/martin-majlis/Wikipedia-API?branch=master
    :alt: Coveralls

.. |version| image:: https://img.shields.io/pypi/v/wikipedia-api.svg?style=flat
    :target: https://pypi.python.org/pypi/Wikipedia-API
    :alt: Version

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/wikipedia-api.svg?style=flat
    :target: https://pypi.python.org/pypi/Wikipedia-API
    :alt: Py Versions

.. |implementations| image:: https://img.shields.io/pypi/implementation/wikipedia-api.svg?style=flat
    :target: https://pypi.python.org/pypi/Wikipedia-API
    :alt: Implementations

.. |github-downloads| image:: https://img.shields.io/github/downloads/martin-majlis/Wikipedia-API/total.svg
    :target: https://github.com/martin-majlis/Wikipedia-API/releases
    :alt: Downloads

.. |github-tag| image:: https://img.shields.io/github/tag/martin-majlis/Wikipedia-API.svg
    :target: https://github.com/martin-majlis/Wikipedia-API/tags
    :alt: Tags

.. |github-release| image:: https://img.shields.io/github/release/martin-majlis/Wikipedia-API.svg
    :target: https://github.com/martin-majlis/Wikipedia-API/

.. |github-commits-since-latest| image:: https://img.shields.io/github/commits-since/martin-majlis/Wikipedia-API/latest.svg
    :target: https://github.com/martin-majlis/Wikipedia-API/
    :alt: Github commits (since latest release)

.. |github-forks| image:: https://img.shields.io/github/forks/martin-majlis/Wikipedia-API.svg?style=social&label=Fork
    :target: https://github.com/martin-majlis/Wikipedia-API/
    :alt: GitHub forks

.. |github-stars| image:: https://img.shields.io/github/stars/martin-majlis/Wikipedia-API.svg?style=social&label=Stars
    :target: https://github.com/martin-majlis/Wikipedia-API/
    :alt: GitHub stars

.. |github-stars-flat| image:: https://img.shields.io/github/stars/martin-majlis/Wikipedia-API.svg?style=flat&label=Stars
    :target: https://github.com/martin-majlis/Wikipedia-API/
    :alt: GitHub stars

.. |github-watches| image:: https://img.shields.io/github/watchers/martin-majlis/Wikipedia-API.svg?style=social&label=Watch
    :target: https://github.com/martin-majlis/Wikipedia-API/
    :alt: GitHub watchers

.. |github-commit-activity| image:: https://img.shields.io/github/commit-activity/y/martin-majlis/Wikipedia-API.svg
    :target: https://github.com/martin-majlis/Wikipedia-API/commits/master
    :alt: GitHub commit activity the past week, 4 weeks, year

.. |github-last-commit| image:: https://img.shields.io/github/commits/martin-majlis/Wikipedia-API/last.svg
    :target: https://github.com/martin-majlis/Wikipedia-API/
    :alt: Last commit

.. |github-code-size| image:: https://img.shields.io/github/languages/code-size/martin-majlis/Wikipedia-API.svg
    :target: https://github.com/martin-majlis/Wikipedia-API/
    :alt: GitHub code size in bytes

.. |github-repo-size| image:: https://img.shields.io/github/repo-size/martin-majlis/Wikipedia-API.svg
    :target: https://github.com/martin-majlis/Wikipedia-API/
    :alt: GitHub repo size in bytes

.. |pypi-license| image:: https://img.shields.io/pypi/l/Wikipedia-API.svg
    :target: https://pypi.python.org/pypi/Wikipedia-API/
    :alt: PyPi License

.. |pypi-wheel| image:: https://img.shields.io/pypi/wheel/Wikipedia-API.svg
    :target: https://pypi.python.org/pypi/Wikipedia-API/
    :alt: PyPi Wheel

.. |pypi-format| image:: https://img.shields.io/pypi/format/Wikipedia-API.svg
    :target: https://pypi.python.org/pypi/Wikipedia-API/
    :alt: PyPi Format

.. |pypi-pyversions| image:: https://img.shields.io/pypi/pyversions/Wikipedia-API.svg
    :target: https://pypi.python.org/pypi/Wikipedia-API/
    :alt: PyPi PyVersions

.. |pypi-implementations| image:: https://img.shields.io/pypi/implementation/Wikipedia-API.svg
    :target: https://pypi.python.org/pypi/Wikipedia-API/
    :alt: PyPi Implementations

.. |pypi-status| image:: https://img.shields.io/pypi/status/Wikipedia-API.svg
    :target: https://pypi.python.org/pypi/Wikipedia-API/
    :alt: PyPi Status

.. |pypi-downloads-dd| image:: https://img.shields.io/pypi/dd/Wikipedia-API.svg
    :target: https://pypi.python.org/pypi/Wikipedia-API/
    :alt: PyPi Downloads - Day

.. |pypi-downloads-dw| image:: https://img.shields.io/pypi/dw/Wikipedia-API.svg
    :target: https://pypi.python.org/pypi/Wikipedia-API/
    :alt: PyPi Downloads - Week

.. |pypi-downloads-dm| image:: https://img.shields.io/pypi/dm/Wikipedia-API.svg
    :target: https://pypi.python.org/pypi/Wikipedia-API/
    :alt: PyPi Downloads - Month

.. |libraries-io-sourcerank| image:: https://img.shields.io/librariesio/sourcerank/pypi/Wikipedia-API.svg
    :target: https://libraries.io/pypi/Wikipedia-API
    :alt: Libraries.io - SourceRank

.. |libraries-io-dependent-repos| image:: https://img.shields.io/librariesio/dependent-repos/pypi/Wikipedia-API.svg
    :target: https://libraries.io/pypi/Wikipedia-API
    :alt: Libraries.io - Dependent Repos

.. |openssf-best-practices| image:: https://www.bestpractices.dev/projects/12083/badge
    :target: https://www.bestpractices.dev/projects/12083
    :alt: OpenSSF Best Practices
