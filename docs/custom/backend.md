# Authentication Backend

## `SessionAuthBackend`

`SessionAuthbackend` is where the HTTP session being evaluated 
to distinct between authenticated and non-authenticated user.
This `SessionAuthBackend` instance will be used as authentication middleware property, 
which will process every HTTP request.



## Usage Example

```py
from starlette_login.backends import SessionAuthBackend
from starlette_login.login_manager import LoginManager

login_manager = LoginManager(redirect_to='/login', secret_key='SECRET_KEY')
sess_auth_backend = SessionAuthBackend(login_manager)
```