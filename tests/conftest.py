from urllib.parse import parse_qsl

import pytest

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import (
    HTMLResponse, RedirectResponse, PlainTextResponse, JSONResponse
)
from starlette.routing import Route, WebSocketRoute
from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from starlette_login.backends import SessionAuthBackend
from starlette_login.decorator import login_required
from starlette_login.middleware import AuthenticationMiddleware
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
    if request.user.is_authenticated:
        return RedirectResponse('/', 302)
    if request.method == 'POST':
        body = (await request.body()).decode()
        data = dict(parse_qsl(body))
        user = user_list.get_by_username(data['username'])
        if not user:
            error = 'Invalid username'
        elif user.check_password(data['password']) is False:
            error = 'Invalid password'
        else:
            await login_user(request, user)
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
    return PlainTextResponse(
        f'You are logged in as {request.user.username}'
    )


@login_required
def sync_protected_page(request: Request):
    return PlainTextResponse(
        f'You are logged in as {request.user.username}'
    )


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
    await websocket.send_json({'username': websocket.user.username})
    await websocket.close()


@pytest.mark.asynctio
@pytest.fixture
async def app():
    application = Starlette(
        debug=True,
        routes=[
            Route('/', home_page, name='home'),
            Route('/login', login_page, methods=['GET', 'POST'], name='login'),
            Route('/logout', logout_page, name='logout'),
            Route('/protected', protected_page, name='protected'),
            Route(
                '/sync_protected', sync_protected_page,
                name='sync_protected_page'
            ),
            Route('/excluded', excluded, name='excluded'),
            WebSocketRoute(
                '/ws_protected', websocket_protected, name='ws_protected'
            )
        ],
        middleware=[
            Middleware(SessionMiddleware, secret_key='secret'),
            Middleware(
                AuthenticationMiddleware,
                backend=SessionAuthBackend(login_manager),
                login_manager=login_manager,
                login_route='login',
                secret_key='secret',
                excluded_dirs=['/excluded']
            )
        ]
    )
    return application


@pytest.fixture
def test_client(app):
    return TestClient(app)
