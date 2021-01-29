========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/curiousksp/badge/?style=flat
    :target: https://readthedocs.org/projects/curiousksp
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.com/david-wm-sanders/curiousksp.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.com/github/david-wm-sanders/curiousksp

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/david-wm-sanders/curiousksp?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/david-wm-sanders/curiousksp

.. |requires| image:: https://requires.io/github/david-wm-sanders/curiousksp/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/david-wm-sanders/curiousksp/requirements/?branch=master

.. |codecov| image:: https://codecov.io/gh/david-wm-sanders/curiousksp/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/david-wm-sanders/curiousksp

.. |version| image:: https://img.shields.io/pypi/v/curiousksp.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/curiousksp

.. |wheel| image:: https://img.shields.io/pypi/wheel/curiousksp.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/curiousksp

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/curiousksp.svg
    :alt: Supported versions
    :target: https://pypi.org/project/curiousksp

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/curiousksp.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/curiousksp

.. |commits-since| image:: https://img.shields.io/github/commits-since/david-wm-sanders/curiousksp/v0.1.4.svg
    :alt: Commits since latest release
    :target: https://github.com/david-wm-sanders/curiousksp/compare/v0.0.0...master



.. end-badges

ksp chaos with curio coroutines

* Free software: MIT license

Installation
============

::

    pip install curiousksp

You can also install the in-development version with::

    pip install https://github.com/david-wm-sanders/curiousksp/archive/master.zip


Documentation
=============


https://curiousksp.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
