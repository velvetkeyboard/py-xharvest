from xharvest.handlers.base import Handler
from xharvest.handlers.shortcut_entry import ShortcutEntryHandler
# from xharvest.models.preferences import Shortcuts


class ShortcutsPreferencesHandler(Handler):

    def bind_data(self):
        cfg = self.preferences.get_config()
        shortcuts = cfg['shortcuts']
        # Recovering Widgets
        # self.label_start_new_timer = self.get_widget('label_start_new_timer')
        # self.label_show_today_entries = self.get_widget(
        #        'label_show_today_entries')
        # self.label_show_time_summary = self.get_widget(
        #        'label_show_time_summary')

        # Binding actual data
        # self.label_start_new_timer.set_label(
        #        f'{shortcuts["mod_key"]} + \
        #        {shortcuts["new_time_entry"]}')
        # self.label_show_today_entries.set_label(
        #        f'{shortcuts["mod_key"]} + \
        #        {shortcuts[Shortcuts.SHOW_TODAYS_ENTRIES]}')
        # self.label_show_time_summary.set_label(
        #        f'{shortcuts["mod_key"]} + \
        #        {shortcuts[Shortcuts.SHOW_TIME_ENTRY_FORM]}')
        self.box_shortcuts = self.get_widget('box_shortcuts')
        for k, v in shortcuts.items():
            hander = ShortcutEntryHandler(k, v)
            self.box_shortcuts.add(hander.get_root_widget())
