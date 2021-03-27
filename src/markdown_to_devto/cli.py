__VERSION__ = "0.3.0"

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
import regex

from .http_client import HTTPClient
from .utils import exceptions

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--devto-api-key", "-k", required=True, envvar="DEVTO_API_KEY", help="Your dev.to API Key.")
@click.option("--imgur-id", "-a", envvar="IMGUR_CLIENT_ID", help="If set will auto upload local images on imgur.")
@click.option("--file", "-m", type=click.Path(exists=True), help="The markdown file to publish.")
@click.option("--folder", "-f", type=click.Path(exists=True), help="Path to folder to publish markdown files from.")
@click.option(
    "--ignore", "-i", multiple=True, help="Folder to ignore and not publish markdown files from i.e. .history."
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=True),
    help="Where to save the articles after they have been transformed (the articles will still be uploaded).",
)
@click.option(
    "--site",
    "-s",
    help="If you're are using the Gatsby plugin to allow local links between articles. For dev.to we will need to replace with the link to your blog.",
)
@click.option(
    "--log-level", "-l", default="INFO", type=click.Choice(["DEBUG", "INFO", "ERROR"]), help="Log level for the script."
)
def cli(devto_api_key, imgur_id, file, folder, ignore, output, site, log_level):
    """A CLI tool for publish markdown articles to dev.to."""
    logger.setLevel(log_level)
    local_article_paths = get_article_paths(file, folder, ignore)
    articles_to_upload = get_local_articles(local_article_paths, site)
    http_client = HTTPClient(devto_api_key=devto_api_key, imgur_client_id=imgur_id)

    try:
        devto_articles = http_client.get_articles()
    except exceptions.HTTPException as error:
        logger.error(f"Failed to get articles on dev.to, {error}.")
        sys.exit(1)

    start = time.time()
    articles_uploaded = 0
    for article_title, article_data in articles_to_upload.items():
        devto_article = devto_articles.get(article_title, {})
        logger.info(f"Uploading Article with title {article_title}.")
        try:
            upload_article(article_data, devto_article, http_client)
            if output:
                save_article(output, article_data)
            articles_uploaded += 1
        except exceptions.HTTPException as error:
            logger.error(f"Failed to upload, {error}.")
        except FileNotFoundError as error:
            logger.error(f"Failed to upload file, file doesn't exist, {error}.")
        except OSError as error:
            logger.error(f"Failed to upload file, cannot open file, {error}.")

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


def get_article_paths(file, folder, ignore_folders):
    """Gets all the paths to the local markdown article. Either file or folder must be set. If the file is in the
    ignore path it will not be uploaded.

    Args:
        file (str): Path to file.
        folder (str): Path to folder.
        ignore_folders (tuple): A list of folders to ignore markdown files in.

    Returns:
        dict: key is the title of the article and value is details.

    """
    article_paths = []
    if not file and not folder:
        logger.error("File and folder cannot be both be empty.")
        sys.exit(1)
    elif folder:
        for path in Path(folder).rglob("*.md"):
            ignore = should_file_be_ignored(ignore_folders, path)

            if not ignore:
                article_paths.append(path)
    else:
        article_paths = [file]
    return article_paths


def should_file_be_ignored(ignore_folders, path):
    """Checks if file should be ignored or not, based on what list of files/folders
    the user has passed as input. If the ignore folder name is in the
    path of the article (markdown file) we will ignore it.

    Args:
        ignore_folders (tuple): A list of folders to ignore markdown files in.
        path (str): Path to markdown file.

    Returns:
        bool: True if we should ignore the file and it will not be uploaded.

    """
    ignore = False
    for path_to_ignore in ignore_folders:
        article_dirname = f"{os.path.dirname(path)}/"
        if path_to_ignore in article_dirname:
            ignore = True
            break

    return ignore


def get_local_articles(article_paths, site):
    """Gets all the local markdown files that we will attempt to upload to dev.to.

    Args:
        article_paths (list): List of paths for local articles to upload to dev.to.
        site (str): The site to use to replace local links with.

    Returns:
        dict: key is the title of the article and value is details.

    """
    logger.info("Getting local articles.")
    articles_data = {}
    for article_path in article_paths:
        article = get_article_data(article_path, site)
        title = article["title"]
        articles_data[title] = article
        articles_data[title]["path"] = os.path.dirname(article_path)

    return articles_data


def get_article_data(path, site):
    """Gets the article data, which includes all the fields in the frontmatter as keys/values in a dict.
    We then generate a checksum with the contents of the article (excluding the fronmatter).

    If this article has already been uploaded to dev.to then we can check if the checksum has changed
    if it has not then we don't need to upload the article.

    The checksum is generated now because later on we may make changes to the images using `imgur` links.

    Args:
        path (str): Path of the article file to upload.
        site (str): The site to use to replace local links with.

    Returns:
        frontmatter.post: key are items in the frontmatter and the contents of the article.

    """
    article = frontmatter.load(path)
    article["path"] = str(path)
    article = clean_article_data(article, site, path)
    article_content = frontmatter.dumps(article)
    checksum = hashlib.md5(article_content.encode("utf-8")).hexdigest()
    article["checksum"] = checksum
    return article


