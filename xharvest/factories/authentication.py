from xharvest.factories.base import Factory


class AuthFactory(Factory):
    widget_ids = ('windowHarvestOAuth2Authorization',)
    root_widget_name = 'windowHarvestOAuth2Authorization'

    def bind(self):
        webview = self.builder.get_object("webkitwebviewOAuth2Authorization")
        webview.load_uri(self.data.get_access_token_authorization_url())
        webview.connect("decide-policy", self.handler.on_decide_policy)
        settings = webview.get_settings()
        settings.set_property("enable-developer-extras", True)

