from starlette_login.login_manager import LoginManager


from .model import user_list

login_manager = LoginManager(redirect_to='login', secret_key='secret')
login_manager.set_user_loader(user_list.user_loader)