def clean_article_data(article, site, path):
    content = article.content
    content = remove_new_lines_in_paragraph(content)
    content = replace_local_links(content, site)
    content = replace_youtube_links(content)
    content = replace_code_meta(content, path)
    content = replace_admonitions(content)

    article["tags"] = convert_tags(article["tags"])
    article["content"] = content
    return article


def convert_tags(tags):
    """Will convert tags so the article can be uploaded to dev.to. This involves removing the `-` and making the tag
    lowercase.

    Args:
        tags (list): The list of tags to convert.

    Returns:
        list: The list of converted tags

    """
    new_tags = []
    for tag in tags:
        converted_tag = tag.replace("-", "").lower()
        new_tags.append(converted_tag)

    return new_tags


def remove_new_lines_in_paragraph(article):
    """When we publish articles to dev.to sometimes the paragraphs don't look very good.
    So we will remove all new lines from paragraphs before we publish them. This means we
    don't have to have very long lines in the document making it easier to edit.

    Some elements we don't want to remove the newlines from, like code blocks or frontmatter.
    So the logic is simple remove new lines from elements except specific ones like code blocks.
    Of course code blocks can span multiple lines so when we see a code block ``` we skip lines
    end until we see end of that code block ```. The same logic applies to all the elements
    we want to ski

    Args:
        article (str): The article we want to publish.

    Returns:
        str: The article with new lines removed from article.

    """
    skip_chars = ["```", "---", "-", "*", "![", ":::"]
    endswith_char = ""

    article_lines = article.split("\n\n")
    for index, line in enumerate(article_lines):
        line_startswith_skip_char = [char for char in skip_chars if line.startswith(char)]

        if line_startswith_skip_char or endswith_char:
            if line_startswith_skip_char:
                endswith_char = line_startswith_skip_char[0]

            if line.endswith(endswith_char):
                endswith_char = ""
            continue

        article_lines[index] = line.replace("\n", " ")

    return "\n\n".join(article_lines)


def replace_local_links(content, site):
    """Replaces a local link with the same link on an external blog. Originally crated because of `gatsby-plugin-catch-links`. Where
    a link like ``[Blog Link](/blog/article-1)`` would get transformed into ``[Blog Link](https://haseebmajid.dev/blog/article-1)``.
    So in case any markdown files link locally we will transform them when on dev.to to link to our blog

    Args:
        content (str): Article data.
        site (str): The site URL i.e. https://haseebmajid.dev, that will be prepended onto local links

    Returns:
        str: The content replacing local links with the external one.

    """
    links_in_markdown = re.compile(r"^\[([\w\s\d]+)\]\(((?:\/|https?:\/\/)[\w\d./?=#]+)\)$")
    links_in_article = re.findall(links_in_markdown, content)

    for link in links_in_article:
        local_link_start = "](/"
        if local_link_start in link:
            local_link_index = link.find("(\\")
            new_website_link = f"{link[:local_link_index + 1]}{site}/{link[local_link_index + 1:]}"
            logger.debug(f"Updating local link {link}, {new_website_link}.")
            content = content.replace(link, new_website_link)

    return content


def replace_youtube_links(content):
    """Replaces a youtube link with the liquid links required for dev.to. Originally crated because of my Gatsby blog.
    For example this would become.

    ::

        `youtube: abcdef`


    To this:

    ::

        {% youtube abcdef %}

    Args:
        content (str): Article data.

    Returns:
        str: The content replacing youtube links with the external one.

    """
    youtube_links_in_markdown = re.compile(r"(?<=`youtube:).*`")
    links_in_article = re.match(youtube_links_in_markdown, content)

    if links_in_article is None:
        links_in_article = []

    for link in links_in_article:
        old_link = f"`youtube: {link}"
        new_link = f"{{% youtube {link.replace('`', '').replace(':', '')} %}}"
        logger.debug(f"Updating youtube link {old_link} with {new_link}.")
        content = content.replace(old_link, new_link)

    return content


def replace_code_meta(content, path):
    """Replaces a code block meta data will the full code block data that dev.to will require. This is for
    users who use `gatsby-remark-import-code` and `gatsby-remark-code-titles` in their markdown files.
    This allows remark to import code from a specified file. However dev.to won't be able to do this for
    us so if we have a code block like this:

    ::

        ```py:title=test.png file=./c.py
        ```

    This will be turned into this:

    ::

        ```py
        import os
        ```

    Args:
        content (str): Article data.
        path (str): The path to the markdown file.

    Returns:
        str: The content replacing code block meta data with normal code block data.

    """
    code_block_in_markdown = re.compile(r"(```[a-z=.:\/ ]*\n[\s\S]*?\n```)")
    code_blocks_in_article = re.findall(code_block_in_markdown, content)

    for code_block in code_blocks_in_article:
        start_code_block = regex.sub("(?<=```[a-z]*):title=.+ ", " ", code_block)
        if start_code_block.startswith("```") and "file=" in start_code_block:
            source_code_path = start_code_block.split("\n")[0].split(" ")[1].replace("file=", "")
            absolute_source_code_path = os.path.join(os.path.dirname(path), source_code_path)
            start_code_block = start_code_block.split(" ")[0]
            logger.debug(f"Importing code block from, {absolute_source_code_path}.")

            try:
                with open(absolute_source_code_path) as code_file:
                    code_contents = code_file.read()
                    new_code_block = f"{start_code_block}\n{code_contents}\n```"
                    content = content.replace(code_block, new_code_block)
            except FileNotFoundError:
                logger.warn(f"File not found at {absolute_source_code_path}")

    return content


