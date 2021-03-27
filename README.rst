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
  -i, --ignore TEXT               Folder to ignore and not publish markdown
                                  files from i.e. .history.
  -o, --output PATH               Where to save the articles after they have
                                  been transformed (the articles will still be
                                  uploaded).
  -s, --site TEXT                 If you're are using the Gatsby plugin to
                                  allow local links between articles. For
                                  dev.to we will need to replace with the link
                                  to your blog.
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
  title: "Auto Publish React Native App to Android Play Store using GitLab CI"
  tags: ["React Native", "CI", "GitLab", "Automation", "Android"]
  license: "public-domain"
  publish: false
  cover_image: https://dev-to-uploads.s3.amazonaws.com/i/w00r4rpmfpjqb8wgygxu.jpg
  ---

  In this article, I will show you how can automate the publishing of your AAB/APK to the `Google Play Console`.
  We will be using the [Gradle Play Publisher](https://github.com/Triple-T/gradle-play-publisher) (GPP) plugin to do
  automate this process for us. Using this plugin we cannot only automate the publishing and release of our app,
  we can also update the release notes, store listing (including photos) all from GitLab CI.

  **Note:** In this article I will assume that you are using Linux and React Native version >= 0.60.

  ![c](c.jpg)
  ![c](c.jpg)
  ![c](c.jpg)

  [My Blog](/blog/storybooks-with-mdx/)

  ```py:title=test.png file=./c.py

  ```

  :::caution Assumption
  This next section assumes that you use Gitlab to host your repos.
  It also assumes that for your Gatsby blog you use Gitlab CI to build/publish it.
  :::

  ---


Other
*****

You can have code block like this:

.. code-block::

  ```py:title=test.png file=./c.py

  ```

Will turn into this:

.. code-block::

  ```py
  import os

  ```


And blocks like will be turned into

.. code-block ::

  :::caution Assumption
  This next section assumes that you use Gitlab to host your repos.
  It also assumes that for your Gatsby blog you use Gitlab CI to build/publish it.
  :::

.. code-block ::

  > This next section assumes that you use Gitlab to host your repos. It also assumes that for your Gatsby blog you use Gitlab CI to build/publish it.


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
