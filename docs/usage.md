## Login Manager

First of all, you need to create a `LoginManager` instance.
The login manager manage the `Starlette-Login` behaviour of your `Starlette` instance.

```python
from starlette_login.login_manager import LoginManager

login_manager = LoginManager(redirect_to='/login_endpoint', secret_key=SECRET_KEY)
```

Then you will need to provide a __user loader__ callback function.

```python
from starlette.requests import Request

from model import User

async def get_user_by_id(request: Request, user_id: int):
    # return a sub class of `mixin.UserMixin` instance
    db = request.state.db
    user = await User.get_by_id(db, user_id)
    return user
    

login_manager.set_user_loader(get_user_by_id)
```

## User Class

User class must inherit `UserMixin` class.

```python
from starlette_login.mixins import UserMixin

class User(UserMixin):
    user_id: int
    name: str
    
    def identity(self) -> int:
        return self.user_id

    def display_name(self):
        return self.name
```

## Starlette Application and Middleware

Upon creation of `Starlette` instance, we add `SessionMiddleware` and `AuthenticationMiddleware`.

`SessionMiddleware` is required to manage `http` and `websocket` session.

```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_login.backends import SessionAuthBackend
from starlette_login.middleware import AuthenticationMiddleware

app = Starlette(
    middleware=[
        Middleware(SessionMiddleware, secret_key=SECRET_KEY),
        Middleware(
            AuthenticationMiddleware,
            backend=SessionAuthBackend(login_manager),
            login_manager=login_manager,
            login_route='login',
        )
    ],
    ...
)
```

Then you need to add the `login manager` to `Starlette` instance `state`.

```python
app.state.login_manager = login_manager
```

## Login and Logout

Now that the `Starlette` application instance is ready to use, 
you will need to create a `login` and `logout` route to manage user authentication. 

See `routes.py` on [Basic](index.md) page for `login` and `logout` route example.


## Decorator

`Starlette-Login` Decorator helps to prevent non-authorized user to access certain route.
There are 3 available __decorator__:

- `login_required`: only authenticated user can access the page
- `fresh_login_required`: only _newly logged-in_ user can access the page
- `ws_login_required`: websocket route version of `login_required`

__Usage__

```python
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.websockets import WebSocket
from starlette_login.decorator import login_required, ws_login_required


@login_required
async def protected_page(request: Request):
    return PlainTextResponse(f'You are logged in as {request.user.username}')


@ws_login_required
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("authenticated")
    await websocket.close()
```

See [tests/views.py](https://github.com/jockerz/Starlette-Login/blob/main/tests/views.py) for more decorated routes example.
