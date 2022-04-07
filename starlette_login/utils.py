import hmac
import typing
from datetime import timedelta
from hashlib import sha512
from urllib.parse import quote, urlparse, urlunparse

from starlette.requests import Request

from .mixins import UserMixin, AnonymousUser

LOGIN_MANAGER_ERROR = 'LoginManager is not set'


async def login_user(
    request: Request, user: UserMixin, remember: bool = False,
    duration: timedelta = None, fresh: bool = True
) -> bool:
    assert request.scope.get('app') is not None, \
        'Invalid Starlette app'
    login_manager = getattr(request.app.state, 'login_manager', None)
    assert login_manager is not None, LOGIN_MANAGER_ERROR

    login_manager = getattr(request.app.state, 'login_manager', None)
    assert login_manager is not None, LOGIN_MANAGER_ERROR
    assert user.identity is not None, \
        'user identity implementation is required'

    request.session[
        login_manager.config.SESSION_NAME_KEY
    ] = user.identity
    request.session[
        login_manager.config.SESSION_NAME_FRESH
    ] = fresh
    request.session[
        login_manager.config.SESSION_NAME_ID
    ] = create_identifier(request)
    if remember:
        request.session[
            login_manager.config.REMEMBER_COOKIE_NAME
        ] = 'set'
        if duration is not None:
            request.session[
                login_manager.config.REMEMBER_SECONDS_NAME
            ] = duration.total_seconds()
    request.scope['user'] = user
    return True


async def logout_user(request: Request) -> None:
    assert request.scope.get('app') is not None, \
        'Invalid Starlette app'
    login_manager = getattr(request.app.state, 'login_manager', None)
    assert login_manager is not None, LOGIN_MANAGER_ERROR

    session_key = login_manager.config.SESSION_NAME_KEY
    session_fresh = login_manager.config.SESSION_NAME_FRESH
    session_id = login_manager.config.SESSION_NAME_ID
    remember_cookie = login_manager.config.REMEMBER_COOKIE_NAME

    if session_key in request.session:
        request.session.pop(session_key)

    if session_fresh in request.session:
        request.session.pop(session_fresh)

    if session_id in request.session:
        request.session.pop(session_id)

    if remember_cookie in request.cookies:
        request.session[remember_cookie] = 'clear'
        remember_seconds = login_manager.config.REMEMBER_SECONDS_NAME
        if remember_seconds in request.session:
            request.session.pop(remember_seconds)

    request.scope['user'] = AnonymousUser()


def encode_cookie(payload: str, key: str) -> str:
    return f'{payload}|{_cookie_digest(payload, key=key)}'


def decode_cookie(cookie: str, key: str) -> typing.Optional[str]:
    try:
        payload, digest = cookie.rsplit('|', 1)
        if hasattr(digest, 'decode'):
            digest = digest.decode('ascii')
    except ValueError:
        return

    if hmac.compare_digest(_cookie_digest(payload, key=key), digest):
        return payload


def make_next_url(
    redirect_url: str, next_url: str = None
) -> typing.Optional[str]:
    if next_url is None:
        return redirect_url

    r_url = urlparse(redirect_url)
    n_url = urlparse(next_url)

    if (not r_url.scheme or r_url.scheme == n_url.scheme) and \
            (not n_url.netloc or n_url.netloc == n_url.netloc):
        param_next = urlunparse((
            '', '', n_url.path, n_url.params, n_url.query, ''
        ))
    else:
        param_next = next_url

    if param_next:
        param_next = '='.join(('next', quote(param_next)))

    if r_url.query:
        result_url = r_url._replace(query='&'.join((r_url.query, param_next)))
    else:
        result_url = r_url._replace(query=param_next)
    return urlunparse(result_url)


def _get_remote_address(request: Request) -> typing.Optional[str]:
    address = request.headers.get('X-Forwarded-For')
    if address is not None:
        address = address.split(',')[0].strip()
    else:
        client = request.scope.get('client')
        if client is not None:
            address = client[0]
        else:
            address = None
    return address


def create_identifier(request) -> str:
    user_agent = request.headers.get('User-Agent')
    if user_agent is not None:
        user_agent = user_agent.encode('utf-8')
    base = f'{_get_remote_address(request)}|{user_agent}'
    h = sha512()
    h.update(base.encode('utf8'))
    return h.hexdigest()


def _secret_key(secret_key: typing.Union[bytes, str]) -> bytes:
    """ensure bytes"""
    if isinstance(secret_key, str):
        return secret_key.encode('latin1')
    return secret_key


def _cookie_digest(payload: str, key: str) -> str:
    key = _secret_key(key)
    if not isinstance(payload, str):
        payload = str(payload)
    return hmac.new(key, payload.encode('utf-8'), sha512).hexdigest()
