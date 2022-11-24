import pytest
from starlette.websockets import WebSocketDisconnect


@pytest.mark.asyncio
class TestLoginRequiredDecorator:
    async def test_not_logged_in(self, test_client):
        resp = test_client.get("/protected")
        assert resp.status_code != 302
        assert resp.headers.get("location") != "/"

    async def test_logged_in(self, app, test_client):
        test_client.post(
            "/login", data={"username": "user1", "password": "password"}
        )

        resp = test_client.get("/protected")
        assert resp.status_code == 200

    async def test_sync_page_not_logged_in(self, test_client):
        resp = test_client.get("/sync_protected")
        assert resp.status_code != 302
        assert resp.headers.get("location") != "/"

    async def test_sync_page_logged_in(self, app, test_client):
        test_client.post(
            "/login", data={"username": "user1", "password": "password"}
        )

        resp = test_client.get("/sync_protected")
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestFreshLoginRequiredDecorator:
    @pytest.mark.parametrize("path", ["/fresh", "/fresh_async"])
    async def test_fresh_login(self, test_client, path):
        test_client.post(
            "/login", data={"username": "user1", "password": "password"}
        )

        resp = test_client.get(path)
        assert resp.status_code == 200

    @pytest.mark.parametrize("path", ["/fresh", "/fresh_async"])
    async def test_fresh_login_after_clean_session(self, test_client, path):
        test_client.post(
            "/login", data={"username": "user1", "password": "password"}
        )

        resp = test_client.get(path)
        assert resp.status_code == 200

        # Set fresh session False
        test_client.get("/un_fresh")

        resp = test_client.get(path)
        assert f"/login?next={path}" in str(resp.url)


@pytest.mark.asyncio
class TestAdminOnlyDecorator:
    async def test_regular_user(self, test_client):
        test_client.post(
            "/login", data={"username": "user1", "password": "password"}
        )

        path = "/admin_only"
        resp = test_client.get(path)
        assert resp.status_code == 403

    async def test_admin(self, test_client):
        test_client.post(
            "/login", data={"username": "admin", "password": "password"}
        )

        path = "/admin_only"
        resp = test_client.get(path)
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestWebsocketLoginRequiredDecorator:
    url_path = "/ws"

    async def test_not_logged_in(self, test_client):
        with pytest.raises(WebSocketDisconnect):
            with test_client.websocket_connect(self.url_path) as websocket:
                websocket.receive_text()

    async def test_logged_in(self, app, test_client):
        test_client.post(
            "/login", data={"username": "user1", "password": "password"}
        )
        with test_client.websocket_connect(self.url_path) as websocket:
            data = websocket.receive_text()
            user = websocket.scope.get("user")

            assert data == "authenticated"
            assert user is not None


@pytest.mark.asyncio
class TestWebsocketAdminLoginRequiredDecorator:
    url_path = "/ws_admin"

    async def test_regular_user(self, test_client):
        test_client.post(
            self.url_path, data={"username": "user1", "password": "password"}
        )
        with pytest.raises(WebSocketDisconnect):
            with test_client.websocket_connect(self.url_path) as websocket:
                websocket.receive_text()

    async def test_admin(self, test_client):
        test_client.post(
            "/login", data={"username": "admin", "password": "password"}
        )
        with test_client.websocket_connect(self.url_path) as websocket:
            data = websocket.receive_text()
            assert data == "authenticated - admin"
