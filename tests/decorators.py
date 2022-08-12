import asyncio
import functools
import typing

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

# Validate that the function received a Request instance argument
from starlette_login.decorator import is_route_function


def admin_only(func: typing.Callable) -> typing.Callable:
    idx = is_route_function(func, "request")

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(
            *args: typing.Any, **kwargs: typing.Any
        ) -> Response:
            request = kwargs.get("request", args[idx] if args else None)
            assert isinstance(request, Request)

            user = request.scope.get("user")
            if user and user.is_admin is not True:
                raise HTTPException(status_code=403, detail="Forbidden access")
            else:
                return await func(*args, **kwargs)

        return async_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args: typing.Any, **kwargs: typing.Any) -> Response:
            request = kwargs.get("request", args[idx] if args else None)
            assert isinstance(request, Request)

            user = request.scope.get("user")
            if user and user.is_admin is not True:
                raise HTTPException(status_code=403, detail="Forbidden access")
            else:
                return func(*args, **kwargs)

        return sync_wrapper
