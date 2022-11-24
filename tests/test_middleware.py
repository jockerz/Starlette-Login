import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from starlette_login.utils import login_user
from tests.model import user_list


@pytest.mark.asyncio
class TestAuthenticationMiddleware:
    async def test_login_without_middleware_error(self, app):
        async def new_app(scope, receive, send):
            request = Request(scope, receive)
            await login_user(request, user_list.get_by_id(1))
            response = JSONResponse({})
            await response(scope, receive, send)

        http = TestClient(new_app)
        with pytest.raises(AssertionError):
            http.get("/")

    async def test_excluded(self, test_client):
        resp = test_client.get("/excluded")

        assert resp.json()["user"] is None
        assert resp.status_code == 200
        assert list(resp.cookies) == []

    async def test_excluded_logged_in(self, test_client):
        test_client.post(
            "/login", data={"username": "user1", "password": "password"}
        )
        resp = test_client.get("/excluded")

        assert resp.json()["user"] is None
