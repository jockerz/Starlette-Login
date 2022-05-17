# Login Manager

`LoginManager` is where we set the configuration for authentication.

Upon creating the instance, `redirect_to` property must be provided.
This property is url name of __redirect route__ that authentication is 
required error redirected to.

`redirect_to` value is either:

 - the complete **route** name that is resolvable by `Request.url_for` method 
 - path if the value contains **`/`** character.

```python
from starlette_login.login_manager import LoginManager

login_manager = LoginManager(redirect_to='login', secret_key='yoursecretkey')
```

The `login_manager` instance is going to be passed to **Starlette** application **state**, authentication __Backend__ and __Middleware__.


## Config

You can pass custom configuration to `LoginManager` instance to set custom `cookie` values such as:

 - COOKIE_NAME
 - COOKIE_DURATION
 - COOKIE_PATH
 - COOKIE_DOMAIN
 - COOKIE_SECURE
 - COOKIE_HTTPONLY
 - COOKIE_SAMESITE


See [Configuration](/advance/configuration) section for more information.
