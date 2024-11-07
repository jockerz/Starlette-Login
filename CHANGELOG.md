# Changelog

All notable changes to this project will be documented in this file.

## 1.0.0

- Requires Python `>=3.8`
- Authentication integration with `starlette` update `v>=0.37.x`
- Enhancement of the `starlette` authentication. Thanks to __@abingham__ [4#issuecomment-2242354437](https://github.com/jockerz/Starlette-Login/issues/4#issuecomment-2242354437)


## 0.2.2

## 0.2.0

### Remove

 - Drop Python 3.7 support


## 0.1.9

### Fixed

 - 🔧 Fix logout on remember issue [#1](https://github.com/jockerz/Starlette-Login/pull/1) by [@eykd](https://github.com/eykd)
 - 🔧 Fix `AttributeError: 'URL' object has no attribute 'decode` error 


## 0.1.8

### Updated

 - remove `login_route` on `AuthenticationMiddleware` init method and property

## 0.1.7

### Removed

 - Follows **starlette**, remove support for Python 3.6

## 0.1.6

### Updated

 - Handle session identifier changes

## 0.1.3

### Added

 - Add tutorial on documentation on integrating with SQLAdmin

## 0.1.1

### Fixed

 - Stable version [documentation](https://starlette-login.readthedocs.io/en/stable/).

### Added

 - `is_route_function` function on `decorator.py`

### Updated

 - Add [Custom Decorator](https://starlette-login.readthedocs.io/advance/decorators) on documentation
 - Documentation menu is updated. `/advance` updated to `/custom` and add more relevant pages to `/advance` menu.

## 0.1

- First release

[doc]: https://starlette-login.readthedocs.io/en/latest/
