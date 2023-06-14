# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2023-06-14

### Fixed
- Fixed Ledger device enumeration on MAC devices

## [1.2.0] - 2023-05-29

### Changed
- package: Version is not longer hardcoded in sources, but inferred from tag then bundled into the
           package thanks to `setuptools_scm`

## [1.1.2] - 2022-11-21

### Changed

- Fix issue preventing APDU dumps to be displayed in console

## [1.1.1] - 2022-11-10

### Changed

- Fix issue preventing connection to multiple devices via `hid`.

## [1.1.0] - 2020-11-26

### Added

- Specific logger for logging instead of basic one

### Changed

- Keyword parameter for `Transport.send()`: `payload` -> `cdata`

### Fixed

- AttributeError when using CLI `ledgercomm-send`

### Removed

- CLI command `ledgercomm-repl` (for now...)

## [1.0.2] - 2020-10-26

### Changed

- CLI command `ledgercomm-parser` renamed to `ledgercomm-send`

## [1.0.1] - 2020-10-23

### Changed

- Package metadata for PyPi


## [1.0.0] - 2020-10-23

### Added

- First release of ledgercomm on PyPi
