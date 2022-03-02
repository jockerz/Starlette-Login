import typing as t
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

from starlette.requests import HTTPConnection

from .mixins import AnonymousUser


class ProtectionLevel(Enum):
    Basic = 1
    Strong = 2


@dataclass
class Config:
    SESSION_NAME_KEY = '_user_id'
    SESSION_NAME_FRESH = '_fresh'
    SESSION_NAME_ID = '_id'

    REMEMBER_COOKIE_NAME = '_remember'
    REMEMBER_SECONDS_NAME = '_remember_seconds'
    EXEMPT_METHODS = {'OPTIONS'}

    protection_level: t.Optional[ProtectionLevel] = ProtectionLevel.Basic

    remember_cookie_name: str = 'remember_token'
    remember_cookie_domain: t.Optional[str] = None
    remember_cookie_path: str = '/'
    remember_cookie_secure: bool = False
    remember_cookie_httponly: bool = True
    remember_cookie_samesite = None
    remember_cookie_duration: timedelta = timedelta(days=365)

    # Skip backend's `authenticate` method call if user has been
    # loaded to scope
    skip_user: bool = True


class LoginManager:
    _user_loader: t.Callable = None

    # const configuration, should not be changed
    LOGIN_REQUIRED = 'login_required'
    SKIP_LOGIN = 'skip_login'

    def __init__(self, redirect_to: str, config: Config = None):
        self.config = config or Config()
        self.anonymous_user_cls = AnonymousUser
        # Name of redirect view when user need to log in.
        self.redirect_to = redirect_to

    def set_user_loader(self, callback: t.Callable):
        self._user_loader = callback

    @property
    def user_loader(self):
        assert self._user_loader is not None, \
            '`user_loader` is required'
        return self._user_loader

    def build_redirect_url(self, request: HTTPConnection):  # pragma: no cover
        if '/' in self.redirect_to:
            return self.redirect_to
        return request.url_for(self.redirect_to)
