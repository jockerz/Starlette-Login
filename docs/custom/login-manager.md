# Login Manager

`LoginManager` is where we set the configuration for authentication.

When creating the instance, `redirect_to` and `secret_key` argument must be provided.
This `redirect_to` parameter is url name of __redirect route__ that authentication is 
required error will be redirected to.

`redirect_to` value is either:

 - the complete **route** name that is resolvable by `Request.url_for` method 
 - path if the value contains **`/`** character.

```python
from starlette_login.login_manager import LoginManager

login_manager = LoginManager(redirect_to='login', secret_key='secretkey')
```

The `login_manager` instance is going to be passed to **Starlette** 
application **state**, authentication __Backend__ and __Middleware__.


## Protection Level

There are 2 protection level `Basic` (_default_) and `Strong`.

Protection level will affect session and cookie session 
when __session identifier__ (hash of user-agent and IP address) changed.

When the session is permanent and __protection level__ is `Strong`, 
then the session will simply be marked as non-fresh, 
and anything requiring a fresh login will force the user 
to re-authenticate while `Basic` will only mark 
the current session as non-`fresh`.

If the identifiers do not match in `Strong` mode for a non-permanent session, 
then the entire session (as well as the remember-token if it exists) is deleted.

__Usage__

```python
from starlette_login.login_manager import Config, LoginManager, ProtectionLevel

config = Config(protection_level=ProtectionLevel.Strong)
login_manager = LoginManager(
    redirect_to='login', secret_key='secretkey', config=config
)
```


## User Loader Callback

You need to set up `user loader callback` function to load `user` for authentication session.

__Callback signature__

```python
import typing
from starlette.requests import Request

# async def / def
async def load_user(request: Request, user_id: typing.Any):
    ...
    return user
```

__Usage__

```python
login_manager.set_user_loader(load_user)
```

## Websocket Authentication Error Callback

If you need to send custom message on `ws_login_required` decorated router,
You can call `login_manager.set_ws_not_authenticated` method.

By default, authentication error will __close__ the websocket connection.

__Usage__

```python
from starlette.websockets import WebSocket

async def custom_ws_auth_error(websocket: WebSocket):
    await websocket.send_text('not authenticated')
    await websocket.close()

    
login_manager.set_ws_not_authenticated(custom_ws_auth_error)
```

## Config

You can pass custom configuration to `LoginManager` instance to set custom `cookie` values such as:

 - COOKIE_NAME
 - COOKIE_DURATION
 - COOKIE_PATH
 - COOKIE_DOMAIN
 - COOKIE_SECURE
 - COOKIE_HTTPONLY
 - COOKIE_SAMESITE


See [Configuration](./configuration.md) section for more information.
