# Login Manager

`LoginManager` is where we set the configuration for authentication.

Upon creating the instance, `redirect_to` property must be provided.
This property is url name of __redirect route__ that authentication is 
required error redirected to.
The `redirect_to` value must be resolvable by `Request.url_for` method.

```python
from starlette_login.login_manager import LoginManager

login_manager = LoginManager(redirect_to='login')
```

The `login_manager` instance is going to be passed to authentication __Backend__ and __Middleware__.
