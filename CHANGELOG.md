# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://gitlab.com/hmajid2301/markdown-to-devto/-/compare/release%2F0.1.0-beta.1...master
[0.1.0-beta.2]: https://gitlab.com/hmajid2301/markdown-to-devto/-/tags/release%2F0.1.0-beta.1
[0.1.0-beta.1]: https://gitlab.com/hmajid2301/markdown-to-devto/-/tags/release%2F0.1.0-beta.1