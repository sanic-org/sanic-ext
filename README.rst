.. image:: https://raw.githubusercontent.com/sanic-org/sanic-assets/master/png/sanic-framework-logo-400x97.png
    :alt: Sanic | Build fast. Run fast.

Sanic Extensions
================

.. start-badges

.. list-table::
    :widths: 15 85
    :stub-columns: 1

    * - Build
      - | |PyTest|
    * - Docs
      - | |UserGuide|
    * - Package
      - | |PyPI| |PyPI version| |Wheel| |Supported implementations| |Code style black|
    * - Support
      - | |Forums| |Discord|


.. |UserGuide| image:: https://img.shields.io/badge/user%20guide-sanic-ff0068
   :target: https://sanicframework.org/en/plugins/sanic-ext/getting-started.html
.. |Forums| image:: https://img.shields.io/badge/forums-community-ff0068.svg
   :target: https://community.sanicframework.org/
.. |Discord| image:: https://img.shields.io/discord/812221182594121728?logo=discord
   :target: https://discord.gg/FARQzAEMAA
.. |PyTest| image:: https://github.com/sanic-org/sanic-ext/actions/workflows/python-package.yml/badge.svg?branch=main
   :target: https://github.com/sanic-org/sanic-ext/actions/workflows/python-package.yml
.. |PyPI| image:: https://img.shields.io/pypi/v/sanic-ext.svg
   :target: https://pypi.python.org/pypi/sanic-ext/
.. |PyPI version| image:: https://img.shields.io/pypi/pyversions/sanic-ext.svg
   :target: https://pypi.python.org/pypi/sanic-ext/
.. |Code style black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black
.. |Wheel| image:: https://img.shields.io/pypi/wheel/sanic-ext.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/sanic-ext
.. |Supported implementations| image:: https://img.shields.io/pypi/implementation/sanic-ext.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/sanic-ext


.. end-badges


`Sanic <https://github.com/sanic-org/sanic>`_ strives to be "Unopinionated and flexible"::

    Build the way you want to build without letting your tooling constrain you.

But what happens when you want all the goodies? Sanic Extensions is an officially supported Sanic plugin to provide application developers with additional tools and features.

Features
--------

- Auto create HEAD, OPTIONS, and TRACE endpoints
- CORS protection
- Predefined, endpoint-specific response serializers
- Argument injection into route handlers
- OpenAPI documentation with Redoc and/or Swagger
- Request query arguments and body input validation


Installation
------------

::

    pip install sanic[ext]
    # OR
    pip install sanic sanic-ext


Getting started
---------------


.. code-block:: python

    from sanic import Sanic

    app = Sanic("MyHelloWorldApp")
    
Nothing new. Just start using Sanic and it will automatically be extended!


Learn more
----------


Go to the `User Guide <https://sanicframework.org/en/plugins/sanic-ext/getting-started.html>`_ to learn more

____

.. warning:: Sanic Extensions is still in **ALPHA** release. The API is not likely to change. It will move to **BETA** with v22.3.


