import pytest

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Route
from starlette.testclient import TestClient

from starlette_login.backends import SessionAuthBackend
from starlette_login.middleware import AuthenticationMiddleware

from .extension import login_manager, x_login_manager
from .views import (
    home_page, login_page, logout_page,
    protected_page, sync_protected_page,
    sync_fresh_login, async_fresh_login,
    un_fresh_login, clear_session,
    excluded, get_request_data,
    admin_only_page
)

routes = [
    Route('/', home_page, name='home'),
    Route('/login', login_page, methods=['GET', 'POST'], name='login'),
    Route('/logout', logout_page, name='logout'),
    Route('/protected', protected_page, name='protected'),
    Route('/fresh', sync_fresh_login, name='sync_fresh_login'),
    Route('/fresh_async', async_fresh_login, name='async_fresh_login'),
    Route('/un_fresh', un_fresh_login, name='un_fresh'),
    Route('/clear', clear_session, name='clear'),
    Route(
        '/sync_protected', sync_protected_page,
        name='sync_protected_page'
    ),
    Route('/excluded', excluded, name='excluded'),
    Route('/request_data', get_request_data, name='req_data'),
    Route('/admin_only', admin_only_page, name='admin_only_page'),
]


@pytest.mark.asynctio
@pytest.fixture
async def app():
    middlewares = [
        Middleware(SessionMiddleware, secret_key='secret'),
        Middleware(
            AuthenticationMiddleware,
            backend=SessionAuthBackend(login_manager),
            login_manager=login_manager,
            login_route='login',
            secret_key='secret',
            excluded_dirs=['/excluded']
        )
    ]
    application = Starlette(
        debug=True, routes=routes, middleware=middlewares
    )
    application.state.login_manager = login_manager
    return application


@pytest.fixture
def test_client(app):
    return TestClient(app)


@pytest.mark.asynctio
@pytest.fixture
async def secure_app():
    middlewares = [
        Middleware(SessionMiddleware, secret_key='secret'),
        Middleware(
            AuthenticationMiddleware,
            backend=SessionAuthBackend(x_login_manager),
            login_manager=x_login_manager,
            login_route='login',
            secret_key='secret',
            excluded_dirs=['/excluded']
        )
    ]
    application = Starlette(
        debug=True, routes=routes, middleware=middlewares
    )
    application.state.login_manager = x_login_manager
    return application


@pytest.fixture
def secure_test_client(secure_app):
    return TestClient(secure_app)
