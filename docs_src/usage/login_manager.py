from starlette_login.login_manager import LoginManager

login_manager = LoginManager(redirect_to='/login_endpoint', secret_key='SECRET_KEY')