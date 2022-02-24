import asyncio
import functools
import inspect
import typing

from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.websockets import WebSocket

from .login_manager import LoginManager


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

                user = websocket.scope.get('user')
                if getattr(user, 'is_authenticated', False) is False:
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

                user = request.scope.get('user')
                if getattr(user, 'is_authenticated', False) is False:
                    return RedirectResponse(
                        request.url_for('login'), status_code=302
                    )
                else:
                    return await func(*args, **kwargs)
            return async_wrapper

        else:
            @functools.wraps(func)
            def sync_wrapper(*args: typing.Any, **kwargs: typing.Any) -> Response:
                request = kwargs.get("request", args[idx] if args else None)
                assert isinstance(request, Request)

                user = request.scope.get('user')
                if getattr(user, 'is_authenticated', False) is False:
                    return RedirectResponse(
                        request.url_for('login'), status_code=302
                    )
                else:
                    return func(*args, **kwargs)
            return sync_wrapper

    return decorator
