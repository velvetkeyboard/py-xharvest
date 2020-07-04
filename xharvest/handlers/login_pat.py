from xharvest.auth import AuthenticationManager
from xharvest.handlers.base import Handler


class LoginPersonalAccessTokenHandler(Handler):
    def bind_data(self):
        self.get_widget('linkButtonHarvestDevelopersPage')\
            .set_label('Create Personal Token')

    def bind_signals(self):
        self.auth_flow.connect(
            "user_authenticated", self.on_user_authenticated)

    def on_user_authenticated(self, gobj):
        self.get_root_widget().destroy()

    def on_validate_pat(self, btn):
        token = self.get_widget('entryToken').get_text()
        account_id = self.get_widget('entryAccountId').get_text()
        auth_man = AuthenticationManager()
        auth_man.set_pat_credentials(account_id=account_id, token=token)
        auth_man.set_auth_method("pat")
        self.auth_flow.emit("user_authenticated")
