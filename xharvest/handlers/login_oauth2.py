from xharvest.logger import logger
from xharvest.auth import AuthenticationManager
from xharvest.handlers.base import Handler


class LoginOAuth2Handler(Handler):
    def bind_data(self):
        self.auth_man = AuthenticationManager()
        webview = self.get_widget("webkitwebviewOAuth2Authorization")
        webview.load_uri(self.auth_man.get_access_token_authorization_url())
        webview.connect("decide-policy", self.on_decide_policy)
        # settings = webview.get_settings()
        # settings.set_property("enable-developer-extras", False)
        self.get_root_widget().present()

    def bind_signals(self):
        self.auth_flow.connect("user_authenticated", self.on_user_authenticated)

    def on_user_authenticated(self, gobj):
        self.get_root_widget().destroy()

    def on_decide_policy(self, web_view, decision, decision_type):
        uri = web_view.get_uri()
        logger.debug("navigating", uri)
        if uri.startswith(self.auth_man.oauth2_redirect_domain):
            decision.ignore()
            params = uri.split("?")[1].split("&")
            params = {txt.split("=")[0]: txt.split("=")[1] for txt in params}

            access_token = params["access_token"]
            expires_in = params["expires_in"]
            scope = params["scope"]

            self.auth_man.set_oauth2_credentials(
                access_token, expires_in, scope)
            self.auth_flow.emit("user_authenticated")
            return True
        return False
