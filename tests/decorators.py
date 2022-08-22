import asyncio
import functools
import inspect
import typing

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket


def admin_only(func: typing.Callable) -> typing.Callable:
    sig = inspect.signature(func)
    for idx, parameter in enumerate(sig.parameters.values()):
        if parameter.name == "request" or parameter.name == "websocket":
            type_ = parameter.name
            break
    else:
        raise Exception(
            f'No "request" or "websocket" argument on function "{func}"'
        )

    if type_ == "websocket":
        @functools.wraps(func)
        async def websocket_wrapper(
            *args: typing.Any, **kwargs: typing.Any
        ) -> None:
            websocket = kwargs.get(
                "websocket", args[idx] if idx < len(args) else None
            )
            assert isinstance(websocket, WebSocket)

            user = websocket.scope.get("user")
            if user and user.is_admin is not True:
                await websocket.close()
            else:
                await func(*args, **kwargs)

        return websocket_wrapper

    elif asyncio.iscoroutinefunction(func):

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
