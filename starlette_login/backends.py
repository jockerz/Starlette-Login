import asyncio
import typing as t

from starlette.requests import HTTPConnection

from .login_manager import LoginManager
from .mixins import UserMixin


class BaseAuthenticationBackend:
    # name: str = None

    async def authenticate(self, request: HTTPConnection):
        ...  # pragma: no cover


class SessionAuthBackend(BaseAuthenticationBackend):
    def __init__(self, login_manager: LoginManager):
        self.login_manager = login_manager

    async def authenticate(
        self, conn: HTTPConnection
    ) -> t.Optional[UserMixin]:
        # Load user from session
        session_key = self.login_manager.config.SESSION_NAME_KEY
        user_id = conn.session.get(session_key)

        remember_cookie = self.login_manager.config.REMEMBER_COOKIE_NAME
        session_fresh = self.login_manager.config.SESSION_NAME_FRESH

        # Using Strong protection
        if self.login_manager.protection_is_strong():
            for key in self.login_manager.config.session_keys:
                try:
                    conn.session.pop(key)
                except KeyError:
                    pass
            conn.session[remember_cookie] = "clear"
        else:
            conn.session[session_fresh] = False

        if (
            user_id is None
            and conn.session.get(remember_cookie, "clear") != "clear"
        ):
            cookie = conn.cookies.get(self.login_manager.config.COOKIE_NAME)
            if cookie:
                user_id = self.login_manager.get_cookie(cookie)
                user_id = int(user_id)
                conn.session[session_fresh] = False

        if user_id is None:
            return None
        elif asyncio.iscoroutinefunction(self.login_manager.user_loader):
            user = await self.login_manager.user_loader(conn, user_id)
        else:
            user = self.login_manager.user_loader(conn, user_id)
        return user
