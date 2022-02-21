from starlette.authentication import BaseUser


class UserMixin(BaseUser):
    ...


class AnonymousUser(UserMixin):
    @property
    def is_authenticated(self) -> bool:
        return False

    @property
    def display_name(self) -> str:
        return ""

    @property
    def identity(self):
        return
