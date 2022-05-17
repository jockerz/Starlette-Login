import typing as t
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

from starlette.requests import HTTPConnection
from starlette.responses import Response

from .mixins import AnonymousUser
from .utils import decode_cookie, encode_cookie


class ProtectionLevel(Enum):
    Basic = 1
    Strong = 2


@dataclass
class Config:
    SESSION_NAME_FRESH: str = '_fresh'
    SESSION_NAME_ID: str = '_id'
    SESSION_NAME_KEY: str = '_user_id'
    SESSION_NAME_NEXT: str = 'next'

    REMEMBER_COOKIE_NAME: str = '_remember'
    REMEMBER_SECONDS_NAME: str = '_remember_seconds'
    EXEMPT_METHODS: t.Tuple = ('OPTIONS')

    protection_level: t.Optional[ProtectionLevel] = ProtectionLevel.Basic

    # Cookie configuration
    COOKIE_NAME: str = 'remember_token'
    COOKIE_DOMAIN: t.Optional[str] = None
    COOKIE_PATH: str = '/'
    COOKIE_SECURE: bool = False
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: t.Optional[str] = None
    COOKIE_DURATION: timedelta = timedelta(days=365)

    @property
    def session_keys(self):
        return (
            self.SESSION_NAME_FRESH,
            self.SESSION_NAME_ID,
            self.SESSION_NAME_KEY,
            self.SESSION_NAME_NEXT,
            self.REMEMBER_COOKIE_NAME,
            self.REMEMBER_SECONDS_NAME,
        )


class LoginManager:
    _user_loader: t.Callable = None

    def __init__(
        self, redirect_to: str, secret_key: str, config: Config = None
    ):
        self.config = config or Config()
        self.anonymous_user_cls = AnonymousUser
        # Name of redirect view when user need to log in.
        self.redirect_to = redirect_to
        self.secret_key = secret_key

    def set_user_loader(self, callback: t.Callable):
        self._user_loader = callback

    @property
    def user_loader(self):
        assert self._user_loader is not None, \
            '`user_loader` is required'
        return self._user_loader

    def build_redirect_url(self, request: HTTPConnection):
        if '/' in self.redirect_to:
            return self.redirect_to
        return request.url_for(self.redirect_to)

    def protection_is_strong(self):
        return self.config.protection_level == ProtectionLevel.Strong

    def set_cookie(self, response: Response, user_id: t.Any):
        # if not isinstance(user_id, str):
        #     user_id = str(user_id)
        response.set_cookie(
            key=self.config.COOKIE_NAME,
            value=encode_cookie(user_id, self.secret_key),
            expires=int(self.config.COOKIE_DURATION.total_seconds()),
            path=self.config.COOKIE_PATH,
            domain=self.config.COOKIE_DOMAIN,
            secure=self.config.COOKIE_SECURE,
            httponly=self.config.COOKIE_HTTPONLY,
            samesite=self.config.COOKIE_SAMESITE
        )

    def get_cookie(self, cookie: str):
        return decode_cookie(cookie, self.secret_key)
