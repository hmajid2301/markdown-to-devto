import filecmp
import time

import pytest
import requests

from markdown_to_devto.cli import check_if_we_need_to_rate_limit
from markdown_to_devto.cli import cli


@pytest.mark.parametrize(
    "args, exit_code",
    [
        ([], 2),
        (["--devto-api-key", "AKEY", "-i", "src/"], 1),
        (["--devto-api-key", "AKEY", "--imgur-id", "client-id", "-i", "src/"], 1),
        (["--devto-api-key", "AKEY", "--imgur-id", "client-id", "-m", "README.md"], 2),
        (["--devto-api-key", "AKEY", "--imgur-id", "client-id", "-f", "does_not_example"], 2),
    ],
)
def test_fail_args(runner, args, exit_code):
    result = runner.invoke(cli, args)
    assert result.exit_code == exit_code


@pytest.mark.parametrize(
    "devto_articles, args",
    [
        ([[], []], ["--devto-api-key", "AKEY", "-m", "tests/data/test.md", "-i", "src"]),
        (
            [
                [
                    {
                        "id": "123797",
                        "body_markdown": "---\nchecksum: 7eb95ce783e8896686c88c739cd30ac3\ncover_image: https://cdn-images-1.medium.com/max/1024/0*zoKBYDQXHpqWod1E.png\npublished: false\ntags: ci,react-native,gitlab\ntitle: A Test Message\n---\n\n> Before we dive straight into the CI file itself, let’s do a quicker refresher on some basic concepts. with CI/CD, Git and Gitlab CI.\n\nContinuous Integration (CI), is typically defined as making sure all code being integrated into a codebase works. It usually involves running a set of jobs referred to as a CI pipeline. Some jobs we may run include lintinusuasia tool such as Travis, Circle or even Gitlab.\n\n![a](images/a.png)\n![b](images/b.jpg)",
                        "title": "A Test Message",
                    },
                    {
                        "id": "78979",
                        "body_markdown": "---\nchecksum: dabaaec68730e589699a6006b4a73ce2\ncover_image: https://dev-to-uploads.s3.amazonaws.com/i/w00r4rpmfpjqb8wgygxu.jpg\nlicense: public-domain\ntags:\n- React Native\n- CI\n- GitLab\n- Automation\n- Android\ntitle: Auto Publish React Native App to Android Play Store using GitLab CI\n---\n\nIn this article, I will show you how can automate the publishing of your AAB/APK to the `Google Play Console`.\nWe will be using the [Gradle Play Publisher](https://github.com/Triple-T/gradle-play-publisher) (GPP) plugin to do\nautomate this process for us. Using this plugin we cannot only automate the publishing and release of our app,\nwe can also update the release notes, store listing (including photos) all from GitLab CI. \n\n**Note:** In this article I will assume that you are using Linux and React Native version >= 0.60.\n\n![c](c.jpg)\n![c](c.jpg)\n![c](c.jpg)\n\n---------------------------------------------------------------------------------------------------",
                        "title": "Auto Publish React Native App to Android Play Store using GitLab CI",
                    },
                ],
                [],
            ],
            ["-k", "AKEY", "-f", "tests/data/", "-i", "tests/data/another_folder/"],
        ),
        (
            [
                [
                    {
                        "id": "78979",
                        "body_markdown": "---\nchecksum: dabaaec68730e589699a6006b4a73ce2\ncover_image: https://dev-to-uploads.s3.amazonaws.com/i/w00r4rpmfpjqb8wgygxu.jpg\nlicense: public-domain\ntags:\n- React Native\n- CI\n- GitLab\n- Automation\n- Android\ntitle: Auto Publish React Native App to Android Play Store using GitLab CI\n---\n\nIn this article, I will show you how can automate the publishing of your AAB/APK to the `Google Play Console`.\nWe will be using the [Gradle Play Publisher](https://github.com/Triple-T/gradle-play-publisher) (GPP) plugin to do\nautomate this process for us. Using this plugin we cannot only automate the publishing and release of our app,\nwe can also update the release notes, store listing (including photos) all from GitLab CI. \n\n**Note:** In this article I will assume that you are using Linux and React Native version >= 0.60.\n\n![c](c.jpg)\n![c](c.jpg)\n![c](c.jpg)\n\n---------------------------------------------------------------------------------------------------",
                        "title": "Auto Publish React Native App to Android Play Store using GitLab CI",
                    }
                ],
                [],
            ],
            ["-k", "AKEY", "-f", "tests/data/", "-i", "tests/data/another_folder/", "-a", "my-client-id"],
        ),
        (
            [
                [
                    {
                        "id": "78979",
                        "body_markdown": "---\ncover_image: https://dev-to-uploads.s3.amazonaws.com/i/w00r4rpmfpjqb8wgygxu.jpg\nlicense: public-domain\ntags:\n- React Native\n- CI\n- GitLab\n- Automation\n- Android\ntitle: Auto Publish React Native App to Android Play Store using GitLab CI\n---\n\nIn this article, I will show you how can automate the publishing of your AAB/APK to the `Google Play Console`.\nWe will be using the [Gradle Play Publisher](https://github.com/Triple-T/gradle-play-publisher) (GPP) plugin to do\nautomate this process for us. Using this plugin we cannot only automate the publishing and release of our app,\nwe can also update the release notes, store listing (including photos) all from GitLab CI. \n\n**Note:** In this article I will assume that you are using Linux and React Native version >= 0.60.\n\n![c](c.jpg)\n![c](c.jpg)\n![c](c.jpg)\n\n---------------------------------------------------------------------------------------------------",
                        "title": "Auto Publish React Native App to Android Play Store using GitLab CI",
                    }
                ],
                [],
            ],
            ["-k", "AKEY", "-f", "tests/data/"],
        ),
    ],
)
def test_success(mocker, runner, devto_articles, args):
    result = run_cli(mocker, runner, devto_articles, args)
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "args, output, expected_file",
    [
        (
            ["-k", "AKEY", "-m", "tests/data/another.md", "-o", "tests/data/tmp/"],
            "tests/data/tmp/Auto-Publish-React-Native-App-to-Android-Play-Store-using-GitLab-CI.md",
            "tests/data/expected/another.md",
        ),
    ],
)
def test_output_file(mocker, runner, args, output, expected_file):
    result = run_cli(mocker, runner, [""], args)
    assert result.exit_code == 0
    assert filecmp.cmp(output, expected_file)


