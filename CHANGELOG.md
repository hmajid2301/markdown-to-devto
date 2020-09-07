# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Unit tests for python 3.6, 3.7 and 3.8.
- Ability to save file after uploading it.

### Changed
- Various small bugs, such as files not being ignored correctly.

## [0.2.2-beta.1] - 2020-08-19
### Changed
- Tags are converted from "react-native" to "reactnative" so it's compatible with `dev.to`.

## [0.2.1-beta.1] - 2020-05-05
### Fixed
- Don't remove lines from lists.

## [0.2.0-beta.2] - 2020-04-12
### Fixed
- Format error in README hyperlinks.

## [0.2.0-beta.1] - 2020-04-12
### Added
- Log the URL of the article that was changed/updated, fixes #1.

### Changed
- The upload and update HTTP methods now return the response JSON data.

## [0.1.0-beta.3] - 2020-03-13
### Changed
- Ignore folder logic, it checks if the ignore folder is in the path of the article.
- Upload logic into two separate functions.
- Updated the timeout time to 30 seconds.

## [0.1.0-beta.2] - 2020-03-11
### Added
- Log level to args.

### Changed
- Only upload images to Imgur we need to update article on dev.to

### Fixed
- Logger not logging to stdout.
- `query` to `params` in `http_client.py`.

## [0.1.0-beta.1] - 2020-03-10
### Added
- Initial Release.
- Publish images to Imgur and replace local references with new Imgur ones.
- Create/Update articles on dev.to.

[Unreleased]: https://gitlab.com/hmajid2301/markdown-to-devto/-/compare/release%2F0.2.2-beta.1...master
[0.2.2-beta.1]: https://gitlab.com/hmajid2301/markdown-to-devto/-/tags/release%2F0.2.2-beta.1...release%2F0.2.1-beta.1
[0.2.1-beta.1]: https://gitlab.com/hmajid2301/markdown-to-devto/-/tags/release%2F0.2.1-beta.1...release%2F0.2.0-beta.2
[0.2.0-beta.2]: https://gitlab.com/hmajid2301/markdown-to-devto/-/tags/release%2F0.2.0-beta.2...release%2F0.2.0-beta.1
[0.2.0-beta.1]: https://gitlab.com/hmajid2301/markdown-to-devto/-/tags/release%2F0.2.0-beta.1...release%2F0.1.0-beta.3
[0.1.0-beta.3]: https://gitlab.com/hmajid2301/markdown-to-devto/-/tags/release%2F0.1.0-beta.3...release%2F0.1.0-beta.2
[0.1.0-beta.2]: https://gitlab.com/hmajid2301/markdown-to-devto/-/tags/release%2F0.1.0-beta.2...release%2F0.1.0-beta.1
[0.1.0-beta.1]: https://gitlab.com/hmajid2301/markdown-to-devto/-/tags/release%2F0.1.0-beta.1