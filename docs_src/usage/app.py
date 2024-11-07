from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_login.backends import SessionAuthBackend
from starlette_login.middleware import AuthenticationMiddleware


app = Starlette(
    middleware=[
        Middleware(SessionMiddleware, secret_key='SECRET_KEY'),
        Middleware(
            AuthenticationMiddleware,
            backend=SessionAuthBackend(login_manager),
            login_manager=login_manager,
            login_route='login',
        )
    ],
    ...
)