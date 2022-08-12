# Securing SQLAdmin

The full code of this tutorial is on [Starlette-Login-Example/sqladmin](https://github.com/jockerz/Starlette-Login-Example/tree/main/sqladmin)


## Introduction

It is a common to have our Web Application to work with Database.
As the application grows we need __admin pages__, 
where we can manage our database data with nice interface is.  

We are going to use [SQLAlchemy][sqlalchemy] for the database 
and [SQLAdmin][sqladmin] for the data management (admin).

Then we need to secure our admin pages that can be accessed by __admin__ only.
For this we are going to use [Starlette-Login][starlette-login].


## Preparation

Python Environment

`requirements.txt`
```text
aiosqlite
jinja2
python-multipart
fastapi
passlib
starlette
uvicorn

Starlette-Login
sqlalchemy[asyncio]
sqladmin
```

```shell
virtualenv -ppython3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## Database Model

This is our `User` model.
We make some `classmethod` method to `get` and `create` user. 

`model.py`
```python
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Boolean, Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from starlette.requests import Request
from starlette_login.mixins import UserMixin


@as_declarative()
class Base:
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class User(Base, UserMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True)
    password = Column(String(128))
    first_name = Column(String(256))
    last_name = Column(String(256))
    is_admin = Column(Boolean, default=False)

    @property
    def identity(self):
        return self.id
    
    @property
    def display_name(self) -> str:
        return ' '.join([self.first_name, self.last_name])

    def set_password(self, password: str):
        self.password = pbkdf2_sha256.hash(password)

    def check_password(self, password: str):
        return pbkdf2_sha256.verify(password, self.password)

    @classmethod
    async def get_user_by_id(cls, request: Request, user_id: int):
        db = request.state.db
        return await db.get(User, user_id)

    @classmethod
    async def get_user_by_username(cls, db: AsyncSession, username: str):
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        if result is None:
            return None
        else:
            return result.scalars().first()

    @classmethod
    async def create_user(
        cls, db: AsyncSession,
        username: str, password: str, first_name: str = None,
        last_name: str = None, is_admin: bool = False
    ):
        user = cls(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_admin=is_admin
        )
        user.set_password(password)
        db.add(user)
        await db.commit()
        return user
```

## Routes

For our basic Web Application, we write routes, namely:

- Login: for login using `username` and `password`
- Logout: End authenticated session
- Home: Home page which can only be accessed by __authenticated user__

`view.py`
```python
from urllib.parse import parse_qsl

from starlette.requests import Request
from starlette.responses import (
    HTMLResponse, PlainTextResponse, RedirectResponse
)
from starlette_login.decorator import login_required
from starlette_login.utils import login_user, logout_user

from model import User


HOME_PAGE = """
You are logged in as {username}<br/>Links:
<ul>
    <li><a href="/">Home</a></li>
    <li><a href="/admin">Admin</a></li>
    <li><a href="/logout">Logout</a></li>
<ul>
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
    db = request.state.db
    error = ''
    if request.method == 'POST':
        body = (await request.body()).decode()
        data = dict(parse_qsl(body))
        username = data.get('username')
        password = data.get('password')

        if username is None or password is None:
            error = "Invalid username or password"
        else:
            user = await User.get_user_by_username(db, username)
            if user:
                if user.check_password(password) is True:
                    await login_user(request, user)
                    return RedirectResponse('/', status_code=302)
                else:
                    error = "Invalid password"
            else:
                error = "User not found"
    return HTMLResponse(LOGIN_PAGE.format(error=error))


async def logout_page(request: Request):
    if request.user.is_authenticated:
        content = 'Logged out'
        await logout_user(request)
    else:
        content = 'You not logged in'
    return PlainTextResponse(content)


@login_required
async def home_page(request: Request):
    user = request.user
    return HTMLResponse(HOME_PAGE.format(username=user.username))
```

## Admin Models

Make `AdminModel` for `User` and make it only accessible by admin.

`admin.py`
```python
from sqladmin import ModelAdmin
from starlette.requests import Request

from model import User


class UserAdmin(ModelAdmin, model=User):
    column_list = [
        User.id, User.username,
        User.first_name, User.last_name,
        User.is_admin
    ]
    form_excluded_columns = [User.password]

    def is_accessible(self, request: Request) -> bool:
        """Restrict access only by admin"""
        user = request.user
        return user and user.is_authenticated and user.is_admin
```

## FastAPI Application

`FastAPI` works well with `Starlette`.
So even we write our `view` function in `Starlette` style, 
it works completely fine.

Now, create main `Application` instance using `FastAPI`

!!! warning "Code snippets below are parts of one file `app.py`."
    Make sure to write as one `app.py` file.

Imports
```python
import logging

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from sqladmin import Admin

from starlette_login.backends import SessionAuthBackend
from starlette_login.login_manager import LoginManager
from starlette_login.middleware import AuthenticationMiddleware

# Admin application instance, model and our previous `view`/`routes`.
from admin import UserAdmin
from model import Base, User
from view import login_page, logout_page, home_page
```

Prepare `Database` (engine and session) and `LoginManager` instance 
and its configuration.

```python
SECRET_KEY = 'our_webapp_secret_key'
DB_URL = 'sqlite+aiosqlite:///./sqlite.db'

logger = logging.getLogger('uvicorn.error')
db_engine = create_async_engine(DB_URL, poolclass=NullPool)
LocalDBSession = sessionmaker(
    db_engine, class_=AsyncSession, expire_on_commit=False
)

login_manager = LoginManager(
    redirect_to='/login', secret_key=SECRET_KEY
)
login_manager.set_user_loader(User.get_user_by_id)
```

Middlewares which required for authentication with `Starlette-Login`.

```python
middleware = [
    Middleware(SessionMiddleware, secret_key=SECRET_KEY),
    Middleware(
        AuthenticationMiddleware,
        backend=SessionAuthBackend(login_manager),
        login_manager=login_manager,
        secret_key=SECRET_KEY,
        excluded_dirs=['/static']
    )
)
```

!!! info "We create two use on `startup` event"
    We do not make `Register` page for registering for simplicity of this totorial.
    Instead Admin user (`admin`) and non-admin user `user`

Main `FastAPI` instance.
```python
app = FastAPI(
    middleware=middleware,
    routes=[
        Route('/', home_page, name='home'),
        Route('/login', login_page, methods=['GET', 'POST'], name='login'),
        Route('/logout', logout_page, name='logout'),
    ]
)
app.state.login_manager = login_manager

@app.middleware('http')
async def extensions(request: Request, call_next):
    try:
        request.state.db = LocalDBSession()
        response = await call_next(request)
    except Exception as exc:
        logger.exception(exc)
        response = PlainTextResponse(f'error: {exc}')
    finally:
        return response


@app.on_event('startup')
async def startup():
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # create admin user
    db = LocalDBSession()
    if not await User.get_user_by_username(db, 'admin'):
        await User.create_user(
            db, 'admin', 'password', is_admin=True
        )
        await User.create_user(
            db, 'user', 'password', is_admin=False
        )
    await db_engine.dispose()
```

`SQLAdmin` instance
```python
# Use `SessionMiddleware` and `AuthenticationMiddleware`
# to secure admin pages
admin = Admin(app, db_engine, middlewares=middleware)
admin.register_model(UserAdmin)
```

Now we can run the code with `uvicorn`

```shell
uvicorn app:app --reload
```

[sqlalchemy]: https://docs.sqlalchemy.org/en/14
[sqladmin]: https://aminalaee.dev/sqladmin
[starlette-login]: https://starlette-login.readthedocs.io
