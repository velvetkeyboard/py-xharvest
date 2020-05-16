from xharvest.handlers.base import Handler
from xharvest.handlers.general_preferences import GeneralPreferencesHandler
from xharvest.handlers.shortcuts_preferences import ShortcutsPreferencesHandler


class PreferencesHandler(Handler):

    def bind_data(self):
        handler = GeneralPreferencesHandler()
        handler.get_root_widget().show_all()
        self.vp_general = self.get_widget('viewport_general')
        self.vp_general.add(handler.get_root_widget())

        handler = ShortcutsPreferencesHandler()
        handler.get_root_widget().show_all()
        self.vp_shortcuts = self.get_widget('viewport_shortcuts')
        self.vp_shortcuts.add(handler.get_root_widget())
