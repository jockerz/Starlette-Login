import asyncio
import functools
import inspect
import typing

from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket


def login_required() -> typing.Callable:
    def decorator(func: typing.Callable) -> typing.Callable:
        sig = inspect.signature(func)
        for idx, parameter in enumerate(sig.parameters.values()):
            if parameter.name == "request" or parameter.name == "websocket":
                break
        else:
            raise Exception(
                f'No "request" or "websocket" argument on function "{func}"'
            )

        if type == 'websocket':
            @functools.wraps(func)
            async def websocket_wrapper(
                *args: typing.Any, **kwargs: typing.Any
            ) -> None:
                websocket = kwargs.get("websocket", args[idx] if args else None)
                assert isinstance(websocket, WebSocket)

                websocket.state.login_required = True
                await func(*args, **kwargs)

            return websocket_wrapper
        elif asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(
                *args: typing.Any, **kwargs: typing.Any
            ) -> Response:
                request = kwargs.get("request", args[idx] if args else None)
                assert isinstance(request, Request)

                request.state.login_required = True
                return await func(*args, **kwargs)

            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: typing.Any, **kwargs: typing.Any) -> Response:
                request = kwargs.get("request", args[idx] if args else None)
                assert isinstance(request, Request)

                request.state.login_required = True
                return func(*args, **kwargs)

            return sync_wrapper

    return decorator


def skip_load_user() -> typing.Callable:
    def decorator(func: typing.Callable) -> typing.Callable:
        sig = inspect.signature(func)
        for idx, parameter in enumerate(sig.parameters.values()):
            if parameter.name == "request" or parameter.name == "websocket":
                type_ = parameter.name
                break
        else:
            raise Exception(
                f'No "request" or "websocket" argument on function "{func}"'
            )

        if type == 'websocket':
            @functools.wraps(func)
            async def websocket_wrapper(
                *args: typing.Any, **kwargs: typing.Any
            ) -> None:
                websocket = kwargs.get("websocket", args[idx] if args else None)
                assert isinstance(websocket, WebSocket)

                websocket.state.login_skip = True
                await func(*args, **kwargs)

            return websocket_wrapper
        elif asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(
                *args: typing.Any, **kwargs: typing.Any
            ) -> Response:
                request = kwargs.get("request", args[idx] if args else None)
                assert isinstance(request, Request)

                request.state.login_skip = True
                return await func(*args, **kwargs)

            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: typing.Any, **kwargs: typing.Any) -> Response:
                request = kwargs.get("request", args[idx] if args else None)
                assert isinstance(request, Request)

                request.state.login_skip = True
                return func(*args, **kwargs)

            return sync_wrapper

    return decorator

