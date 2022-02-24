from urllib.parse import parse_qsl

import pytest

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import (
    HTMLResponse, RedirectResponse, PlainTextResponse
)
from starlette.routing import Route
from starlette.testclient import TestClient

from starlette_login.backends import SessionAuthBackend
from starlette_login.decorator import login_required
from starlette_login.login_manager import LoginManager
from starlette_login.middleware import AuthenticationMiddleware
from starlette_login.utils import login_user, logout_user

from .model import user_list

login_manager = LoginManager(redirect_to='login')
login_manager.set_user_loader(user_list.user_loader)

HOME_PAGE = """
<p>You are logged in as {{ user.username }}<p>
"""
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
    return HTMLResponse(content)


async def home_page(request: Request):
    if request.user.is_authenticated:
        content = f'You are logged in as {request.user.username}'
    else:
        content = 'You are not logged in'
    return HTMLResponse(content=content)


@login_required()
async def protected_page(request: Request):
    return PlainTextResponse(
        f'You are logged in as {request.user.username}'
    )


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
        ],
        middleware=[
            Middleware(SessionMiddleware, secret_key='secret'),
            Middleware(
                AuthenticationMiddleware,
                backend=SessionAuthBackend(login_manager),
                login_manager=login_manager,
                login_route='login',
                secret_key='secret',
            )
        ]
    )
    return application


@pytest.fixture
def test_client(app):
    return TestClient(app)
