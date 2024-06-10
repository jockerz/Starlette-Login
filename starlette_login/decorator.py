import asyncio
import functools
import inspect
import typing

from starlette.authentication import AuthCredentials
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.websockets import WebSocket

from .utils import create_identifier, make_next_url

LOGIN_MANAGER_ERROR = "LoginManager is not set"


def is_route_function(func: typing.Callable, param_name: str) -> int:
    # Validate that the function received a Request instance argument
    sig = inspect.signature(func)
    for index_num, parameter in enumerate(sig.parameters.values()):
        if parameter.name == param_name:
            return index_num
    else:
        raise Exception(
            f'No "{param_name}" argument on function "{func}"'
        )  # pragma: no cover


def login_required(func: typing.Callable) -> typing.Callable:
    idx = is_route_function(func, "request")

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(
            *args: typing.Any, **kwargs: typing.Any
        ) -> Response:
            request = kwargs.get("request", args[idx] if args else None)
            assert isinstance(request, Request)

            login_manager = getattr(request.app.state, "login_manager", None)
            assert login_manager is not None, LOGIN_MANAGER_ERROR

            if request.method in login_manager.config.EXEMPT_METHODS:
                return await func(*args, **kwargs)  # pragma: no cover

            user = request.scope.get("user")
            if not user or getattr(user, "is_authenticated", False) is False:
                redirect_url = make_next_url(
                    login_manager.build_redirect_url(request), str(request.url)
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

            login_manager = getattr(request.app.state, "login_manager", None)
            assert login_manager is not None, LOGIN_MANAGER_ERROR

            if request.method in login_manager.config.EXEMPT_METHODS:
                return func(*args, **kwargs)  # pragma: no cover

            user = request.scope.get("user")
            if not user or getattr(user, "is_authenticated", False) is False:
                redirect_url = make_next_url(
                    login_manager.build_redirect_url(request), str(request.url)
                )
                return RedirectResponse(redirect_url, status_code=302)
            else:
                return func(*args, **kwargs)

        return sync_wrapper


def ws_login_required(func: typing.Callable) -> typing.Callable:
    idx = is_route_function(func, "websocket")

    @functools.wraps(func)
    async def async_wrapper(*args: typing.Any, **kwargs: typing.Any):
        websocket = kwargs.get("websocket", args[idx] if args else None)
        assert isinstance(websocket, WebSocket)

        login_manager = getattr(websocket.app.state, "login_manager", None)
        assert login_manager is not None, LOGIN_MANAGER_ERROR

        user = websocket.scope.get("user")
        if not user or getattr(user, "is_authenticated", False) is False:
            await login_manager.ws_not_authenticated(websocket)
        else:
            return await func(*args, **kwargs)

    return async_wrapper


def fresh_login_required(func: typing.Callable) -> typing.Callable:
    idx = is_route_function(func, "request")

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(
            *args: typing.Any, **kwargs: typing.Any
        ) -> Response:
            request = kwargs.get("request", args[idx] if args else None)
            assert isinstance(request, Request)
            login_manager = getattr(request.app.state, "login_manager", None)
            assert login_manager is not None, LOGIN_MANAGER_ERROR

            if request.method in login_manager.config.EXEMPT_METHODS:
                return await func(*args, **kwargs)  # pragma: no cover

            session_fresh = login_manager.config.SESSION_NAME_FRESH

            user = request.scope.get("user")
            if (
                not user
                or getattr(user, "is_authenticated", False) is False
                or request.session.get(session_fresh, False) is False
            ):
                request.session[
                    login_manager.config.SESSION_NAME_ID
                ] = create_identifier(request)

                return RedirectResponse(
                    make_next_url(
                        login_manager.build_redirect_url(request),
                        str(request.url),
                    ),
                    status_code=302,
                )
            else:
                return await func(*args, **kwargs)

        return async_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args: typing.Any, **kwargs: typing.Any) -> Response:
            request = kwargs.get("request", args[idx] if args else None)
            assert isinstance(request, Request)
            login_manager = getattr(request.app.state, "login_manager", None)
            assert login_manager is not None, LOGIN_MANAGER_ERROR

            if request.method in login_manager.config.EXEMPT_METHODS:
                return func(*args, **kwargs)  # pragma: no cover

            session_fresh = login_manager.config.SESSION_NAME_FRESH

            user = request.scope.get("user")
            if (
                not user
                or getattr(user, "is_authenticated", False) is False
                or request.session.get(session_fresh, False) is False
            ):
                request.session[
                    login_manager.config.SESSION_NAME_ID
                ] = create_identifier(request)

                return RedirectResponse(
                    make_next_url(
                        login_manager.build_redirect_url(request),
                        str(request.url),
                    ),
                    status_code=302,
                )
            else:
                return func(*args, **kwargs)

        return sync_wrapper
