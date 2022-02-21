import typing


class LoginManager:
    _user_loader: typing.Callable = None

    def set_user_loader(self, callback: typing.Callable):
        self._user_loader = callback

    @property
    def user_loader(self):
        assert self._user_loader is not None, '`user_loader` is required'
        return self._user_loader
