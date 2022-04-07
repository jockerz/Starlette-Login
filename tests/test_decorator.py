import pytest


@pytest.mark.asyncio
class TestLoginRequiredDecorator:
    async def test_not_logged_in(self, test_client):
        resp = test_client.get('/protected')
        assert resp.status_code != 302
        assert resp.headers.get('location') != '/'

    async def test_logged_in(self, app, test_client):
        test_client.post('/login', data={
            'username': 'user1', 'password': 'password'
        })

        resp = test_client.get('/protected')
        assert resp.status_code == 200

    async def test_sync_page_not_logged_in(self, test_client):
        resp = test_client.get('/sync_protected')
        assert resp.status_code != 302
        assert resp.headers.get('location') != '/'

    async def test_sync_page_logged_in(self, app, test_client):
        test_client.post('/login', data={
            'username': 'user1', 'password': 'password'
        })

        resp = test_client.get('/sync_protected')
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestFreshLoginRequiredDecorator:
    @pytest.mark.parametrize('path', ['/fresh', '/fresh_async'])
    async def test_fresh_login(self, test_client, path):
        test_client.post('/login', data={
            'username': 'user1', 'password': 'password'
        })

        resp = test_client.get(path)
        assert resp.status_code == 200

    @pytest.mark.parametrize('path', ['/fresh', '/fresh_async'])
    async def test_fresh_login_after_clean_session(
        self, test_client, path
    ):
        test_client.post('/login', data={
            'username': 'user1', 'password': 'password'
        })

        resp = test_client.get(path)
        assert resp.status_code == 200

        # Set fresh session False
        test_client.get('/un_fresh')

        resp = test_client.get(path)
        assert f'/login?next={path}' in resp.url
