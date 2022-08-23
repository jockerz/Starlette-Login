**Custom decorator** can be helpful to **filter access** a certain pages on your Web Application.

For usage example we will create a decorator that can only be accessed by `admin` user.

We can add custom decorator that added after `login_required` decorator.

## Admin only Page Decorator

### Introduction

As your Web Application grows, you need to protect some pages for *admin* only.
You can add a filter alike `decorator` for this.

### Codes

!!! warning "Codes below are incomplete"
    Python files below are edit/update of Web Application we created on [Basic page](../index.md).
    Please follow the [Basic page](../index.md) to try codes below.

Edit to **model.py** from [Basic] page.

```python
# ...[skipped]...

@dataclass
class User(BaseUser):
    identifier: int
    username: str
    password: str = 'password'
    is_admin: bool = False       # Added line

    # ...[skipped]...


# ...[skipped]...
# Add new admin user
user_list.add(
    User(identifier=2, username='admin', password='password', is_admin=True)
)
```

Then we add **decorator.py**

```python
import asyncio
import functools
import inspect
import typing

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

# Validate that the function received a Request instance argument
from starlette_login.decorator import is_route_function

from .model import User


def admin_only(func: typing.Callable) -> typing.Callable:
    # HTTP only
    idx = is_route_function(func, "request")

    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(
            *args: typing.Any, **kwargs: typing.Any
        ) -> Response:
            request = kwargs.get("request", args[idx] if args else None)
            assert isinstance(request, Request)

            user = request.scope.get('user')
            if user and user.is_admin is not True:
                raise HTTPException(status_code=403, detail='Forbidden access')
            else:
                return await func(*args, **kwargs)
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args: typing.Any, **kwargs: typing.Any) -> Response:
            request = kwargs.get("request", args[idx] if args else None)
            assert isinstance(request, Request)

            user = request.scope.get('user')
            if user and user.is_admin is not True:
                raise HTTPException(status_code=403, detail='Forbidden access')
            else:
                return func(*args, **kwargs)

        return sync_wrapper
```

Then we edit **routes.py** to add more view routes that is restricted to admin only.

```python
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette_login.decorator import login_required

from .decorator import admin_only


@login_required
@admin_only
async def admin_page(request: Request):
    return PlainTextResponse(
        f'You are an admin and logged in as {request.user.username}'
    )
```

Then we add *the route* to **app.py**.


```python
from starlette.applications import Starlette

# ...[skipped]...

from .routes import admin_page


# ...[skipped]...

app = Starlette(
    # ...[skipped]...
    routes=[
        # ...[skipped]...
        # Add admin only page
        Route('/', admin_page, name='admin'),
    ]
)

# ...[skipped]...
```