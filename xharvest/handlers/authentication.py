from datetime import datetime
from xharvest.handlers.base import Handler


class AuthHandler(Handler):

    def on_decide_policy(self, web_view, decision, decision_type):
        uri = web_view.get_uri()
        print('navigating', uri)
        if (uri.startswith(self.oauth2_mng.redirect_domain)):
            decision.ignore()
            params = uri.split('?')[1].split('&')
            params = {txt.split('=')[0]: txt.split('=')[1] for txt in params}
            # Storing Credentials
            self.oauth2_mng.set_access_token(params['access_token'])
            self.oauth2_mng.set_expiration(params['expires_in'])
            self.oauth2_mng.set_last_request_date(datetime.now().isoformat())
            self.oauth2_mng.set_scope(params['scope'])
            self.custom_signals.emit('user_authenticated')
            self.builder.get_object(
                    'windowHarvestOAuth2Authorization').destroy()
            return True
        return False

