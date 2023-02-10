import pytest

from .extension import login_manager
from .model import user_list


@pytest.mark.asyncio
class TestSessionAuthBackend:
    async def test_async_user_loader(self, test_client):
        login_manager.set_user_loader(user_list.async_user_loader)

        resp = test_client.post(
            "/login",
            data={"username": "user1", "password": "password"},
            follow_redirects=False,
        )

        assert resp.status_code == 302
        assert resp.headers["location"] == "/"

    async def test_use_cookies(self, test_client):
        test_client.post(
            "/login",
            data={
                "username": "user1",
                "password": "password",
                "remember": True,
            },
        )

        # clean authentication session
        resp = test_client.get("/request_data")
        resp = test_client.get("/clear")
        assert resp.status_code == 200

        # just after login access
        resp = test_client.get("/request_data")

        assert resp.status_code == 200
        assert "login" not in str(resp.url)
