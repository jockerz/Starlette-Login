import hmac
import typing
from datetime import timedelta
from hashlib import sha512

from starlette.requests import Request

from .configs import SESSION_KEY
from .mixins import UserMixin, AnonymousUser


async def login_user(
    request: Request, user: UserMixin, remember: bool = False,
    duration: timedelta = None, fresh: bool = True
):
    if user.identity is None:
        return False
    request.session[SESSION_KEY] = user.identity
    request.session['_fresh'] = fresh
    request.session['_id'] = _create_identifier(request)
    if remember:
        request.session['_remember'] = 'set'
        if duration is not None:
            request.session['_remember_seconds'] = duration.total_seconds()
    request.scope['user'] = user
    return True


async def logout_user(request: Request):
    request.session.clear()
    if hasattr(request.session, 'regenerate_id'):
        await request.session.regenerate_id()  # type: ignore
    request.scope['user'] = AnonymousUser()


def encode_cookie(payload, key=None):
    return '{0}|{1}'.format(payload, _cookie_digest(payload, key=key))


def decode_cookie(cookie, key=None):
    try:
        payload, digest = cookie.rsplit('|', 1)
        if hasattr(digest, 'decode'):
            digest = digest.decode('ascii')  # pragma: no cover
    except ValueError:
        return

    if hmac.compare_digest(_cookie_digest(payload, key=key), digest):
        return payload


def _get_remote_address(request):
    address = request.headers.get('X-Forwarded-For')
    if address is not None:
        address = address.split(',')[0].strip()
    else:
        address = request.scope.get('client')[0]
    return address


def _create_identifier(request):
    user_agent = request.headers.get('User-Agent')
    if user_agent is not None:
        user_agent = user_agent.encode('utf-8')
    base = f'{_get_remote_address(request)}|{user_agent}'
    h = sha512()
    h.update(base.encode('utf8'))
    return h.hexdigest()


def _secret_key(secret_key: typing.Union[bytes, str]):
    """ensure bytes"""
    if isinstance(secret_key, str):
        return secret_key.encode('latin1')
    return secret_key


def _cookie_digest(payload: str, key: str):
    key = _secret_key(key)
    return hmac.new(key, payload.encode('utf-8'), sha512).hexdigest()


def _update_request_user(request: Request, user: UserMixin = None):
    if user is None:
        user = AnonymousUser()
    request.scope['user'] = user
