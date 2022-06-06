import asyncio
import functools
import inspect
import typing

from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from .utils import create_identifier, make_next_url

LOGIN_MANAGER_ERROR = 'LoginManager is not set'


def is_route_function(func: typing.Callable) -> int:
    # Validate that the function received a Request instance argument
    sig = inspect.signature(func)
    for index_num, parameter in enumerate(sig.parameters.values()):
        if parameter.name == "request":
            return index_num
    else:
        raise Exception(
            f'No "request" argument on function "{func}"'
        )   # pragma: no cover


def login_required(func: typing.Callable) -> typing.Callable:
    idx = is_route_function(func)

    if asyncio.iscoroutinefunction(func):
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
    idx = is_route_function(func)

    if asyncio.iscoroutinefunction(func):
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
