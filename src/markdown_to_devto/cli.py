# -*- coding: utf-8 -*-
r"""A CLI tool for publishing your markdown articles to dev.to. The tool can also auto upload local images to imgur and
then update the reference to point to these uploaded images.

It uses the title in the frontmatter to determine "uniqueness" of an article. Every time it updates an article it adds
a checksum field. So in future it will only upload an article if the checksums are different i.e. the content has
changed.

The script will wait 3 seconds between publishing articles because the dev.to API rate limits us to only publish 10
articles in 30 seconds. This way we can make sure we don't hit that limit.

Example:
    ::

        $ pip install -e .

.. _Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

"""
import hashlib
import io
import logging
import os
import re
import sys
import time
from pathlib import Path

import click
import frontmatter

from .http_client import HTTPClient
from .utils import exceptions

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--devto-api-key", "-k", required=True, envvar="DEVTO_API_KEY", help="Your dev.to API Key.",
)
@click.option(
    "--imgur-id", "-a", envvar="IMGUR_CLIENT_ID", help="If set will auto upload local images on imgur.",
)
@click.option("--file", "-m", type=click.Path(exists=True), help="The markdown file to publish.")
@click.option("--folder", "-f", type=click.Path(exists=True), help="Path to folder to publish markdown files from.")
@click.option(
    "--ignore",
    "-i",
    type=click.Path(exists=True),
    multiple=True,
    help="Path to folder to ignore and not publish markdown files from .history.",
)
def cli(devto_api_key, imgur_id, file, folder, ignore):
    """A CLI tool for publish markdown articles to dev.to."""
    local_article_paths = get_article_paths(file, folder, ignore)
    articles_to_upload = get_local_articles(local_article_paths)
    http_client = HTTPClient(devto_api_key=devto_api_key, imgur_client_id=imgur_id)

    try:
        devto_articles = http_client.get_articles()
    except exceptions.HTTPException as error:
        logger.error(f"Failed to get articles on dev.to, {error.msg}.")
        sys.exit(1)

    start = time.time()
    articles_uploaded = 0
    for article_title, article_data in articles_to_upload.items():
        devto_article = devto_articles.get(article_title, {})
        logger.info(f"Uploading Article with title {article_title}.")
        try:
            upload_article(article_data, devto_article, http_client)
            articles_uploaded += 1
        except exceptions.HTTPException as error:
            logger.error(f"Failed to upload, {error.msg}.")
        except FileNotFoundError:
            logger.error("Failed to upload file, file doesn't exist.")
        except OSError:
            logger.error("Failed to upload file, file cannot open.")

        articled_uploaded, start = check_if_we_need_to_rate_limit(articles_uploaded, start)


def check_if_we_need_to_rate_limit(articles_uploaded, start):
    """Dev.to only allows us to upload 10 articles every 30 seconds.
    So we check if 10 articles have been uploaded then calculate
    the time elapsed. If less than 30 seconds sleep until 30 seconds
    have elapsed. If we do sleep/wait we can then reset the start time
    and articles_uploaded number.

    We stop for 35 seconds because various actions of the script before
    we start uploading the very first article may taken a bit longer
    than when we start timing.

    Args:
        articles_uploaded (int): Number of articles we have uploaded.
        start (time.time): The time we started uploading articles at.

    Returns:
        tuple: article we have uploaded and start time.

    """

    rate_limit_time = 35
    if articles_uploaded == 10:
        end = time.time()
        time_elapsed = end - start

        if time_elapsed < rate_limit_time:
            time.sleep(rate_limit_time - time_elapsed)

        start = time.time()
        articles_uploaded = 0

    return articles_uploaded, start


def get_article_paths(file, folder, ignore_paths):
    """Gets all the paths to the local markdown article. Either file or folder must be set. If the file is in the
    ignore path it will not be uploaded.

    Args:
        file (str): Path to file.
        folder (str): Path to folder.
        ignore_paths (tuple): A list of paths to ignore markdown files in.

    Returns:
        dict: key is the title of the article and value is details.

    """
    article_paths = []
    if not file and not folder:
        logger.error("File and folder cannot be both be empty.")
        sys.exit(1)
    elif folder:
        for path in Path(folder).rglob("*.md"):
            ignore = should_file_be_ignored(ignore_paths, path)

            if not ignore:
                article_paths.append(path)
    else:
        article_paths = [file]
    return article_paths


def should_file_be_ignored(ignore_paths, path):
    """Checks if file should be ignored or not, based on what list of files/folders
    the user has passed as input.

    Args:
        ignore_paths (tuple): A list of paths to ignore markdown files in.
        path (str): Path to markdown file.

    Returns:
        bool: True if we should ignore the file and it will not be uploaded.

    """
    ignore = False
    for path_to_ignore in ignore_paths:
        normalised_ignore_path = os.path.normpath(path_to_ignore)
        if os.path.commonpath([path_to_ignore, path]) == normalised_ignore_path:
            ignore = True
            break

    return ignore


