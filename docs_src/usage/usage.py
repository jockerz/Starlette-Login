from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.websockets import WebSocket
from starlette_login.decorator import login_required, ws_login_required


@login_required
async def protected_page(request: Request):
    return PlainTextResponse(f'You are logged in as {request.user.username}')


@ws_login_required
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("authenticated")
    await websocket.close()
