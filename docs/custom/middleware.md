# Middlewares

## `AuthenticationMiddleware`

!!! warning
    Before `AuthenticationMiddleware`,
    Starlette's [`SessionMiddleware`](https://starlette.dev/middleware/#sessionmiddleware) is required to help managing http and websocket session.


### `excluded_dir` (`list[str]`)

For basic web application, which often serve static files like CSS and javascript files.
These endpoints might be need to be excluded from the **authentication process**.


### `allow_websocket` (`bool`)

If `allow_websocket` value is `False`, all websocket endpoints will be excluded.  


### Usage Example

```py
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_login.backends import SessionAuthBackend
from starlette_login.middleware import AuthenticationMiddleware

login_manager = ...
app = Starlette(
    middleware=[
        Middleware(SessionMiddleware, secret_key='SECRET_KEY'),
        Middleware(
            AuthenticationMiddleware,
            backend=SessionAuthBackend(login_manager),
            login_manager=login_manager,
            excluded_dir=['/statics', '/favicon.ico'],
            allow_websocket=False
        )
    ],
    ...
)
```

!!! warning
    `request.user` call on excluded path will lead to 
    `AssertionError: AuthenticationMiddleware must be installed to access request.user` error.
    This exception raised by `starlette`.
    
    The authentication middleware is ignoring the excluded path and `request.user` is not being set.


[starlette]: https://starlette.dev