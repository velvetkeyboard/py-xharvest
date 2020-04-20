from xharvest.handlers.base import Handler


class SettingsHandler(Handler):

    def on_signout(self, btn):
        self.custom_signals.emit('user_signout')
        self.win.destroy()
