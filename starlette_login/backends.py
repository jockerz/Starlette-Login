import asyncio
import typing as t

from starlette.requests import HTTPConnection

from .login_manager import LoginManager, ProtectionLevel
from .mixins import UserMixin


class BaseAuthenticationBackend:
    # name: str = None

    async def authenticate(self, request: HTTPConnection):
        ...     # pragma: no cover


class SessionAuthBackend(BaseAuthenticationBackend):
    def __init__(self, login_manager: LoginManager):
        self.login_manager = login_manager

    async def authenticate(
        self, request: HTTPConnection
    ) -> t.Optional[UserMixin]:
        # Load user from session
        session_key = self.login_manager.config.SESSION_NAME_KEY
        user_id = request.session.get(session_key)

        # Using Strong protection
        if self.login_manager.protection_is_strong():
            for key in self.login_manager.config.session_keys:
                try:
                    request.session.pop(key)
                except KeyError:
                    pass
            request.session[
                self.login_manager.config.REMEMBER_COOKIE_NAME
            ] = 'clear'
        else:
            request.session[
                self.login_manager.config.SESSION_NAME_FRESH
            ] = False

        if user_id is None and request.session.get(
            self.login_manager.config.REMEMBER_COOKIE_NAME, 'clear'
        ) != 'clear':
            cookie = request.cookies.get(
                self.login_manager.config.COOKIE_NAME
            )
            if cookie:
                user_id = self.login_manager.get_cookie(cookie)
                user_id = int(user_id)
                request.session[
                    self.login_manager.config.SESSION_NAME_FRESH
                ] = False

        if user_id is None:
            return
        elif asyncio.iscoroutinefunction(self.login_manager.user_loader):
            user = await self.login_manager.user_loader(request, user_id)
        else:
            user = self.login_manager.user_loader(request, user_id)

        if user is not None:
            return user