def test_dev_to_api_auth_failure_get_articles(mocker, runner):
    args = ["-k", "AKEY", "-f", "tests/data/", "-i", "tests/data/another_folder/"]
    get_mock = mocker.Mock(status_code=401)
    mocker.patch("requests.get", return_value=get_mock)
    result = runner.invoke(cli, args)
    assert result.exit_code == 1


def test_os_error_image_upload(mocker, runner):
    args = ["-k", "AKEY", "-m", "tests/data/another.md", "-i", "tests/data/another_folder/", "-a", "client-id"]
    get_mock = mocker.Mock(status_code=200)
    get_mock.json.side_effect = [[], []]
    mocker.patch("requests.get", return_value=get_mock)
    mocker.patch("builtins.open", side_effect=OSError)

    articles = "---\ncover_image: https://dev-to-uploads.s3.amazonaws.com/i/w00r4rpmfpjqb8wgygxu.jpg\nlicense: public-domain\ntags:\n- React Native\n- CI\n- GitLab\n- Automation\n- Android\ntitle: Auto Publish React Native App to Android Play Store using GitLab CI\n---\n\nIn this article, I will show you how can automate the publishing of your AAB/APK to the `Google Play Console`.\nWe will be using the [Gradle Play Publisher](https://github.com/Triple-T/gradle-play-publisher) (GPP) plugin to do\nautomate this process for us. Using this plugin we cannot only automate the publishing and release of our app,\nwe can also update the release notes, store listing (including photos) all from GitLab CI. \n\n**Note:** In this article I will assume that you are using Linux and React Native version >= 0.60.\n\n![c](c.jpg)\n![c](c.jpg)\n![c](c.jpg)\n\n---------------------------------------------------------------------------------------------------"
    mocker.patch(
        "markdown_to_devto.cli.get_local_articles",
        return_value={"A Test": {"content": articles, "cover_image": "random_image.jpg", "path": "./"}},
    )
    result = runner.invoke(cli, args)
    assert result.exit_code == 0


@pytest.mark.parametrize("status_code", [401, 422, 500, 502])
def test_dev_to_api_failure_upload_articles(mocker, runner, status_code):
    args = ["-k", "AKEY", "-m", "tests/data/example.md"]
    get_mock = mocker.Mock(status_code=200)
    get_mock.json.side_effect = [[], []]
    mocker.patch("requests.get", return_value=get_mock)

    post_mock = mocker.Mock(status_code=status_code)
    mocker.patch("requests.post", return_value=post_mock)
    result = runner.invoke(cli, args)
    assert result.exit_code == 0


@pytest.mark.parametrize("exception", [requests.ConnectionError, requests.ConnectTimeout])
def test_dev_to_api_connection_failure_upload_articles(mocker, runner, exception):
    args = ["-k", "AKEY", "-m", "tests/data/example.md"]
    mocker.patch("requests.get", side_effect=exception)
    result = runner.invoke(cli, args)
    assert result.exit_code == 1


@pytest.mark.parametrize("time_wait", [34.5, 40])
def test_rate_limiting(time_wait):
    articled_uploaded, start = check_if_we_need_to_rate_limit(10, time.time() - time_wait)
    assert articled_uploaded == 0 and type(start) == float


def run_cli(mocker, runner, devto_articles, args):
    get_mock = mocker.Mock(status_code=200)
    get_mock.json.side_effect = devto_articles
    mocker.patch("requests.get", return_value=get_mock)
    create_mock = mocker.Mock(status_code=201)
    mocker.patch("requests.post", return_value=create_mock)
    create_mock.json.return_value = {"data": {"link": "https://imgur.com/123456"}, "url": "random_url.com"}
    mocker.patch("requests.put", return_value=create_mock)
    result = runner.invoke(cli, args)
    return result
