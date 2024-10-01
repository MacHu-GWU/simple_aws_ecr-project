
.. image:: https://readthedocs.org/projects/simple-aws-ecr/badge/?version=latest
    :target: https://simple-aws-ecr.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/simple_aws_ecr-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/simple_aws_ecr-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/simple_aws_ecr-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/simple_aws_ecr-project

.. image:: https://img.shields.io/pypi/v/simple-aws-ecr.svg
    :target: https://pypi.python.org/pypi/simple-aws-ecr

.. image:: https://img.shields.io/pypi/l/simple-aws-ecr.svg
    :target: https://pypi.python.org/pypi/simple-aws-ecr

.. image:: https://img.shields.io/pypi/pyversions/simple-aws-ecr.svg
    :target: https://pypi.python.org/pypi/simple-aws-ecr

.. image:: https://img.shields.io/badge/Release_History!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/simple_aws_ecr-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/simple_aws_ecr-project

------

.. image:: https://img.shields.io/badge/Link-Document-blue.svg
    :target: https://simple-aws-ecr.readthedocs.io/en/latest/

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://simple-aws-ecr.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/simple_aws_ecr-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/simple_aws_ecr-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/simple_aws_ecr-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/simple-aws-ecr#files


Welcome to ``simple_aws_ecr`` Documentation
==============================================================================
.. image:: https://simple-aws-ecr.readthedocs.io/en/latest/_static/simple_aws_ecr-logo.png
    :target: https://simple-aws-ecr.readthedocs.io/en/latest/

The aws_ecr project is a comprehensive Python library designed to streamline interactions with Amazon Elastic Container Registry (ECR). It provides a high-level, object-oriented interface for managing ECR repositories, images, and replication rules across multiple AWS accounts. The library offers utility functions for common ECR operations, such as creating repositories, configuring cross-account access, setting up replication, and deploying Lambda functions using ECR images. With support for Docker image building and pushing, cross-account permissions, and efficient error handling, aws_ecr enables developers to easily integrate ECR management into their AWS-based applications and CI/CD pipelines.


.. _install:

Install
------------------------------------------------------------------------------

``simple_aws_ecr`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install simple-aws-ecr

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade simple-aws-ecr
