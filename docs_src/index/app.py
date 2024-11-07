from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Route

from starlette_login.backends import SessionAuthBackend
from starlette_login.login_manager import LoginManager
from starlette_login.middleware import AuthenticationMiddleware

from models import user_list
from routes import home_page, login_page, logout_page, protected_page


login_manager = LoginManager(redirect_to='login', secret_key='secret')
login_manager.set_user_loader(user_list.user_loader)

app = Starlette(
    middleware=[
        Middleware(SessionMiddleware, secret_key='secret'),
        Middleware(
            AuthenticationMiddleware,
            backend=SessionAuthBackend(login_manager),
            login_manager=login_manager,
            allow_websocket=False,
        )
    ],

    routes=[
        Route('/', home_page, name='home'),
        Route('/login', login_page, methods=['GET', 'POST'], name='login'),
        Route('/logout', logout_page, name='logout'),
        Route('/protected', protected_page, name='protected'),
    ],
)
app.state.login_manager = login_manager