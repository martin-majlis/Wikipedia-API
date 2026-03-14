================
``wikipediaapi``
================

.. automodule:: wikipediaapi
    :members:
    :exclude-members: Wikipedia, AsyncWikipedia, WikipediaPage, AsyncWikipediaPage,
        WikipediaPageSection, ExtractFormat, Namespace,
        WikipediaException, WikiHttpTimeoutError, WikiHttpError,
        WikiRateLimitError, WikiInvalidJsonError, WikiConnectionError
    :member-order: bysource

-------
Clients
-------

.. autoclass:: wikipediaapi.Wikipedia
    :members:
    :exclude-members: __module__, __weakref__

.. autoclass:: wikipediaapi.AsyncWikipedia
    :members:
    :exclude-members: __module__, __weakref__

-----
Pages
-----

.. autoclass:: wikipediaapi.WikipediaPage
    :members:
    :exclude-members: __module__, __weakref__

.. autoclass:: wikipediaapi.AsyncWikipediaPage
    :members:
    :exclude-members: __module__, __weakref__

.. autoclass:: wikipediaapi.WikipediaPageSection
    :members:
    :exclude-members: __module__, __weakref__

--------------
Enums & Types
--------------

.. autoclass:: wikipediaapi.ExtractFormat
    :members:
    :member-order: bysource

.. autoclass:: wikipediaapi.Namespace
    :members:
    :undoc-members:
    :member-order: bysource
    :exclude-members: __module__, __weakref__

----------
Exceptions
----------

.. autoexception:: wikipediaapi.WikipediaException

.. autoexception:: wikipediaapi.WikiHttpTimeoutError
    :members:

.. autoexception:: wikipediaapi.WikiHttpError
    :members:

.. autoexception:: wikipediaapi.WikiRateLimitError
    :members:

.. autoexception:: wikipediaapi.WikiInvalidJsonError
    :members:

.. autoexception:: wikipediaapi.WikiConnectionError
    :members:
