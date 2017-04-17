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

.. |docs| image:: https://readthedocs.org/projects/aws-buildspec/badge/?style=flat
    :target: https://readthedocs.org/projects/aws-buildspec
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/jonjitsu/aws-buildspec.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/jonjitsu/aws-buildspec

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/jonjitsu/aws-buildspec?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/jonjitsu/aws-buildspec

.. |requires| image:: https://requires.io/github/jonjitsu/aws-buildspec/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/jonjitsu/aws-buildspec/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/jonjitsu/aws-buildspec/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/jonjitsu/aws-buildspec

.. |version| image:: https://img.shields.io/pypi/v/aws-buildspec.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/aws-buildspec

.. |commits-since| image:: https://img.shields.io/github/commits-since/jonjitsu/aws-buildspec/v0.2.0.svg
    :alt: Commits since latest release
    :target: https://github.com/jonjitsu/aws-buildspec/compare/v0.2.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/aws-buildspec.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/aws-buildspec

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/aws-buildspec.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/aws-buildspec

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/aws-buildspec.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/aws-buildspec


.. end-badges

A CodeBuild runner.

* Free software: BSD license

Installation
============

::

    pip install aws-buildspec

Documentation
=============

https://aws-buildspec.readthedocs.io/

Development
===========

To run the all tests run::

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
