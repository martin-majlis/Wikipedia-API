CLI
===

Wikipedia-API includes a command line tool ``wikipedia-api`` that is
automatically installed with the package. It provides access to all
library features from the terminal.

Global Options
--------------

Every command supports the following options:

* ``-l, --language`` — Language edition of Wikipedia (default: ``en``)
* ``-u, --user-agent`` — HTTP User-Agent string
* ``-v, --variant`` — Language variant (e.g. ``zh-cn``, ``zh-tw``)
* ``-f, --extract-format`` — Extraction format: ``wiki`` or ``html`` (default: ``wiki``)
* ``-n, --namespace`` — Wikipedia namespace number (default: ``0`` = Main)
* ``-h, --help`` — Show help for any command

Commands that return lists also support:

* ``--json`` — Output results as JSON

Getting Help
------------

Show all available commands::

    wikipedia-api --help

Show help for a specific command::

    wikipedia-api summary --help

Show version::

    wikipedia-api --version

Page Info
---------

Show metadata about a page::

    wikipedia-api page "Python (programming language)"

Output as JSON::

    wikipedia-api page "Python (programming language)" --json

Summary
-------

Print the summary of a Wikipedia page::

    wikipedia-api summary "Python (programming language)"

Summary in Czech::

    wikipedia-api summary "Ostrava" --language cs

Summary in Chinese with variant::

    wikipedia-api summary "Python" --language zh --variant zh-cn

Full Text
---------

Print the full text (summary + all sections)::

    wikipedia-api text "Python (programming language)"

Full text in HTML format::

    wikipedia-api text "Ostrava" --language cs --extract-format html

Sections
--------

List all sections of a page::

    wikipedia-api sections "Python (programming language)"

List sections as JSON::

    wikipedia-api sections "Python (programming language)" --json

Print the text of a specific section::

    wikipedia-api section "Python (programming language)" "Features and philosophy"

Links
-----

List all pages linked from a page::

    wikipedia-api links "Python (programming language)"

Output as JSON::

    wikipedia-api links "Python (programming language)" --json

Backlinks
---------

List pages that link to a given page::

    wikipedia-api backlinks "Python (programming language)"

Output as JSON::

    wikipedia-api backlinks "Python (programming language)" --json

Language Links
--------------

List translations of a page in other language editions::

    wikipedia-api langlinks "Python (programming language)"

Output as JSON::

    wikipedia-api langlinks "Python (programming language)" --json

Categories
----------

List categories a page belongs to::

    wikipedia-api categories "Python (programming language)"

Output as JSON::

    wikipedia-api categories "Python (programming language)" --json

Category Members
----------------

List pages in a category::

    wikipedia-api categorymembers "Category:Physics"

Recursively list subcategory members (depth 1)::

    wikipedia-api categorymembers "Category:Physics" --max-level 1

Output as JSON::

    wikipedia-api categorymembers "Category:Physics" --json

Coordinates
-----------

Show geographic coordinates for a page::

    wikipedia-api coordinates "Mount Everest"

Show all coordinates (primary and secondary)::

    wikipedia-api coordinates "Mount Everest" --primary all

Output as JSON::

    wikipedia-api coordinates "Mount Everest" --json

Images
------

List images (files) used on a page::

    wikipedia-api images "Python (programming language)"

Output as JSON::

    wikipedia-api images "Python (programming language)" --json

Fetch image metadata (URL, dimensions, MIME type, uploader, etc.) with
the ``--imageinfo`` flag::

    wikipedia-api images "Mount Everest" --imageinfo

Display imageinfo metadata as JSON::

    wikipedia-api images "Mount Everest" --imageinfo --json

Limit the number of images::

    wikipedia-api images "Earth" --limit 50

Combine options::

    wikipedia-api images "Earth" --limit 20 --imageinfo --language de

Geosearch
---------

Search for pages near a geographic coordinate::

    wikipedia-api geosearch --coord "51.5074|-0.1278"

Search near a named page::

    wikipedia-api geosearch --page "Big Ben" --radius 1000

Output as JSON::

    wikipedia-api geosearch --coord "48.8566|2.3522" --json

Random
------

Get a random Wikipedia page::

    wikipedia-api random

Get multiple random pages::

    wikipedia-api random --limit 5

Output as JSON::

    wikipedia-api random --limit 3 --json

Search
------

Search Wikipedia for pages matching a query::

    wikipedia-api search "Python programming"

Output as JSON::

    wikipedia-api search "Python programming" --json

Search in another language::

    wikipedia-api search "машинное обучение" --language ru

Complete Workflow Example
-------------------------

Fetch a page summary, then explore its sections and links::

    # Get summary
    wikipedia-api summary "Python (programming language)"

    # List sections
    wikipedia-api sections "Python (programming language)"

    # Read a specific section
    wikipedia-api section "Python (programming language)" "History"

    # List categories
    wikipedia-api categories "Python (programming language)"

    # Find the page in other languages
    wikipedia-api langlinks "Python (programming language)"

    # Get the same page in German
    wikipedia-api summary "Python (Programmiersprache)" --language de

    # Show coordinates for a geographic page
    wikipedia-api coordinates "Mount Everest"

    # Search for pages near a location
    wikipedia-api geosearch --coord "27.9881|86.9250"

    # Search Wikipedia
    wikipedia-api search "Mount Everest"

    # Get random pages
    wikipedia-api random --limit 3
