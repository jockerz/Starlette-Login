import json

import pytest
from starlette.websockets import WebSocketDisconnect


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

    async def test_websocket_not_logged_int(self, test_client):
        with pytest.raises(WebSocketDisconnect):
            with test_client.websocket_connect('/ws_protected') as ws:
                data = ws.receive_json()

    async def test_websocket(self, test_client):
        # get auth session
        test_client.post('/login', data={
            'username': 'user1', 'password': 'password'
        })

        with test_client.websocket_connect('/ws_protected') as ws:
            data = ws.receive_json()
            assert data.get('username') == 'user1'

    @pytest.mark.parametrize('path', ['/fresh', '/fresh_async'])
    async def test_fresh_login(self, test_client, path):
        test_client.post('/login', data={
            'username': 'user1', 'password': 'password'
        })

        resp = test_client.get(path)
        assert resp.status_code == 200

        # Set fresh session False
        test_client.get('/un_fresh')

        resp = test_client.get(path)
        assert f'/login?next={path}' in resp.url
