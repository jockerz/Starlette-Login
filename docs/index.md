# Starlette-Login

Repository: [Starlette-Login](https://github.com/jockerz/Starlette-Login)


Starlette-Login provides user session management for Starlette.

Much inspired by [Flask-Login][Flask-Login],
it handles the common tasks of logging in, logging out,
and remembering your users' sessions over extended periods of time.

Key features:

- Store the active user’s ID in the session,
  and let you log them in and out easily.
- Restrict routes to logged-in user only
- Handle "remember-me" functionality


## Installation

Stable
```shell
pip install Starlette-Login
```

Development
```shell
pip install 'git+https://github.com/jockerz/Starlette-Login'
```

## Usage Examples

 - [Basic Auth](https://github.com/jockerz/Starlette-Login-Example/tree/main/basic_auth)
 - Token Auth: *TODO*
 - Multiple Auth: *TODO*


## Usage

**model.py**

User model and how to get the user by `username` and `id`

```python
import typing
from dataclasses import dataclass

from starlette.requests import Request
from starlette_login.mixins import UserMixin


@dataclass
class User(UserMixin):
    identifier: int
    username: str
    password: str = 'password'

    def check_password(self, password: str):
        return self.password == password

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> int:
        return self.identifier


class UserList:
    def __init__(self):
        self.user_list = []

    def dict_username(self) -> dict:
        d = {}
        for user in self.user_list:
            d[user.username] = user
        return d

    def dict_id(self) -> dict:
        d = {}
        for user in self.user_list:
            d[user.identity] = user
        return d

    def add(self, user: User) -> bool:
        if user.identity in self.dict_id():
            return False
        self.user_list.append(user)
        return True

    def get_by_username(self, username: str) -> typing.Optional[User]:
        return self.dict_username().get(username)

    def get_by_id(self, identifier: int) -> typing.Optional[User]:
        return self.dict_id().get(identifier)

    def user_loader(self, request: Request, user_id: int):
        return self.get_by_id(user_id)


user_list = UserList()
user_list.add(User(identifier=1, username='user1', password='password'))
user_list.add(User(identifier=2, username='user2', password='password'))
```

**routes.py**

Implement `login` and `logout` **utils** and `login_required` **decorator**

```python
from urllib.parse import parse_qsl

from starlette.requests import Request
from starlette.responses import (
    RedirectResponse, HTMLResponse, PlainTextResponse
)

from starlette_login.decorator import login_required
from starlette_login.utils import login_user, logout_user

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
    return PlainTextResponse(f'You are logged in as {request.user.username}')
```

**app.py**

Using `AuthenticationMiddleware`, 
then using the `LoginManager` and set `LoginManager`'s `user_loader` 
callback function by `set_user_loader` method.


```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Route

from starlette_login.backends import SessionAuthBackend
from starlette_login.login_manager import LoginManager
from starlette_login.middleware import AuthenticationMiddleware

from .model import user_list
from .routes import home_page, login_page, logout_page, protected_page


login_manager = LoginManager(redirect_to='login')
login_manager.set_user_loader(user_list.user_loader)

app = Starlette(
    middleware=[
        Middleware(SessionMiddleware, secret_key='secret'),
        Middleware(
            AuthenticationMiddleware,
            backend=SessionAuthBackend(login_manager),
            login_manager=login_manager,
            login_route='login',
            secret_key='secret',
        )
    ],

    routes=[
        Route('/', home_page, name='home'),
        Route('/login', login_page, methods=['GET', 'POST'], name='login'),
        Route('/logout', logout_page, name='logout'),
        Route('/protected', protected_page, name='protected'),
    ],
)
app.state.login_manager = login_manager
```

**Run**

```shell
uvicorn app:app
```

[Flask-Login]: https://flask-login.readthedocs.io
