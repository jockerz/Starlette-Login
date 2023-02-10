class TestApplication:
    def test_home_page_no_login(self, test_client):
        resp = test_client.get("/")
        assert resp.status_code == 200
        assert b"not logged in" in resp.content

    def test_login(self, test_client):
        resp = test_client.get("/login")
        assert resp.status_code == 200

        resp = test_client.post(
            "/login",
            data={"username": "user1", "password": "password"},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert resp.headers["location"] == "/"

    def test_home_page_after_login(self, test_client):
        _ = test_client.post(
            "/login", data={"username": "user1", "password": "password"}
        )

        resp = test_client.get("/")
        assert b"You are logged in as user1" in resp.content

    def test_log_out_without_login(self, test_client):
        resp = test_client.get("/logout", follow_redirects=False)
        assert b"You not logged in" in resp.content

    def test_logout_after_login(self, test_client):
        _ = test_client.post(
            "/login", data={"username": "user1", "password": "password"}
        )

        resp = test_client.get("/logout")
        assert b"Logged out" in resp.content

    def test_protected_page(self, test_client):
        resp = test_client.get("/protected", follow_redirects=False)

        assert resp.status_code == 302
        assert (
            resp.headers.get("location")
            == "http://testserver/login?next=/protected"
        )

    def test_protected_page_after_login(self, test_client):
        _ = test_client.post(
            "/login", data={"username": "user1", "password": "password"}
        )

        resp = test_client.get("/protected")
        assert b"You are logged in as user1" in resp.content
