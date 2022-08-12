from starlette_login.mixins import AnonymousUser, UserMixin


class TestUserMixinTest:
    def test_anonymous_user(self):
        anon = AnonymousUser()

        assert anon.is_authenticated is False
        assert anon.display_name == ""
        assert anon.identity is None

    def test_user(self):
        user = UserMixin()

        assert user.is_authenticated is True
