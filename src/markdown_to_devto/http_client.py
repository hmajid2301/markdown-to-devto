# -*- coding: utf-8 -*-
r"""A client used to send API requests to dev.to. It can be used to get current articles. It can also be used to
update and create new articles.

Example:
    ::

        $ devto = DevtoClient(api_key=12345678)

.. _Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

"""
import os

import requests

from .utils import exceptions


class HTTPClient:
    def __init__(self, devto_api_key=None, imgur_client_id=None):
        self.devto_api_key = devto_api_key
        self.imgur_client_id = imgur_client_id

    def get_articles(self):
        """Gets all the articles published on dev.to under your account.
        The API uses pagination and only returns 30 articles at a time. So
        we keep querying the API and incrementing the page number until the number
        of articles is less than 30.

        Returns:
            dict: Where the key is the article title and values are the info about the article.

        """
        page = 1
        articles_data = {}

        url = "https://dev.to/api/articles/me/all"
        while True:
            current_articles = self._make_http_request(
                method="get", url=url, params={"page": page, "per_page": 200}, headers={"api-key": self.devto_api_key}
            )
            if not current_articles:
                break

            page += 1
            for article in current_articles:
                title, uid, content = (article["title"], article["id"], article["body_markdown"])
                articles_data[title] = {"id": uid, "content": content}

        return articles_data

    def update_article(self, article_id, article_data):
        """Update an already existing article on dev.to.

        Args:
            article_id (int): The article id on dev.to we are trying to update.
            article_data (dict): The "new" article data we are updating on dev.to, such as content.

        """
        data = {"article": {"body_markdown": article_data["content"]}}
        url = f"https://dev.to/api/articles/{article_id}"
        headers = {"api-key": self.devto_api_key}
        response = self._make_http_request(method="put", url=url, json=data, headers=headers)
        return response

    def create_article(self, article_data):
        """Create a new article on dev.to.

        Args:
            article_data (dict): The article data we are creating on dev.to, such as content.

        """
        data = {"article": {"body_markdown": article_data["content"]}}
        url = "https://dev.to/api/articles"
        headers = {"api-key": self.devto_api_key}
        response = self._make_http_request(method="post", url=url, json=data, headers=headers)
        return response

    def upload_image(self, local_path):
        """Uploads an image to Imgur (as an anonymouse image).

        Args:
            local_path (str): The path to the image you want to upload..

        Returns:
            str: URL on imgur where the image was uploaded.

        """
        url = "https://api.imgur.com/3/upload"
        headers = {"Authorization": f"Client-ID {self.imgur_client_id}"}
        image_path = os.path.join(os.getcwd(), local_path)
        response = self._make_http_request(
            method="post", url=url, headers=headers, files={"image": open(image_path, "rb")}
        )
        link = response["data"]["link"]
        return link

    def _make_http_request(self, method, url, **kwargs):
        """Make a HTTP request to dev.to, for example to.

            - To get articles
            - To update article
            - To create an article

        Args:
            method (str): The HTTP method/verb to use i.e. "post", "get".
            url (str): The URL/endpoint to send the HTTP request to.
            **kwargs: Extra parameters to use with "requests" such as `query` or `json`.

        Raises:
            HTTPConnextionException: When there are connection issues or the request times out.

        """
        http_method = getattr(requests, method)
        try:
            response = http_method(url, timeout=30, **kwargs)
        except (requests.ConnectTimeout, requests.ConnectionError) as e:
            raise exceptions.HTTPConnectionException(msg=e)

        data = response.json()
        self._handle_response(status_code=response.status_code, response_json=data)
        return data

    @staticmethod
    def _handle_response(status_code, response_json):
        """Checks the HTTP response from the dev.to API and raises exceptions if the status code is
        not what we expect.

        Args:
            status_code (int): The HTTP response status code.
            response_json (dict): The response data sent from the dev.to API.

        Raises:
            HTTPBadRequestException: If the API returns a "bad" HTTP response (400, 422).
            HTTPAuthRequestException: If the API returns an auth error HTTP response (401).
            HTTPServerException: If the API returns an server error HTTP response (5xx).

        """
        if status_code in [400, 422]:
            raise exceptions.HTTPBadRequestException(msg=response_json)
        elif status_code == 401:
            raise exceptions.HTTPAuthException(msg=response_json)
        elif status_code not in [200, 201]:
            raise exceptions.HTTPServerException(msg=response_json)
