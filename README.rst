.. image:: https://gitlab.com/hmajid2301/markdown-to-devto/badges/master/pipeline.svg
   :target: https://gitlab.com/hmajid2301/markdown-to-devto
   :alt: Pipeline Status

.. image:: https://gitlab.com/hmajid2301/markdown-to-devto/badges/master/coverage.svg
   :target: https://gitlab.com/hmajid2301/markdown-to-devto
   :alt: Coverage

.. image:: https://img.shields.io/pypi/l/markdown-to-devto.svg
   :target: https://pypi.org/project/markdown-to-devto/
   :alt: PyPI Project License

.. image:: https://img.shields.io/pypi/v/markdown-to-devto.svg
   :target: https://pypi.org/project/markdown-to-devto/
   :alt: PyPI Project Version

markdown-to-devto
=================

A CLI tool for publishing markdown articles to dev.to. The tool will also update articles if they already exist
on dev.to. It matches articles based on title in the frontmatter. 

Usage
-----

To use the CLI you will need a `dev.to API Key <https://docs.dev.to/api/#section/Authentication/api_key>`_.
If you want to auto upload your local images to Imgur you need to use the ``-a`` or ``-imgur-id`` and 
enter your `client id  <https://api.imgur.com/oauth2/addclient>`_.

.. code-block:: bash

  pip install markdown-to-devto
  markdown_to_devto --help

Usage: markdown_to_devto [OPTIONS]

  A CLI tool for publish markdown articles to dev.to.

Options:
  -k, --devto-api-key TEXT        Your dev.to API Key.  [required]
  -a, --imgur-id TEXT             If set will auto upload local images on
                                  imgur.
  -m, --file PATH                 The markdown file to publish.
  -f, --folder PATH               Path to folder to publish markdown files
                                  from.
  -i, --ignore PATH               Path to folder to ignore and not publish
                                  markdown files from .history.
  -l, --log-level                 [DEBUG|INFO|ERROR]
                                  Log level for the script.
  --help                          Show this message and exit.

.. code-block:: bash

    $ markdown_to_devto --devto-api-key ATokenAPI --imgur-id ImgurClientId --folder tests/data --ignore another_folder --ignore .history --ignore node_modules

Example Articles
****************

For an article which looks like this; it will first check if any articles exist on your dev.to account using
the title ``Example Document``. The frontmatter includes all the various options you can set.

.. code-block:: 

  ---
  title: Hello, World!
  published: true
  tags: discuss, help
  date: 20190701T10:00Z
  series: Hello series
  canonical_url: https://example.com/blog/hello
  cover_image: article_published_cover_image
  ---

  This is an example document.

  ![c](c.jpg)

GitLab CI
*********

You can use also use this in your CI/CD with the provided Docker image. Below is an example ``.gitlab-ci.yml`` file,
you may wish to use or include. The advantage of this is you can publish your aritcles using CI/CD.

.. code-block:: yaml

  stages:
    - publish

  publish:articles:
    image: registry.gitlab.com/hmajid2301/markdown-to-devto
    stage: publish
    before_script: []
    script:
      - markdown_to_devto --folder tests/data --ignore /tests/data/another_folder

Setup Development Environment
==============================

.. code-block:: bash

  git clone git@gitlab.com:hmajid2301/markdown-to-devto.git
  cd markdown-to-devto
  pip install tox
  make install-venv
  source .venv/bin/activate
  make install-dev

Changelog
=========

You can find the `changelog here <https://gitlab.com/hmajid2301/markdown-to-devto/blob/master/CHANGELOG.md>`_.