def get_local_articles(article_paths):
    """Gets all the local markdown files that we will attempt to upload to dev.to.

    Args:
        article_paths (list): List of paths for local articles to upload to dev.to.

    Returns:
        dict: key is the title of the article and value is details.

    """
    logger.info("Getting local articles.")
    articles_data = {}
    for article_path in article_paths:
        article = get_article_data(article_path)
        title = article["title"]
        articles_data[title] = article
        articles_data[title]["path"] = os.path.dirname(article_path)

    return articles_data


def get_article_data(path):
    """Gets the article data, which includes all the fields in the frontmatter as keys/values in a dict.
    We then generate a checksum with the contents of the article (excluding the fronmatter).

    If this article has already been uploaded to dev.to then we can check if the checksum has changed
    if it has not then we don't need to upload the article.

    The checksum is generated now because later on we may make changes to the images using `imgur` links.

    Args:
        path (list): Path of the article file to upload.

    Returns:
        frontmatter.post: key are items in the frontmatter and the contents of the article.

    """
    article = frontmatter.load(path)
    article["content"] = frontmatter.dumps(article)
    checksum = hashlib.md5(article["content"].encode("utf-8")).hexdigest()
    article["checksum"] = checksum
    return article


def upload_article(article, devto_article, http_client):
    """Uploads the article to dev.to. If imgur client id is set,
    it will also auto-upload your images to imgur and change the image links
    in the markdown. As the API doesn't allow you upload images yet.

    If the article exists we will update the article. However we will only update
    the article if the checksums don't match. Else we create the article.

    Everytime we update am article/create one we add a checksum to the frontmatter
    so we can check at a later date if we need to update it.

    Args:
        article (frontmatter.Post): The article you want to upload.
        devto_article (dict): The existing dev.to article (matched using title), if none exists will be an empty dict ({}).
        http_client (HTTPClient): Used to make HTTP requests to dev.to API and also Imgur.

    """
    if http_client.imgur_client_id:
        article["content"] = upload_local_images(article, http_client)

    if devto_article:
        logger.info("Article already exists on dev.to.")
        checksum_matched = check_if_article_requires_update(
            devto_content=devto_article["content"], local_checksum=article["checksum"]
        )

        if not checksum_matched:
            logger.info("Checksum does not match, article needs to be updated on dev.to.")
            article_id = devto_article["id"]
            logger.info("Updating article on dev.to.")
            http_client.update_article(article_id, article)

    else:
        logger.info("Creating article on dev.to.")
        http_client.create_article(article)


def check_if_article_requires_update(devto_content, local_checksum):
    """Gets the checksum for the dev.to article and compares it with the local checksum
    to see if we need to update the article.

    Args:
        devto_article (frontmatter): The existing dev.to article (match using title), if none exists will be an empty dict ({}).
        local_checksum (str): The checksum on the local article we want to upload.


    Returns:
        bool: True if the checksum matched else false.

    """
    devto_file = io.StringIO(devto_content)
    devto_data = frontmatter.load(devto_file)
    try:
        devto_checksum = devto_data["checksum"]
    except KeyError:
        logger.warning(
            "Checksum doesn't exist on article, this likely means article wasn't originally uploaded with this tool."
        )
        devto_checksum = ""

    return devto_checksum == local_checksum


def upload_local_images(article_data, http_client):
    """Will upload all local images to imgur (and cover image). Then update the references
    within the markdown. If the cover image is a local file will also upload the cover image
    and update that as well.

    Args:
        article_data (frontmatter): Article data.
        http_client (HTTPClient): Used to make HTTP requests to Imgur.

    Returns:
        bool: True if the checksum matched else false.

    """

    content, cover_image, article_path = article_data["content"], article_data["cover_image"], article_data["path"]
    logger.info("Uploading images to Imgur.")
    images_in_markdown = re.compile(r"(?:!\[(.*?)\]\((.*?)\))")
    images_in_article = re.findall(images_in_markdown, content)

    for image_markdown in images_in_article:
        description, local_path = image_markdown
        logger.info(f"Uploading image at {local_path}.")
        image_path = os.path.join(article_path, local_path)
        link = http_client.upload_image(image_path)
        old_image_markdown = f"![{description}]({local_path})"
        new_image_markdown = f"![{description}]({link})"
        logger.info(f"Updating path of image in article from {local_path} to {link}.")
        content = content.replace(old_image_markdown, new_image_markdown)

    cover_path = os.path.join(article_path, cover_image)
    if os.path.isfile(cover_path):
        logger.info("Updating article cover image.")
        link = http_client.upload_image(cover_path)
        logger.info(f"Updating path of cover image in article from {cover_image} to {link}.")
        content = content.replace(f"cover_image: {cover_image}", f"cover_image: {link}")

    return content


if __name__ == "__main__":
    cli(sys.argv[1:])
