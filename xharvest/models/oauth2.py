from datetime import datetime
from datetime import timedelta
import urllib.parse
import keyring
from gi.repository import GObject
from harvest.credentials import OAuth2Credential


class OAuth2CredentialManager(GObject.GObject):

    __gsignals__ = {
        'user_authenticated': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    domain = 'https://id.getharvest.com'
    redirect_domain = 'http://localhost:8118'

    def get_credential(self):
        access_token = keyring.get_password("xharvest", "access_token")
        scope = keyring.get_password("xharvest", "scope")
        return OAuth2Credential(
                access_token,
                scope,
                )

    def set_access_token(self, access_token):
        keyring.set_password("xharvest", "access_token", access_token)

    def set_scope(self, scope):
        scope = urllib.parse.unquote(scope)
        scope = scope.split(':')[1].strip()
        keyring.set_password("xharvest", "scope", scope)

    def set_refresh_token(self, refresh_token):
        keyring.set_password("xharvest", "refresh_token", refresh_token)

    def set_expiration(self, expires_in):
        keyring.set_password("xharvest", "expires_in", expires_in)

    def set_last_request_date(self, date_str):
        keyring.set_password("xharvest", "last_request_date", date_str)

    def get_client_id(self):
        return keyring.get_password("xharvest", "client_id")

    def get_client_secret(self):
        return keyring.get_password("xharvest", "client_secret")

    def get_access_token(self):
        return keyring.get_password("xharvest", "access_token")

    def get_last_request_date(self):
        ret = keyring.get_password("xharvest", "last_request_date")
        if ret:
            ret = datetime.strptime(ret, "%Y-%m-%dT%H:%M:%S.%f")
        return ret

    def get_expiration_in_secs(self):
        return keyring.get_password("xharvest", "expires_in")

    def get_access_token_authorization_url(self):
        return '{}/oauth2/authorize?client_id={}&response_type=token'.format(
            self.domain,
            self.get_client_id())

    def is_access_token_expired(self):
        if keyring.get_password("xharvest", "access_token"):
            exp_in_sec = self.get_expiration_in_secs()
            last_request_date = self.get_last_request_date()
            if exp_in_sec and last_request_date:
                exp_delta = timedelta(seconds=int(exp_in_sec))
                expiration_date = last_request_date + exp_delta
                if datetime.now() < expiration_date:
                    return False

        return True

    def wipe(self):
        keyring.delete_password('xharvest', 'access_token')
        keyring.delete_password('xharvest', 'client_secret')
        keyring.delete_password('xharvest', 'last_request_date')
        keyring.delete_password("xharvest", "expires_in")

