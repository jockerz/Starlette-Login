import typing as t

from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Receive, Scope, Send

from .backends import BaseAuthenticationBackend
from .login_manager import LoginManager


class AuthenticationMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        backend: BaseAuthenticationBackend,
        login_manager: LoginManager,
        login_route: str,
        secret_key: str,
        excluded_dirs: t.List[str] = None
    ):
        self.app = app
        self.backend = backend
        self.login_route = login_route
        self.secret_key = secret_key
        self.login_manager = login_manager
        self.excluded_dirs = excluded_dirs or []

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        # Excluded prefix path. E.g. /static
        for prefix_dir in self.excluded_dirs:
            if scope['path'].startswith(prefix_dir):
                await self.app(scope, receive, send)
                return

        conn = HTTPConnection(scope)
        if 'user' not in scope:
            scope['user'] = self.login_manager.anonymous_user_cls()
        elif getattr(scope['user'], 'is_authenticated', False) is True \
                and self.login_manager.config.skip_user:
            await self.app(scope, receive, send)

        user = await self.backend.authenticate(conn)
        if user and user.is_authenticated is True:
            scope['user'] = user

        await self.app(scope, receive, send)
