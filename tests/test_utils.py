import pytest

from starlette_login.utils import decode_cookie, encode_cookie

SECRET_KEY = "secret"
COOKIE = (
    "1|aaa4e6f2e894c5c79920d71fa547e900c772f1b43b5e9324e4a0021b584c"
    "3a948e104d97c7cf5c114466a9d94ca4893fd13a62a0b3847a88102e917b"
    "f3b2d442"
)


class TestCookieEncoding:
    def test_cookie_encoding(self):
        assert encode_cookie("1", SECRET_KEY) == COOKIE

    def test_cookie_decoding(self):
        assert decode_cookie(COOKIE, SECRET_KEY) == "1"

    def test_cookie_decoding_none(self):
        assert decode_cookie("GOT|NONE", SECRET_KEY) is None


@pytest.mark.asyncio
class TestLogin:
    async def test_login_success(self, test_client):
        resp = test_client.post(
            "/login",
            data={"username": "user1", "password": "password"},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert resp.headers["location"] == "/"

    async def test_logout(self, test_client):
        _ = test_client.post(
            "/login", data={"username": "user1", "password": "password"}
        )
        resp = test_client.get("/protected")
        assert resp.status_code == 200

        _ = test_client.get("/logout")
        resp = test_client.get("/protected", follow_redirects=False)
        assert resp.status_code == 302

    async def test_remember_me(self, test_client):
        _ = test_client.post(
            "/login",
            data={
                "username": "user1",
                "password": "password",
                "remember": True,
            },
        )
        resp = test_client.get("/request_data")
        data = resp.json()

        assert resp.status_code == 200
        assert data["session"]["_remember"] == "set"


@pytest.mark.asyncio
class TestStrongProtection:
    async def test_regular(self, secure_test_client):
        _ = secure_test_client.post(
            "/login",
            data={
                "username": "user1",
                "password": "password",
            },
        )

        resp = secure_test_client.get("/request_data")
        assert resp.status_code == 200
        assert resp.json()

    async def test_identifier_changed(self, secure_test_client):
        _ = secure_test_client.post(
            "/login",
            data={
                "username": "user1",
                "password": "password",
            },
        )

        secure_test_client.headers["user-agent"] = "changed"
        resp = secure_test_client.get("/request_data")

        assert '<button type="submit">Login</button>' in resp.text


@pytest.mark.asyncio
class TestStrongProtectionRememberMe:
    async def test_regular(self, secure_test_client):
        _ = secure_test_client.post(
            "/login",
            data={
                "username": "user1",
                "password": "password",
                "remember": True,
            },
        )

        resp = secure_test_client.get("/request_data")
        data = resp.json()

        assert resp.status_code == 200
        assert data["session"]["_remember"] != "clear"

    async def test_identifier_changed(self, secure_test_client):
        """Client's User-agent or IP data has been changed"""
        _ = secure_test_client.post(
            "/login",
            data={
                "username": "user1",
                "password": "password",
                "remember": True,
            },
        )

        secure_test_client.headers["user-agent"] = "changed"

        resp = secure_test_client.get("/request_data")
        assert resp.status_code == 200
        assert '<button type="submit">Login</button>' in resp.text
