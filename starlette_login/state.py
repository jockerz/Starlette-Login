class AuthenticationState:
    login_required: bool = False
    skip_load_user: bool = False

    # TODO: https://swagger.io/docs/specification/authentication/
    # one of: basic, session, bearer, apikey
    default_auth_type: str

    def login_is_required(self):
        return self.login_required

    def set_login_is_required(self):
        self.login_required = True

    def __repr__(self):
        return f'<AuthenticationState: login_required={self.login_required}>'
