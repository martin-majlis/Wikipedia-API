Wikipedia API
==========

This package provides fluent API for `MailGun API`_.

.. _MailGun API: http://mailgun-documentation.readthedocs.io/

|build-status| |docs| |cc-badge| |cc-issues|

.. PYPI-BEGIN
.. toctree::
   :maxdepth: 2

   CHANGES
   API
.. PYPI-END

Installation
------------

.. code-block:: python

    pip install mailgunv3


Usage
-----

.. code-block:: python

    domain = 'example.com'

    mg = MailGunV3(domain,
                   'key-asdfghjkl',
                   'pubkey-asdfghjkl')

    res1 = (mg.
            mailinglist('mlA-{}@{}'.format(random.randint(0, 10), domain)).
            create('Test Mailing List').
            delete())
    print(repr(res1))

    res2 = (mg.
            mailinglist('mlB-{}@{}'.format(random.randint(0, 10), domain)).
            create('Test Mailing List').
            update(
                name='New Name',
                description='New Description').
            get())
    print(repr(res2))

    res3 = (mg.
            mailinglist('newsletter-dev@' + domain).
            members())
    print(repr(res3))

    res4 = (mg.
            mailinglist('newsletter-dev@' + domain).
            member('a01-{}@{}'.format(random.randint(0, 1000), domain)).
            create(
                name='Foo Bar',
                params={'a': 1, 'b': 2}).
            get())
    print(repr(res4))

    res5 = (mg.
            mailinglist('newsletter-dev@' + domain).
            member('a01-{}@{}'.format(random.randint(0, 1000), domain)).
            update(
                name='Foo Bar - EDIT',
                params={'a': 1, 'b': 2}).
            get())
    print(repr(res5))

    res6 = (mg.
            mailinglist('newsletter-dev@' + domain).
            members())
    print(repr(res6))

    res7 = (mg.
            mailinglist('newsletter-dev@' + domain).
            member('a01@' + domain).
            delete())
    print(repr(res7))

External Links
--------------

* `GitHub`_
* `PyPi`_
* `Travis`_
* `ReadTheDocs`_

.. _GitHub: https://github.com/martin-majlis/MailGunV3/
.. _PyPi: https://pypi.python.org/pypi/MailGunV3/
.. _Travis: https://travis-ci.org/martin-majlis/MailGunV3/
.. _ReadTheDocs: http://mailgunv3.readthedocs.io/



.. |build-status| image:: https://travis-ci.org/martin-majlis/MailGunV3.svg?branch=master
    :alt: build status
    :target: https://travis-ci.org/martin-majlis/MailGunV3

.. |docs| image:: https://readthedocs.org/projects/mailgunv3/badge/?version=latest
    :target: http://mailgunv3.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |cc-badge| image:: https://codeclimate.com/github/martin-majlis/MailGunV3/badges/gpa.svg
    :target: https://codeclimate.com/github/martin-majlis/MailGunV3
    :alt: Code Climate

.. |cc-issues| image:: https://codeclimate.com/github/martin-majlis/MailGunV3/badges/issue_count.svg
    :target: https://codeclimate.com/github/martin-majlis/MailGunV3
    :alt: Issue Count
