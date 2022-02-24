class AuthenticationState:
    _login_required: bool = False
    skip_load_user: bool = False

    def login_required(self):
        return self.login_required

    def set_login_is_required(self):
        self._login_required = True

    def set_skip_load_user(self):
        self.skip_load_user = True
