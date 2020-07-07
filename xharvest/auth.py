from datetime import datetime
from datetime import timedelta
import keyring
from harvest.credentials import PersonalAccessAuthCredential
from harvest.credentials import OAuth2Credential
from harvest.services import CurrentUser


class AuthenticationManager(object):

    OAUTH2_METHOD = "oauth2"
    PAT_METHOD = "pat"
    ALLOWED_METHODS = [
        PAT_METHOD,
    ]

    domain = "https://id.getharvest.com"
    oauth2_redirect_domain = "http://localhost:8118"

    # ----------------------------------------------------------------[Helpers]

    def set_secret(self, key, val):
        keyring.set_password("xharvest", key, val)

    def get_secret(self, key):
        return keyring.get_password("xharvest", key)

    def set_auth_method(self, method):
        if method not in self.ALLOWED_METHODS:
            raise Exception('Authentication Method Not Supported')
        self.set_secret("auth_method", method)

    # ----------------------------------------------------------------[OAuth 2]

    def set_oauth2_credentials(self, access_token, expires_in, scope):
        self.set_secret("access_token", access_token)
        self.set_secret("expires_in", expires_in)
        self.set_secret("last_request_date", datetime.now().isoformat())
        self.set_secret("scope", scope)

    def get_last_request_date(self):
        ret = self.get_secret("last_request_date")
        if ret:
            ret = datetime.strptime(ret, "%Y-%m-%dT%H:%M:%S.%f")
        return ret

    def get_access_token_authorization_url(self):
        return "{}/{}?client_id={}&response_type=token".format(
                "oauth2/authorize",
                self.domain,
                self.get_secret("client_id"),
            )

    # --------------------------------------------------[Personal Access Token]

    def set_pat_credentials(self, account_id, token):
        self.set_secret("pat", token)
        self.set_secret("account_id", account_id)

    # -------------------------------------------------------------------[Core]

    def is_user_authenticated(self, auth_method=None):
        auth_method = auth_method or self.get_secret("auth_method")
        if auth_method == self.PAT_METHOD:
            resp = CurrentUser(self.get_credential(auth_method)).get()
            print(resp)
            if not resp.get('error'):
                return True
        elif auth_method == self.OAUTH2_METHOD:
            if self.get_secret("access_token"):
                exp_in_sec = self.get_secret("expires_in")
                last_request_date = self.get_last_request_date()
                if exp_in_sec and last_request_date:
                    exp_delta = timedelta(seconds=int(exp_in_sec))
                    expiration_date = last_request_date + exp_delta
                    if datetime.now() < expiration_date:
                        return True

    def get_credential(self, auth_method=None):
        auth_method = auth_method or self.get_secret("auth_method")
        if auth_method == self.PAT_METHOD:
            account_id = keyring.get_password("xharvest", "account_id")
            token = keyring.get_password("xharvest", "pat")
            return PersonalAccessAuthCredential(
                    account_id=account_id, token=token)
        elif auth_method == self.OAUTH2_METHOD:
            access_token = self.get_secret("access_token")
            scope = self.get_secret("scope")
            return OAuth2Credential(access_token, scope,)

    def wipe(self):
        # TODO Maybe set this as a attribute?
        keys = [
            "access_token",
            "client_secret",
            "last_request_date",
            "expires_in",
            "pat",
            "account_id",
            ]
        for key in keys:
            try:
                keyring.delete_password("xharvest", key)
            except keyring.errors.PasswordDeleteError:
                pass
