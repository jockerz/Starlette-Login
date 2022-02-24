import hmac
import typing
from datetime import timedelta
from hashlib import sha512
from urllib.parse import quote, urlparse, urlunparse

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


def make_next_url(redirect_url: str, next_url: str = None):
    if next_url is None:
        return redirect_url
    
    r_url = urlparse(redirect_url)
    n_url = urlparse(next_url)

    if (not r_url.scheme or r_url.scheme == n_url.scheme) and \
            (not n_url.netloc or n_url.netloc == n_url.netloc):
        param_next = urlunparse(('', '', n_url.path, n_url.params, n_url.query, ''))
    else:
        param_next = next_url

    if param_next:
        param_next = '='.join(('next', quote(param_next)))

    if r_url.query:
        result_url = r_url._replace(query='&'.join((r_url.query, param_next)))
    else:
        result_url = r_url._replace(query=param_next)
    return urlunparse(result_url)
