from starlette_login.login_manager import Config, LoginManager, ProtectionLevel

from .model import user_list

login_manager = LoginManager(redirect_to="login", secret_key="secret")
login_manager.set_user_loader(user_list.user_loader)

config = Config(protection_level=ProtectionLevel.Strong)
x_login_manager = LoginManager(
    redirect_to="login", secret_key="secret", config=config
)
x_login_manager.set_user_loader(user_list.user_loader)