def replace_admonitions(content):
    """Replaces admonitions with quote blocks `>`. This allows those who use `gatsby-remark-admonitions` in their
    markdown files, to publish to dev.to without any weird syntax.

    This allows remark to import code from a specified file. However dev.to won't be parse admonitions like we can.

    ::

        :::caution Assumption
        This next section assumes that you use Gitlab to host your repos.
        It also assumes that for your Gatsby blog you use Gitlab CI to build/publish it.
        :::

    This will be turned into this:

    ::

        > This next section assumes that you use Gitlab to host your repos ...

    Args:
        content (str): Article data.

    Returns:
        str: The content replacing admonitions with `>` quote.

    """
    admonintions_in_markdown = re.compile(r":::[\s\S]*?\n:::")
    admonitions_in_article = re.findall(admonintions_in_markdown, content)

    for admonition in admonitions_in_article:
        admonition_content = admonition.split("\n")[1:-1]
        admonition_line = " ".join([line for line in admonition_content])
        quote_line = f"> {admonition_line}"
        content = content.replace(admonition, quote_line)

    return content


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

    if devto_article:
        logger.info("Article already exists on dev.to.")
        checksum_matched = check_if_article_requires_update(
            devto_content=devto_article["content"], local_checksum=article["checksum"]
        )

        if not checksum_matched:
            if http_client.imgur_client_id:
                article["content"] = upload_local_images(article, http_client)

            logger.info("Checksum does not match, article needs to be updated on dev.to.")
            article_id = devto_article["id"]
            response = http_client.update_article(article_id, article)
            logger.info(f"Updating article on dev.to, at {response['url']}")

    else:
        if http_client.imgur_client_id:
            article["content"] = upload_local_images(article, http_client)

        response = http_client.create_article(article)
        logger.info(f"Creating article on dev.to, at {response['url']}")


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
    logger.info("Uploading images to Imgur.")
    content = upload_image_tags(article_data, http_client)
    content = upload_cover_image(article_data, http_client)
    return content


def upload_image_tags(article_data, http_client):
    """Finds all the image tags (with local paths) in the markdown file and uploads them to Imgur. It then replaces
    them with new paths on imgur.

    Args:
        article_data (frontmatter): Article data.
        http_client (HTTPClient): Used to make HTTP requests to Imgur.

    Returns:
        bool: True if the checksum matched else false.

    """
    content, article_path = article_data["content"], article_data["path"]
    images_in_markdown = re.compile(r"(?:!\[(.*?)\]\((.*?)\))")
    images_in_article = re.findall(images_in_markdown, content)

    for image_markdown in images_in_article:
        description, local_path = image_markdown
        image_path = os.path.join(article_path, local_path)
        logger.debug(f"Uploading image at {image_path}.")
        if not os.path.isfile(image_path):
            continue

        link = http_client.upload_image(image_path)
        old_image_markdown = f"![{description}]({local_path})"
        new_image_markdown = f"![{description}]({link})"
        logger.debug(f"Updating path of image in article from {image_path} to {link}.")
        content = content.replace(old_image_markdown, new_image_markdown)

    return content


def upload_cover_image(article_data, http_client):
    """Uploads the cover image if it's a local file in the frontmatter to Imgur. It then replaces the local path
    with new uploaded path.

    Args:
        article_data (frontmatter): Article data.
        http_client (HTTPClient): Used to make HTTP requests to Imgur.

    Returns:
        bool: True if the checksum matched else false.

    """
    content, cover_image, article_path = article_data["content"], article_data["cover_image"], article_data["path"]
    cover_path = os.path.join(article_path, cover_image)

    if os.path.isfile(cover_path):
        logger.debug("Updating article cover image.")
        logger.debug(f"Uploading image at {cover_path}.")
        link = http_client.upload_image(cover_path)
        logger.debug(f"Updating path of cover image in article from {cover_path} to {link}.")
        content = content.replace(f"cover_image: {cover_image}", f"cover_image: {link}")
    return content


def save_article(output, article):
    try:
        article.content = article.metadata["content"]
        del article.metadata["content"]
    except KeyError as e:
        logger.error(f"Missing content in article metadata {e}")
        raise KeyError

    file_name = f"{article.metadata['title'].replace(' ', '-')}.md"
    file_path = os.path.join(output, file_name)
    with open(file_path, "wb") as f:
        try:
            frontmatter.dump(article, f)
        except PermissionError:
            logger.warning(f"Failed to save file at {file_path}.")


if __name__ == "__main__":
    cli(sys.argv[1:])
