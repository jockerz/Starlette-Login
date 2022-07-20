from starlette.authentication import BaseUser


class UserMixin(BaseUser):
    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        raise NotImplementedError()  # pragma: no cover

    @property
    def identity(self) -> str:
        raise NotImplementedError()  # pragma: no cover


class AnonymousUser(BaseUser):
    @property
    def is_authenticated(self) -> bool:
        return False

    @property
    def display_name(self) -> str:
        return ""

    @property
    def identity(self):
        return
