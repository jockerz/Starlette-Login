import typing as t

import anyio
from starlette.middleware.base import (
    BaseHTTPMiddleware, RequestResponseEndpoint
)
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from .backends import BaseAuthenticationBackend
from .login_manager import LoginManager


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        backend: BaseAuthenticationBackend,
        login_manager: LoginManager,
        secret_key: str,
        login_route: str = None,
        excluded_dirs: t.List[str] = None
    ):
        super().__init__(app)
        self.app = app
        self.backend = backend
        self.login_route = login_route
        self.secret_key = secret_key
        self.login_manager = login_manager
        self.excluded_dirs = excluded_dirs or []

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        scope = request.scope
        # Excluded prefix path. E.g. /static
        for prefix_dir in self.excluded_dirs:
            if scope['path'].startswith(prefix_dir):
                response = await call_next(request)
                return response

        user = await self.backend.authenticate(request)
        if not user or user.is_authenticated is False:
            request.scope['user'] = self.login_manager.anonymous_user_cls()
        else:
            request.scope['user'] = user

        response = await call_next(request)

        if user and user.is_authenticated:
            self.login_manager.set_cookie(response, user.identity)

        return response
