import pytest

from .extension import login_manager
from .model import user_list


class TestSessionAuthBackend:
    @pytest.mark.asyncio
    async def test_async_user_loader(self, test_client):
        login_manager.set_user_loader(user_list.async_user_loader)

        resp = test_client.post('/login', data={
            'username': 'user1', 'password': 'password'
        })
        assert resp.status_code == 302
        assert resp.headers['location'] == '/'
