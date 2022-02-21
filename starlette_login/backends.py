import typing as t

from starlette.requests import HTTPConnection

from .configs import SESSION_KEY
from .login_manager import LoginManager
from .mixins import UserMixin


class BaseAuthenticationBackend:
    name: str = None

    async def authenticate(self, request: HTTPConnection):
        ...


class SessionAuthBackend(BaseAuthenticationBackend):
    name = 'session'

    def __init__(self, login_manager: LoginManager):
        self.login_manager = login_manager

    async def authenticate(
        self, request: HTTPConnection
    ) -> t.Optional[UserMixin]:
        user_id = request.session.get(SESSION_KEY)
        if user_id is None:
            return

        return await self.login_manager.user_loader(request, user_id)
