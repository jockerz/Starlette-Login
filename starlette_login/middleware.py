import typing as t

from starlette.requests import HTTPConnection
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from .backends import BaseAuthenticationBackend
from .login_manager import LoginManager
from .mixins import AnonymousUser


class AuthenticationMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        backends: t.List[BaseAuthenticationBackend],
        login_manager: LoginManager,
        login_route: str,
        secret_key: str,
        excluded_dirs: t.List[str] = None
    ):
        self.app = app
        self.backends = backends or []
        self.login_route = login_route
        self.secret_key = secret_key
        self.excluded_dirs = excluded_dirs or []
        self.immediately = True
        self.login_manager = login_manager

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        # TODO
        # if scope.get('login_skip') is True:
        #     await self.app(scope, receive, send)
        #     return

        for prefix_dir in self.excluded_dirs:
            if scope['path'].startswith(prefix_dir):
                await self.app(scope, receive, send)
                return

        conn = HTTPConnection(scope)
        if 'user' not in scope:
            scope['user'] = AnonymousUser()

        # populate user data
        for backend in self.backends:
            user = await backend.authenticate(conn)
            if user and user.is_authenticated:
                scope['user'] = user
                if self.immediately:
                    await self.app(scope, receive, send)
                    return
        if not scope.get('login_required') is True:
            await self.app(scope, receive, send)
        else:
            response = RedirectResponse(
                conn.url_for(self.login_route), status_code=302
            )
            await response(scope, receive, send)
