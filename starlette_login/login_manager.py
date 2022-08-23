import http.cookies
import typing as t
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

from starlette.datastructures import MutableHeaders
from starlette.requests import HTTPConnection
from starlette.types import Message
from starlette.websockets import WebSocket

from .mixins import AnonymousUser, UserMixin
from .utils import decode_cookie, encode_cookie

WebsocketAuthFailCallback = t.Callable[[WebSocket], t.Awaitable[None]]


class ProtectionLevel(Enum):
    Basic = 1
    Strong = 2


@dataclass
class Config:
    SESSION_NAME_FRESH: str = "_fresh"
    SESSION_NAME_ID: str = "_id"
    SESSION_NAME_KEY: str = "_user_id"
    SESSION_NAME_NEXT: str = "next"
    REMEMBER_COOKIE_NAME: str = "_remember"
    REMEMBER_SECONDS_NAME: str = "_remember_seconds"
    EXEMPT_METHODS: t.Tuple[str] = ("OPTIONS",)

    protection_level: t.Optional[ProtectionLevel] = ProtectionLevel.Basic

    # Cookie configuration
    COOKIE_NAME: str = "remember_token"
    COOKIE_DOMAIN: t.Optional[str] = None
    COOKIE_PATH: str = "/"
    COOKIE_SECURE: bool = False
    COOKIE_HTTPONLY: bool = True
    # Not supported on python 3.6 and 3.7
    # COOKIE_SAMESITE: t.Optional[t.Literal["lax", "strict", "none"]] = None
    COOKIE_SAMESITE: t.Optional[str] = None
    COOKIE_DURATION: timedelta = timedelta(days=365)

    @property
    def session_keys(self) -> t.Tuple[str, str, str, str, str, str]:
        return (
            self.SESSION_NAME_FRESH,
            self.SESSION_NAME_ID,
            self.SESSION_NAME_KEY,
            self.SESSION_NAME_NEXT,
            self.REMEMBER_COOKIE_NAME,
            self.REMEMBER_SECONDS_NAME,
        )


class LoginManager:
    def __init__(
        self, redirect_to: str, secret_key: str, config: Config = None
    ):
        self.config = config or Config()
        self.anonymous_user_cls = AnonymousUser
        # Name of redirect view when user need to log in.
        self.redirect_to = redirect_to
        self.secret_key = secret_key

        self._user_loader: t.Optional[t.Callable[..., UserMixin]] = None
        # Custom not authenticated callback for websocket
        self._ws_auth_fail_func: t.Optional[WebsocketAuthFailCallback] = None

    def set_user_loader(self, callback: t.Callable[..., UserMixin]):
        """Set custom user loader"""
        self._user_loader = callback

    def set_ws_not_authenticated(self, callback: WebsocketAuthFailCallback):
        """Set not authenticated callback for websocket"""
        self._ws_auth_fail_func = callback

    async def ws_not_authenticated(self, websocket: WebSocket):
        if self._ws_auth_fail_func is None:
            await websocket.close()
        else:
            await self._ws_auth_fail_func(websocket)

    @property
    def user_loader(self):
        assert self._user_loader is not None, "`user_loader` is required"
        return self._user_loader

    def build_redirect_url(self, request: HTTPConnection):
        if "/" in self.redirect_to:
            return self.redirect_to
        return request.url_for(self.redirect_to)

    def protection_is_strong(self):
        return self.config.protection_level == ProtectionLevel.Strong

    def set_cookie(self, message: Message, user_id: t.Any) -> Message:
        key = self.config.COOKIE_NAME
        value = encode_cookie(user_id, self.secret_key)
        expires = int(self.config.COOKIE_DURATION.total_seconds())
        path = self.config.COOKIE_PATH
        domain = self.config.COOKIE_DOMAIN
        secure = self.config.COOKIE_SECURE
        httponly = self.config.COOKIE_HTTPONLY
        samesite = self.config.COOKIE_SAMESITE

        message.setdefault("headers", [])
        headers = MutableHeaders(scope=message)
        cookie: "http.cookies.BaseCookie[str]" = http.cookies.SimpleCookie()

        cookie[key] = value
        if expires is not None:
            cookie[key]["expires"] = expires
        if path is not None:
            cookie[key]["path"] = path
        if domain is not None:
            cookie[key]["domain"] = domain
        if secure:
            cookie[key]["secure"] = True
        if httponly:
            cookie[key]["httponly"] = True
        if samesite is not None:
            assert samesite.lower() in [
                "strict",
                "lax",
                "none",
            ], "samesite must be either 'strict', 'lax' or 'none'"
            cookie[key]["samesite"] = samesite

        headers['set-cookie'] = cookie.output(header="").strip()
        return message

    def get_cookie(self, cookie: str):
        return decode_cookie(cookie, self.secret_key)
