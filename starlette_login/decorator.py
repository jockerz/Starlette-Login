import asyncio
import functools
import inspect
import typing

from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.websockets import WebSocket

from .utils import create_identifier, make_next_url

LOGIN_MANAGER_ERROR = 'LoginManager is not set'


def login_required(func: typing.Callable) -> typing.Callable:
    sig = inspect.signature(func)
    for idx, parameter in enumerate(sig.parameters.values()):
        if parameter.name == "request" or parameter.name == "websocket":
            break
    else:
        raise Exception(
            f'No "request" or "websocket" argument on function "{func}"'
        )   # pragma: no cover

    if parameter.name == 'websocket':
        @functools.wraps(func)
        async def websocket_wrapper(
            *args: typing.Any, **kwargs: typing.Any
        ) -> None:
            websocket = kwargs.get("websocket", args[idx] if args else None)
            assert isinstance(websocket, WebSocket)

            user = websocket.scope.get('user')
            if not user or getattr(user, 'is_authenticated', False) is False:
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

            login_manager = getattr(request.app.state, 'login_manager', None)
            assert login_manager is not None, LOGIN_MANAGER_ERROR

            if request.method in login_manager.config.EXEMPT_METHODS:
                return await func(*args, **kwargs)    # pragma: no cover

            user = request.scope.get('user')
            if not user or getattr(user, 'is_authenticated', False) is False:
                redirect_url = make_next_url(
                    login_manager.build_redirect_url(request),
                    str(request.url)
                )
                return RedirectResponse(redirect_url, status_code=302)
            else:
                return await func(*args, **kwargs)
        return async_wrapper

    else:
        @functools.wraps(func)
        def sync_wrapper(*args: typing.Any, **kwargs: typing.Any) -> Response:
            request = kwargs.get("request", args[idx] if args else None)
            assert isinstance(request, Request)

            login_manager = getattr(request.app.state, 'login_manager', None)
            assert login_manager is not None, LOGIN_MANAGER_ERROR

            if request.method in login_manager.config.EXEMPT_METHODS:
                return func(*args, **kwargs)    # pragma: no cover

            user = request.scope.get('user')
            if not user or getattr(user, 'is_authenticated', False) is False:
                redirect_url = make_next_url(
                    login_manager.build_redirect_url(request),
                    str(request.url)
                )
                return RedirectResponse(redirect_url, status_code=302)
            else:
                return func(*args, **kwargs)
        return sync_wrapper


def fresh_login_required(func: typing.Callable) -> typing.Callable:
    sig = inspect.signature(func)
    for idx, parameter in enumerate(sig.parameters.values()):
        if parameter.name == "request" or parameter.name == "websocket":
            break
    else:
        raise Exception(
            f'No "request" or "websocket" argument on function "{func}"'
        )   # pragma: no cover

    if parameter.name == 'websocket':
        @functools.wraps(func)
        async def websocket_wrapper(
            *args: typing.Any, **kwargs: typing.Any
        ) -> None:
            websocket = kwargs.get("websocket", args[idx] if args else None)
            assert isinstance(websocket, WebSocket)
            login_manager = getattr(websocket.app.state, 'login_manager', None)
            assert login_manager is not None, LOGIN_MANAGER_ERROR

            session_fresh = login_manager.config.SESSION_NAME_FRESH

            user = websocket.scope.get('user')
            if not user \
                    or getattr(user, 'is_authenticated', False) is False \
                    or websocket.session.get(session_fresh, False) is False:
                websocket.session[
                    login_manager.config.SESSION_NAME_ID
                ] = create_identifier(websocket)
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
            login_manager = getattr(request.app.state, 'login_manager', None)
            assert login_manager is not None, 'LoginManager state is not set'

            if request.method in login_manager.config.EXEMPT_METHODS:
                return await func(*args, **kwargs)    # pragma: no cover

            session_fresh = login_manager.config.SESSION_NAME_FRESH

            user = request.scope.get('user')
            if not user \
                    or getattr(user, 'is_authenticated', False) is False \
                    or request.session.get(session_fresh, False) is False:
                request.session[
                    login_manager.config.SESSION_NAME_ID
                ] = create_identifier(request)

                return RedirectResponse(make_next_url(
                    login_manager.build_redirect_url(request),
                    str(request.url)
                ), status_code=302)
            else:
                return await func(*args, **kwargs)
        return async_wrapper

    else:
        @functools.wraps(func)
        def sync_wrapper(*args: typing.Any, **kwargs: typing.Any) -> Response:
            request = kwargs.get("request", args[idx] if args else None)
            assert isinstance(request, Request)
            login_manager = getattr(request.app.state, 'login_manager', None)
            assert login_manager is not None, 'LoginManager state is not set'

            if request.method in login_manager.config.EXEMPT_METHODS:
                return func(*args, **kwargs)    # pragma: no cover

            session_fresh = login_manager.config.SESSION_NAME_FRESH

            user = request.scope.get('user')
            if not user \
                    or getattr(user, 'is_authenticated', False) is False \
                    or request.session.get(session_fresh, False) is False:
                request.session[
                    login_manager.config.SESSION_NAME_ID
                ] = create_identifier(request)

                return RedirectResponse(make_next_url(
                    login_manager.build_redirect_url(request),
                    str(request.url)
                ), status_code=302)
            else:
                return func(*args, **kwargs)
        return sync_wrapper
