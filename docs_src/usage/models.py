from starlette_login.mixins import UserMixin


class User(UserMixin):
    user_id: int
    name: str

    def identity(self) -> int:
        return self.user_id

    def display_name(self):
        return self.name
