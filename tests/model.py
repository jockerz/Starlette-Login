import typing
from dataclasses import dataclass

from starlette.requests import Request

from starlette_login.mixins import BaseUser


@dataclass
class User(BaseUser):
    id: int
    username: str
    password: str = "password"
    is_admin: bool = False

    def check_password(self, password: str):
        return self.password == password

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> int:
        return self.id


class UserList:
    def __init__(self):
        self.user_list = []

    def dict_username(self) -> dict:
        d = {}
        for user in self.user_list:
            d[user.username] = user
        return d

    def dict_id(self) -> dict:
        d = {}
        for user in self.user_list:
            d[user.identity] = user
        return d

    def add(self, user: User) -> bool:
        if user.identity in self.dict_id():
            return False
        self.user_list.append(user)
        return True

    def get_by_username(self, username: str) -> typing.Optional[User]:
        return self.dict_username().get(username)

    def get_by_id(self, identifier: int) -> typing.Optional[User]:
        return self.dict_id().get(identifier)

    def user_loader(self, request: Request, user_id: int):
        if not isinstance(user_id, int):
            user_id = int(user_id)
        return self.get_by_id(user_id)

    async def async_user_loader(self, request: Request, user_id: int):
        if not isinstance(user_id, int):
            user_id = int(user_id)
        return self.get_by_id(user_id)


user_list = UserList()
user_list.add(User(id=1, username="user1", password="password"))
user_list.add(User(id=2, username="user2", password="password"))
user_list.add(User(id=3, username="admin", password="password", is_admin=True))
