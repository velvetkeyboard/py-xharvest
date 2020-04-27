from datetime import datetime
from gi.repository import Gtk
from xharvest.threads import GtkThread
from xharvest.threads import gtk_thread_cb
# from xharvest.models.timesummary import TimeSummary
from xharvest.handlers.base import Handler


class LoginHandler(Handler):

    def bind_data(self):
        webview = self.get_widget("webkitwebviewOAuth2Authorization")
        webview.load_uri(self.oauth2.get_access_token_authorization_url())
        webview.connect("decide-policy", self.on_decide_policy)
        settings = webview.get_settings()
        # settings.set_property("enable-developer-extras", False)

    def bind_signals(self):
        self.oauth2.connect(
            'user_authenticated', self.on_user_authenticated)

    def on_user_authenticated(self, gobj):
        from xharvest.handlers.main2 import MainWindowHandler
        handler = MainWindowHandler()
        handler.get_root_widget().show_all()
        self.get_root_widget().destroy()

    def on_decide_policy(self, web_view, decision, decision_type):
        uri = web_view.get_uri()
        print('navigating', uri)
        if (uri.startswith(self.oauth2.redirect_domain)):
            decision.ignore()
            params = uri.split('?')[1].split('&')
            params = {txt.split('=')[0]: txt.split('=')[1] for txt in params}
            # Storing Credentials
            self.oauth2.set_access_token(params['access_token'])
            self.oauth2.set_expiration(params['expires_in'])
            self.oauth2.set_last_request_date(datetime.now().isoformat())
            self.oauth2.set_scope(params['scope'])
            self.user.oauth2 = self.oauth2.get_credential()
            self.assignments.oauth2 = self.oauth2.get_credential()
            self.time_entries.oauth2 = self.oauth2.get_credential()
            self.oauth2.emit('user_authenticated')
            # self.get_root_widget().destroy()
            return True
        return False

    def on_quit(self, *args):
        Gtk.main_quit()