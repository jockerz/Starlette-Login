# Login Manager Configuration

## Basic Usage

Custom `configuration` is needed when you need to set custom behavior of `LoginManager`

```python
from datetime import timedelta

from starlette_login.login_manager import (
    Config, LoginManager, ProtectionLevel
)

config = Config(
    SESSION_NAME_FRESH='_fresh',
    SESSION_NAME_ID='_id',
    SESSION_NAME_KEY='_user_id',
    SESSION_NAME_NEXT='next',
    EXEMPT_METHODS=('OPTIONS',),
    protection_level=ProtectionLevel.Basic,
    REMEMBER_COOKIE_NAME='_remember',
    REMEMBER_SECONDS_NAME='_remember_seconds',

    # Cookie configuration
    COOKIE_NAME = 'remember_token',
    COOKIE_DOMAIN=None,
    COOKIE_PATH='/',
    COOKIE_SECURE=False,
    COOKIE_HTTPONLY=True,
    COOKIE_SAMESITE=None,
    COOKIE_DURATION=timedelta(days=365),
)
login_manager = LoginManager(
    redirect_to='login', config=config, secret_key='yoursecretkey'
)
```

## Main Configuration

#### Session Fresh

 - Property name: : `SESSION_NAME_FRESH`
 - Type: `str`
 - Default Value: `'_fresh'`


#### Session ID

 - Property name: : `SESSION_NAME_ID`
 - Type: `str`
 - Default Value: `'_id'`


#### Session Key

 - Property name: : `SESSION_NAME_KEY`
 - Type: `str`
 - Default Value: `'_user_id'`


#### Session Next

 - Property name: : `SESSION_NAME_NEXT`
 - Type: `str`
 - Default Value: `'next'`


#### Excluded HTTP Methods

 - Property name: : `EXEMPT_METHODS`
 - Type: `tuple`
 - Default Value: `{'OPTIONS'}`


#### Cookie Remember

 - Property name: : `REMEMBER_COOKIE_NAME`
 - Type: `str`
 - Default Value: `'_remember'`


#### Cookie Remember Time (seconds)

 - Property name: : `REMEMBER_SECONDS_NAME`
 - Type: `str`
 - Default Value: `'_remember_seconds'`


#### Protection Level

 - Property name: : `protection_level`
 - Type: `ProtectionLevel`
 - Default Value: `ProtectionLevel.Basic`


Usage:

```python
from starlette_login.login_manager import (
    Config, LoginManager, ProtectionLevel
)

config = Config(protection_level=ProtectionLevel.Strong)
login_manager = LoginManager(
    redirect_to='login', config=config, secret_key='yoursecretkey'
)
```

## Cookie Attributes

Documentation: [Cookie - developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)


#### Cookie Name

 - Property name: : `COOKIE_NAME`
 - Type: `str`
 - Default Value: `'remember_token'`


#### Cookie Domain

 - Property name: : `COOKIE_DOMAIN`
 - Type: `typing.Optional[str]`
 - Default Value: `None`


#### Cookie Path

 - Property name: : `COOKIE_PATH`
 - Type: `str`
 - Default Value: `'/'`


#### Cookie Secure

 - Property name: : `COOKIE_SECURE`
 - Type: `bool`
 - Default Value: `False`


#### Cookie HttpOnly

 - Property name: : `COOKIE_HTTPONLY`
 - Type: `bool`
 - Default Value: `True`


#### Cookie SameSite

 - Property name: : `COOKIE_SAMESITE`
 - Type: `str`
 - Default Value: `None`
 - Documentation: [SameSite - developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite)


#### Cookie Duration

 - Property name: : `COOKIE_DURATION`
 - Type: `datetime.timedelta`
 - Default Value: `timedelta(days=365)`
