from urllib.parse import parse_qsl

from starlette.requests import Request
from starlette.responses import (
    HTMLResponse, RedirectResponse, PlainTextResponse, JSONResponse
)
from starlette.websockets import WebSocket

from starlette_login.decorator import login_required, fresh_login_required
from starlette_login.utils import login_user, logout_user

from .extension import login_manager
from .model import user_list


HOME_PAGE = "You are logged in as {{ user.username }}"
LOGIN_PAGE = """
<h4>{error}<h4>
<form method="POST">
<label>username <input name="username"></label>
<label>Password <input name="password" type="password"></label>
<button type="submit">Login</button>
</form>
"""


async def login_page(request: Request):
    error = ''
    if request.method == 'POST':
        body = (await request.body()).decode()
        data = dict(parse_qsl(body))
        user = user_list.get_by_username(data['username'])
        if not user:
            error = 'Invalid username'
        elif user.check_password(data['password']) is False:
            error = 'Invalid password'
        else:
            await login_user(request, user, bool(data.get('remember')))
            return RedirectResponse('/', 302)
    return HTMLResponse(LOGIN_PAGE.format(error=error))


async def logout_page(request: Request):
    if request.user.is_authenticated:
        content = 'Logged out'
        await logout_user(request)
    else:
        content = 'You not logged in'
    return PlainTextResponse(content)


async def home_page(request: Request):
    if request.user.is_authenticated:
        content = f'You are logged in as {request.user.username}'
    else:
        content = 'You are not logged in'
    return PlainTextResponse(content=content)


@login_required
async def protected_page(request: Request):
    if getattr(request, 'user') is not None:
        username = request.user.username
    else:
        username = None
    return PlainTextResponse(f'You are logged in as {username}')


@login_required
def sync_protected_page(request: Request):
    return PlainTextResponse(
        f'You are logged in as {request.user.username}'
    )


@login_required
def get_request_data(request: Request):
    return JSONResponse({
        'user': request.user.__dict__,
        'session': request.session,
        'cookie': request.cookies
    })


@fresh_login_required
def sync_fresh_login(request: Request):
    result = {'cookie': request.cookies, 'session': request.session}
    return JSONResponse(result)


@fresh_login_required
async def async_fresh_login(request: Request):
    result = {'cookie': request.cookies, 'session': request.session}
    return JSONResponse(result)


def un_fresh_login(request: Request):
    session_fresh = login_manager.config.SESSION_NAME_FRESH
    request.session[session_fresh] = False
    result = {'cookie': request.cookies, 'session': request.session}
    return JSONResponse(result)


def clear_session(request: Request):
    for key in login_manager.config.session_keys:
        if key == login_manager.config.REMEMBER_COOKIE_NAME:
            continue
        try:
            request.session.pop(key)
        except KeyError:
            pass
    result = {'cookie': request.cookies, 'session': request.session}
    return JSONResponse(result)


async def excluded(request: Request):
    try:
        user = request.user
    except AssertionError:
        # Ignore starlette(`AuthenticationMiddleware`) exception
        user = None

    return JSONResponse({
        'user': getattr(user, 'username', None)
    })


@login_required
async def websocket_protected(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({
        'username': websocket.user.username,
        'session': websocket.session
    })
    await websocket.close()


@fresh_login_required
async def websocket_fresh(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({
        'username': websocket.user.username,
        'session': websocket.session
    })
    await websocket.close()
