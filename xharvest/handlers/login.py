from xharvest.data import get_img_path
from xharvest.handlers.base import Handler
from xharvest.handlers.login_pat import LoginPersonalAccessTokenHandler
# from xharvest.handlers.login_oauth2 import LoginOAuth2Handler


class LoginHandler(Handler):
    def bind_data(self):
        self.get_widget("imageAppLogo")\
            .set_from_file(get_img_path("xharvest.png"))

    def bind_signals(self):
        self.auth_flow.connect(
                "user_authenticated", self.on_user_authenticated)

    def on_user_authenticated(self, gobj):
        self.get_root_widget().destroy()

    def on_login_with_pat(self, btn):
        self.get_root_widget().hide()  # TODO Move to a decorator?
        LoginPersonalAccessTokenHandler().get_root_widget().show_all()

    def on_login_with_oauth2(self, btn):
        # self.get_root_widget().hide()  # TODO Move to a decorator?
        # LoginOAuth2Handler().get_root_widget().show_all()
        pass
