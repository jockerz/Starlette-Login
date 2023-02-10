import typing as t

from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .backends import BaseAuthenticationBackend
from .login_manager import LoginManager


class AuthenticationMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        backend: BaseAuthenticationBackend,
        login_manager: LoginManager,
        excluded_dirs: t.List[str] = None,
        allow_websocket: bool = True,
    ):
        self.app = app
        self.backend = backend
        self.excluded_dirs = excluded_dirs or []
        self.login_manager = login_manager
        self.secret_key = login_manager.secret_key
        self.allow_websocket = allow_websocket

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if self.allow_websocket is False and scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        elif scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        # Excluded prefix path. E.g. /static
        for prefix_dir in self.excluded_dirs:
            if scope["path"].startswith(prefix_dir):
                await self.app(scope, receive, send)
                return

        conn = HTTPConnection(scope=scope, receive=receive)

        user = await self.backend.authenticate(conn)
        if not user or user.is_authenticated is False:
            conn.scope["user"] = self.login_manager.anonymous_user_cls()
        else:
            conn.scope["user"] = user

        async def custom_send(message: Message):
            user_ = conn.scope["user"]
            if user and user_.is_authenticated:
                operation = conn.session.get(
                    self.login_manager.config.REMEMBER_COOKIE_NAME
                )
                if operation == "set":
                    message = self.login_manager.set_cookie(
                        message=message, user_id=user_.identity
                    )
                elif operation == "clear":
                    try:
                        del conn.cookies[self.login_manager.config.COOKIE_NAME]
                    except KeyError:
                        pass
            await send(message)

        await self.app(scope, receive, custom_send)
        return
