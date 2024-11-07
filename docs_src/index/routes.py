from urllib.parse import parse_qsl

from starlette.requests import Request
from starlette.responses import (
    RedirectResponse, HTMLResponse, PlainTextResponse
)

from starlette_login.decorator import login_required
from starlette_login.utils import login_user, logout_user

from models import user_list


HOME_PAGE = "You are logged in as <strong>{username}</strong>"
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
        content = HOME_PAGE.format(username=request.user.username)
    else:
        content = 'You are not logged in'
    return HTMLResponse(content=content)


@login_required
async def protected_page(request: Request):
    return PlainTextResponse(f'You are logged in as {request.user.username}')
