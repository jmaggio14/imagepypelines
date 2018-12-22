# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]
### Changed
  -

## [0.1.4a] - 2018-12-22
### Added
  - Experimental imagepypelines gui to visualize pipeline construction and operation
  - New Unit testing setup involving py.test, coverage.py, and doctest
  - TfBlock: New Block Subclass designed specifically for use with tensorflow
  - more unit tests
  - tools to sample datasets, calculate model accuracy & confidence, etc
  - Pipeline list functionality, insert blocks arbitrarily, delitem, etc


### Changed
  - SimpleImageClassifier now accepts image data, not image filenames
  - Minor bug fixes, Typos
  - made opencv and tensorflow imports inside of separate functions
  - Printer printouts are now sent to stderr, not stdout
