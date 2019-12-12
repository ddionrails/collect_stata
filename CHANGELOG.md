# Changelog

All notable changes to this project will be documented in this file.

## [unreleased]

## [v0.1.0] 2019-12-06

### Added

- use of TypedDicts to improve type hint readability.
- concurrent processing with multiprocessing library.
- VSCode dev container setup.

### Changed

- Bump supported python version from 3.6 to 3.8, to get new typing functionality.
- Internal structure for metadata is now the same as the structure of the output.
- Refactor project; make use of OOP to reduce data flow complexity.

  - Data that was passed a lot between functions
    is now stored as object attributes.

### Fixed

- encoding issues with german umlauts.
- Study flag --study is now a required argument.

## [v0.0.1] 2019-08-23

### Added

- All Scripts for collect_stata

[unreleased]: https://github.com/ddionrails/collect_stata/compare/v0.1.0...develop
[v0.1.0]: https://github.com/ddionrails/collect_stata/releases/tag/v0.1.0
[v0.0.1]: https://github.com/ddionrails/collect_stata/releases/tag/v0.0.1
